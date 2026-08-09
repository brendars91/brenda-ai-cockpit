"""
Engine Service
Executes compiled agents and provides telemetry streaming.
"""
import time
import uuid
import json
import asyncio
import random
import sys
from pathlib import Path
from typing import Dict, AsyncGenerator, Optional

class EngineService:
    def __init__(self):
        self.executions_dir = Path("artifacts/engine_executions")
        self.telemetry_file = Path("artifacts/telemetry/history.jsonl")
        self.agents_dir = Path("artifacts/builder_agents")
        self.executions_dir.mkdir(parents=True, exist_ok=True)
        self.telemetry_file.parent.mkdir(parents=True, exist_ok=True)
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        self.active_executions: Dict[str, Dict] = {}

    def _get_agent_data(self, agent_id: str) -> Optional[Dict]:
        """
        Get agent data directly from filesystem without BuilderService dependency.
        This avoids circular imports between Engine and Builder services.
        """
        agent_file = self.agents_dir / f"{agent_id}.json"
        if agent_file.exists():
            try:
                return json.loads(agent_file.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"[Engine] Error reading agent data: {e}")
                return None
        return None

    async def execute_agent(self, agent_id: str, task: str, stream: bool = True) -> AsyncGenerator:
        """
        Execute an agent with a given task.
        Yields streaming logs and metrics.
        """
        execution_id = str(uuid.uuid4())

        # Create execution record
        execution = {
            "execution_id": execution_id,
            "agent_id": agent_id,
            "task": task,
            "status": "running",
            "started_at": time.time(),
            "logs": [],
            "result": None
        }

        self.active_executions[execution_id] = execution

        # Execute Real Agent Script (with Self-Healing Loop)
        retries = 2
        attempt = 0

        while attempt <= retries:
            try:
                # Check if agent has a real script (without BuilderService dependency)
                agent_data = self._get_agent_data(agent_id)

                if not agent_data:
                    # Fallback to simulation if no agent data found
                    # yield self._create_log_event("⚠️ [SIMULATION MODE] No compiled agent found. Running semantic simulation.")
                    # await asyncio.sleep(1)
                    # result = self._generate_mock_result(task, agent_id)
                    raise Exception("Agent not found. Real execution required. Simulation disabled.")

                script_path = agent_data.get("script_path")
                
                if not script_path or not Path(script_path).exists():
                    # Fallback to simulation if no script found
                    # yield self._create_log_event("⚠️ [SIMULATION MODE] No compiled agent found. Running semantic simulation for resource optimization.")
                    # await asyncio.sleep(1)
                    # result = self._generate_mock_result(task, agent_id)
                    raise Exception("Agent script not found. Real execution required. Simulation disabled.")
                
                yield self._create_log_event(f"🚀 Starting Real Agent: {agent_data.get('name')} (Attempt {attempt+1})")
                
                # Run subprocess with same Python interpreter
                proc = await asyncio.create_subprocess_exec(
                    sys.executable, script_path, task,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                # Stream logs
                while True:
                    line = await proc.stdout.readline()
                    if not line:
                        break
                    line_str = line.decode().strip()
                    if line_str:
                        yield self._create_log_event(line_str)
                
                await proc.wait()
                
                if proc.returncode == 0:
                    result = f"Process finished successfully."
                    execution["status"] = "success"
                    break # Success!
                else:
                    stderr = await proc.stderr.read()
                    error_msg = stderr.decode()
                    yield self._create_log_event(f"❌ Execution Failed: {error_msg}")
                    
                    if attempt < retries:
                        yield self._create_log_event("🩹 Initiating Self-Healing Protocol...")
                        await self._heal_agent_code(script_path, error_msg, task)
                        attempt += 1
                        continue
                    else:
                        raise Exception(f"Failed after {retries} repairs: {error_msg}")

            except Exception as e:
                # If it's the last attempt, fail
                if attempt == retries:
                    yield self._create_log_event(f"Error: {str(e)}")
                    execution["status"] = "failed"
                    execution["error"] = str(e)
                    raise
                attempt += 1 # In case exception wasn't from subprocess
                
        execution["result"] = result
        execution["completed_at"] = time.time()
        yield self._create_result_event(result)
        self._save_execution(execution)

    async def _heal_agent_code(self, script_path: str, error_log: str, task: str):
        """Uses LLM to patch the broken script"""
        from timeout_config import get_timeout, OperationType

        try:
            from llm_provider import LLMProvider
            llm = LLMProvider()
            path = Path(script_path)
            code = path.read_text(encoding="utf-8")

            prompt = (
                f"The following Python script failed execution.\n"
                f"Task: {task}\n"
                f"Error: {error_log}\n"
                f"Broken Code:\n```python\n{code}\n```\n"
                f"Please fix the code. Return ONLY the full fixed Python code in a markdown block."
            )

            # Get timeout from config
            timeout = get_timeout(OperationType.ENGINE_HEAL)

            response = await llm.generate(prompt, system_prompt="You are an expert Python debugger.")

            # Extract code block
            if "```python" in response:
                fixed_code = response.split("```python")[1].split("```")[0].strip()
            elif "```" in response:
                fixed_code = response.split("```")[1].split("```")[0].strip()
            else:
                fixed_code = response

            path.write_text(fixed_code, encoding="utf-8")

        except Exception as e:
            print(f"[Engine] Heal failed: {e}")
            raise
    
    def get_telemetry(self, agent_id: str) -> Dict:
        """Get current telemetry for an agent"""
        # Real telemetry from execution history
        telemetry = {
            "cpu": 0.0,
            "memory": 0,
            "tokens": 0,
            "latency": 0,
            "executions": 0,
            "timestamp": time.time()
        }

        # Try to get real system metrics
        try:
            import psutil
            telemetry["cpu"] = psutil.cpu_percent(interval=0.1)
            telemetry["memory"] = psutil.virtual_memory().used // (1024 * 1024)  # MB
        except ImportError:
            # Fallback: use execution history if available
            telemetry["cpu"] = 0.0
            telemetry["memory"] = 0

        # Aggregate from execution history
        try:
            if self.telemetry_file.exists():
                agent_executions = []
                with open(self.telemetry_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if entry.get("agent_id") == agent_id:
                                agent_executions.append(entry)
                        except:
                            continue

                if agent_executions:
                    telemetry["executions"] = len(agent_executions)
                    # Calculate average latency from execution times
                    total_latency = 0
                    count = 0
                    for entry in agent_executions[-10:]:  # Last 10 executions
                        try:
                            exec_file = self.executions_dir / f"{entry['execution_id']}.json"
                            if exec_file.exists():
                                exec_data = json.loads(exec_file.read_text(encoding="utf-8"))
                                if "started_at" in exec_data and "completed_at" in exec_data:
                                    latency = (exec_data["completed_at"] - exec_data["started_at"]) * 1000
                                    total_latency += latency
                                    count += 1
                        except:
                            continue
                    telemetry["latency"] = int(total_latency / count) if count > 0 else 0
                    telemetry["tokens"] = len(agent_executions) * 100  # Estimated
        except:
            pass

        return telemetry
    
    def _create_log_event(self, message: str) -> Dict:
        """Create a log event"""
        return {
            "type": "log",
            "timestamp": time.strftime('%H:%M:%S'),
            "message": message
        }
    
    def _create_metric_event(self, cpu: float, memory: int, tokens: int, latency: int) -> Dict:
        """Create a metric event"""
        return {
            "type": "metric",
            "cpu": cpu,
            "memory": memory,
            "tokens": tokens,
            "latency": latency
        }
    
    def _create_result_event(self, result: str) -> Dict:
        """Create a result event"""
        return {
            "type": "result",
            "output": result,
            "status": "success"
        }
    
    
    # Mocks removed for security compliance

    
    def _save_execution(self, execution: Dict):
        """Save execution record and structured telemetry"""
        execution_file = self.executions_dir / f"{execution['execution_id']}.json"
        execution_file.write_text(json.dumps(execution, indent=2))
        
        # Append to structured history for long-term audit
        with open(self.telemetry_file, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": time.time(),
                "agent_id": execution["agent_id"],
                "execution_id": execution["execution_id"],
                "task_preview": execution["task"][:100],
                "status": execution["status"],
                "mode": "simulation" if "SIMULATION" in str(execution.get("logs", "")) else "real"
            }) + "\n")
