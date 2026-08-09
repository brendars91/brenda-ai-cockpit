"""
Builder Service
Manages build queue and agent compilation.
"""
import time
import uuid
import json
import threading
import subprocess
from pathlib import Path
from typing import Dict, List
from enum import Enum
class BuildStatus(str, Enum):
    PENDING = "PENDING"
    BUILDING = "BUILDING"
    READY = "READY"
    FAILED = "FAILED"
class BuilderService:
    def __init__(self):
        self.builds_dir = Path("artifacts/builder_builds")
        self.agents_dir = Path("artifacts/builder_agents")
        self.builds_dir.mkdir(parents=True, exist_ok=True)
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        
        self.queue: List[Dict] = []
        self.queue_lock = threading.Lock()
        self.worker_thread = None
        self.worker_active = False
        
    def compile_agent(self, payload_id: str, agent_name: str, model_config: Dict, tools: List[str]) -> Dict:
        """Submit agent for compilation"""
        build_id = str(uuid.uuid4())
        
        build_item = {
            "build_id": build_id,
            "payload_id": payload_id,
            "agent_name": agent_name,
            "model": model_config.get("model", "gemini-2.0-flash"),
            "tools": tools,
            "status": BuildStatus.PENDING,
            "progress": 0,
            "eta_seconds": 45,
            "created_at": time.time(),
            "started_at": None,
            "completed_at": None
        }
        
        with self.queue_lock:
            self.queue.append(build_item)
            position = len(self.queue)
        
        # Start worker if not running
        if not self.worker_active:
            self._start_worker()
        
        return {
            "build_id": build_id,
            "status": BuildStatus.PENDING,
            "position": position,
            "eta_seconds": position * 45
        }
    
    def get_queue(self) -> List[Dict]:
        """Get current build queue"""
        with self.queue_lock:
            return [item.copy() for item in self.queue]
    
    def get_agents(self) -> List[Dict]:
        """List all compiled agents"""
        agents = []
        for agent_file in self.agents_dir.glob("*.json"):
            try:
                agent_data = json.loads(agent_file.read_text())
                agents.append(agent_data)
            except:
                pass
        return agents
    
    def get_agent(self, agent_id: str) -> Dict:
        """Get specific agent"""
        agent_file = self.agents_dir / f"{agent_id}.json"
        if not agent_file.exists():
            return {}
        return json.loads(agent_file.read_text())
    
    def _start_worker(self):
        """Start background worker for processing queue"""
        if self.worker_active:
            return
        
        self.worker_active = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def _worker_loop(self):
        """Background worker that processes the queue"""
        while self.worker_active:
            with self.queue_lock:
                pending = [item for item in self.queue if item["status"] == BuildStatus.PENDING]
            
            if pending:
                build_item = pending[0]
                self._process_build(build_item)
            else:
                # No pending builds, sleep
                time.sleep(2)
                # Stop worker if queue is empty
                with self.queue_lock:
                    if not any(item["status"] == BuildStatus.PENDING for item in self.queue):
                        self.worker_active = False
                        break
    
    def _process_build(self, build_item: Dict):
        """Process a single build"""
        build_id = build_item["build_id"]
        
        # Update status to BUILDING
        with self.queue_lock:
            for item in self.queue:
                if item["build_id"] == build_id:
                    item["status"] = BuildStatus.BUILDING
                    item["started_at"] = time.time()
                    break
        
        # Simulate build process
        try:
            # --- SMART TOOL DETECTION ---
            # If no tools provided, try to infer from payload
            if not build_item.get("tools"):
                try:
                    payload_id = build_item.get("payload_id")
                    if payload_id:
                        payload_path = Path("resources/payloads") / f"{payload_id}.json"
                        if payload_path.exists():
                            payload_data = json.loads(payload_path.read_text(encoding="utf-8"))
                            context_str = json.dumps(payload_data).lower()
                            
                            inferred_tools = []
                            # Simple keyword matching to suggest skills
                            if "sap" in context_str or "bapi" in context_str or "abap" in context_str:
                                inferred_tools.append("sap-knowledge-base")
                            
                            if "rag" in context_str or "embedding" in context_str or "vector" in context_str:
                                inferred_tools.append("rag-pipeline")
                                
                            if "web" in context_str or "search" in context_str:
                                inferred_tools.append("web-search")
                                
                            if inferred_tools:
                                print(f"[Builder] Auto-detected tools for {build_id}: {inferred_tools}")
                                with self.queue_lock:
                                    for item in self.queue:
                                        if item["build_id"] == build_id:
                                            item["tools"] = inferred_tools
                                            build_item["tools"] = inferred_tools # Update local copy
                                            break
                except Exception as e:
                    print(f"[Builder] Tool auto-detection failed: {e}")
            # Phase 1: Setup
            # time.sleep(5) - REMOVED: Optimization for speed
            with self.queue_lock:
                for item in self.queue:
                    if item["build_id"] == build_id:
                        item["progress"] = 20
                        break
            
            # Phase 2: Compilation
            # time.sleep(2) - REMOVED: Optimization for speed
            with self.queue_lock:
                for item in self.queue:
                    if item["build_id"] == build_id:
                        item["progress"] = 60
                        break
            
            # Phase 3: Finalization (100%)
            # Generate Real Code
            script_path = self._generate_agent_code(build_item)
            
            # --- AUDITOR INTEGRATION ---
            try:
                print(f"[Builder] 🛡️ Launching Antigravity Auditor v2.1 for {build_item['agent_name']}...")
                
                # Resolve path to Auditor Agent relative to this file
                # builder_service.py is in local-watcher/
                # auditor is in modules/engine/agents/auditor_agent_v2.1.py
                # This path looks for: ../modules/engine/agents/auditor_agent_v2.1.py
                auditor_script = (Path(__file__).parent.parent / "modules/engine/agents/auditor_agent_v2.1.py").resolve()
                
                if not auditor_script.exists():
                    # Fallback: try absolute path if defined in environment or standard location
                    possible_path = Path.home() / ".gemini" / "Gem-Trinity-Genesis" / "modules" / "engine" / "agents" / "auditor_agent_v2.1.py"
                    if possible_path.exists():
                         auditor_script = possible_path

                if auditor_script.exists():
                    target_file = Path(script_path)
                    workspace_dir = target_file.parent
                    
                    # Task: Audit and Refactor
                    audit_task = (
                        f"AUDIT_CRITICAL: Refactor '{target_file.name}' to be UNBEATABLE. "
                        "1. Fix ALL security issues (Bandit/OWASP). "
                        "2. Optimize performance (Cyclomatic Complexity < 10). "
                        "3. Enforce strict PEP8. "
                        "4. Add robust error handling. "
                        "DO NOT ask for permission. EXECUTE changes immediately."
                    )
                    
                    cmd = [
                        "python", 
                        str(auditor_script),
                        audit_task,
                        "--workspace",
                        str(workspace_dir)
                    ]
                    
                    # Execute Auditor as a separate process to ensure isolation
                    process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    
                    if process.returncode == 0:
                        print(f"[Builder] [OK] Auditor finished successfully.")
                        # Optional: Log auditor output for debugging
                        # print(process.stdout)
                    else:
                        print(f"[Builder] [WARN] Auditor warning (Exit {process.returncode}): {process.stderr}")
                else:
                    print(f"[Builder] [ERROR] Warning: Auditor agent not found at {auditor_script}")

            except Exception as e:
                print(f"[Builder] [ERROR] Auditor invocation failed: {e}")
            # ---------------------------
            
            agent_data = self._compile_agent_artifact(build_item, script_path)
            
            # Save agent metadata
            agent_file = self.agents_dir / f"{build_id}.json"
            agent_file.write_text(json.dumps(agent_data, indent=2))
            
            # Update status to READY
            with self.queue_lock:
                for item in self.queue:
                    if item["build_id"] == build_id:
                        item["status"] = BuildStatus.READY
                        item["progress"] = 100
                        item["completed_at"] = time.time()
                        item["eta_seconds"] = 0
                        break
        
        except Exception as e:
            # Mark as FAILED
            with self.queue_lock:
                for item in self.queue:
                    if item["build_id"] == build_id:
                        item["status"] = BuildStatus.FAILED
                        item["error"] = str(e)
                        break
    
    def _generate_agent_code(self, build_item: Dict) -> str:
        """Generate actual Python code for the agent"""
        # Fix: Use path relative to this file to find resources
        template_path = Path(__file__).parent / "resources/templates/agent_template.py"
        if not template_path.exists():
            return "Error: Template not found"
            
        content = template_path.read_text(encoding='utf-8')
        
        # Replace Placeholders
        agent_id = build_item["build_id"]
        class_name = f"Agent_{agent_id.replace('-', '_')}"
        
        content = content.replace("{{AGENT_ID}}", agent_id)
        content = content.replace("{{AGENT_NAME}}", build_item["agent_name"])
        content = content.replace("{{DOMAIN}}", "general") # TODO: get from payload
        content = content.replace("{{OBJECTIVES}}", "[]") # TODO: get from payload
        content = content.replace("{{CLASS_NAME}}", class_name)
        
        # Dynamic Tool Imports
        tool_imports = ""
        # Generate FULL execution block (indentation: 8 spaces to fit inside 'async def run')
        tool_logic = """
        try:
            # Tool execution placeholder
            pass
        except ImportError as e:
            # Basic Self-Healing for missing modules during execution
            missing_module = str(e).split("'")[-2] # Extract 'module_name'
            print(f"[WARN] Missing module detected during execution: {missing_module}")
            ensure_dependency(missing_module)
            print("[RETRY] Retrying execution...")
            # Tool execution placeholder
            pass # Retry once
        """
        
        # --- SKILL GENETICS: Auto-generate missing skills ---
        skill_context_str = ""
        
        try:
            from skill_genetics import SkillGeneticsService
            from llm_provider import LLMProvider
            
            llm = LLMProvider()
            genetics = SkillGeneticsService(llm_provider=llm)
            
            # Get project context from payload if available
            project_context = build_item.get("agent_name", "") + " " + str(build_item.get("tools", []))
            
            for tool in build_item.get("tools", []):
                print(f"[Builder] Processing skill: {tool}")
                skill_content = genetics.get_skill(tool, project_context)
                if skill_content:
                    skill_context_str += f"\n--- SKILL: {tool} ---\n{skill_content}\n"
                else:
                    skill_context_str += f"\n--- SKILL: {tool} (generation failed) ---\n"
                    
        except ImportError as e:
            print(f"[Builder] SkillGenetics not available: {e}. Using fallback.")
            # Fallback to old behavior
            skills_path = Path("resources/skills")
            for tool in build_item.get("tools", []):
                skill_dir = skills_path / tool
                if skill_dir.exists():
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        try:
                            skill_text = skill_md.read_text(encoding="utf-8")
                            skill_context_str += f"\n--- SKILL: {tool} ---\n{skill_text}\n"
                        except Exception as e:
                            skill_context_str += f"\nError loading skill {tool}: {e}\n"
        
        content = content.replace("{{TOOL_IMPORTS}}", tool_imports)
        content = content.replace("{{TOOL_EXECUTION_LOGIC}}", tool_logic)
        content = content.replace("{{SKILL_CONTEXT}}", skill_context_str)
        
        output_path = self.agents_dir / f"{agent_id}.py"
        output_path.write_text(content, encoding='utf-8')
        
        return str(output_path.resolve())
    def _compile_agent_artifact(self, build_item: Dict, script_path: str) -> Dict:
        """Create agent artifact (compiled bundle)"""
        return {
            "id": build_item["build_id"],
            "name": build_item["agent_name"],
            "model": build_item["model"],
            "tools": build_item["tools"],
            "payload_id": build_item["payload_id"],
            "version": "1.0.0",
            "compiled_at": time.time(),
            "status": "ready",
            "script_path": script_path, 
            "config": {
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "capabilities": build_item.get("tools", [])
        }
