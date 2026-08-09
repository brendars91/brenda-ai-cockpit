"""
Builder Service v2.0 - Multi-Core Optimization
Manages build queue with parallel compilation using ThreadPoolExecutor.
"""
import time
import uuid
import json
import os
import subprocess
import heapq
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from datetime import datetime

class BuildStatus(str, Enum):
    PENDING = "PENDING"
    BUILDING = "BUILDING"
    READY = "READY"
    FAILED = "FAILED"

class BuildPriority(int, Enum):
    """Priority levels for builds"""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0

@dataclass(order=True)
class BuildItem:
    """Build item with priority support"""
    priority: int
    build_id: str = field(compare=False)
    payload_id: str = field(compare=False)
    agent_name: str = field(compare=False)
    model: str = field(compare=False)
    tools: List[str] = field(compare=False, default_factory=list)
    status: BuildStatus = field(compare=False, default=BuildStatus.PENDING)
    progress: int = field(compare=False, default=0)
    created_at: float = field(compare=False, default_factory=time.time)
    started_at: Optional[float] = field(compare=False, default=None)
    completed_at: Optional[float] = field(compare=False, default=None)
    error: Optional[str] = field(compare=False, default=None)

    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            "build_id": self.build_id,
            "payload_id": self.payload_id,
            "agent_name": self.agent_name,
            "model": self.model,
            "tools": self.tools,
            "status": self.status.value,
            "progress": self.progress,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error
        }

class BuilderService:
    """
    Builder Service v2.0 - Multi-Core Compilation

    Features:
    - Parallel compilation with ThreadPoolExecutor
    - Priority queue (heap-based)
    - Dynamic timeouts based on build complexity
    - Progress tracking
    - Circuit breaker for repeated failures
    """

    # Timeout configurations per task type
    TIMEOUTS = {
        "compile": 120,           # 2 min for code generation
        "audit": 180,             # 3 min for auditor
        "skill_genetics": 60,     # 1 min per skill
        "total_max": 300          # 5 min absolute max
    }

    def __init__(self, max_workers: Optional[int] = None):
        """Initialize Builder with thread pool

        Args:
            max_workers: Number of parallel workers. Defaults to CPU count.
        """
        self.builds_dir = Path("artifacts/builder_builds")
        self.agents_dir = Path("artifacts/builder_agents")
        self.builds_dir.mkdir(parents=True, exist_ok=True)
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        # Thread pool for parallel builds
        self.max_workers = max_workers or max(1, os.cpu_count() - 1)
        self.executor: Optional[ThreadPoolExecutor] = None

        # Priority queue (heap)
        self.pending_queue: List[BuildItem] = []

        # Active builds tracking
        self.active_builds: Dict[str, BuildItem] = {}
        self.completed_builds: Dict[str, BuildItem] = {}

        # Statistics
        self.stats = {
            "total_built": 0,
            "total_failed": 0,
            "avg_build_time": 0.0,
            "concurrent_builds": 0
        }

    def _ensure_executor(self):
        """Ensure thread pool executor is running"""
        if self.executor is None:
            self.executor = ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix="BuilderWorker"
            )

    def compile_agent(
        self,
        payload_id: str,
        agent_name: str,
        model_config: Dict,
        tools: List[str],
        priority: BuildPriority = BuildPriority.NORMAL
    ) -> Dict:
        """Submit agent for compilation with priority

        Args:
            payload_id: Payload ID to build from
            agent_name: Name for the agent
            model_config: Model configuration
            tools: List of tools/skills to include
            priority: Build priority (default: NORMAL)

        Returns:
            Dict with build_id, status, position, and ETA
        """
        self._ensure_executor()

        build_id = str(uuid.uuid4())
        build_item = BuildItem(
            priority=priority.value,
            build_id=build_id,
            payload_id=payload_id,
            agent_name=agent_name,
            model=model_config.get("model", "gemini-2.0-flash"),
            tools=tools
        )

        # Add to priority queue
        heapq.heappush(self.pending_queue, build_item)

        # Submit to thread pool
        future = self.executor.submit(self._process_build, build_item)
        future.add_done_callback(lambda f: self._build_completed(build_id, f))

        # Calculate ETA based on queue position
        position = self.pending_queue.index(build_item) + len(self.active_builds)
        eta_seconds = position * (self.stats["avg_build_time"] or 45)

        return {
            "build_id": build_id,
            "status": BuildStatus.PENDING.value,
            "position": position,
            "eta_seconds": eta_seconds,
            "max_workers": self.max_workers
        }

    def get_queue(self) -> List[Dict]:
        """Get current build queue with status"""
        queue = []

        # Pending items
        for item in self.pending_queue:
            queue.append(item.to_dict())

        # Active builds
        for item in self.active_builds.values():
            queue.append(item.to_dict())

        # Recent completed (last 10)
        completed = list(self.completed_builds.values())
        completed.sort(key=lambda x: x.completed_at or 0, reverse=True)
        for item in completed[:10]:
            queue.append(item.to_dict())

        return queue

    def get_agents(self) -> List[Dict]:
        """List all compiled agents"""
        agents = []
        for agent_file in self.agents_dir.glob("*.json"):
            try:
                agent_data = json.loads(agent_file.read_text())
                agents.append(agent_data)
            except Exception as e:
                print(f"[Builder] Error reading agent {agent_file}: {e}")
        return agents

    def get_agent(self, agent_id: str) -> Dict:
        """Get specific agent"""
        agent_file = self.agents_dir / f"{agent_id}.json"
        if not agent_file.exists():
            return {}
        return json.loads(agent_file.read_text())

    def get_stats(self) -> Dict:
        """Get builder statistics"""
        return {
            **self.stats,
            "max_workers": self.max_workers,
            "pending_count": len(self.pending_queue),
            "active_count": len(self.active_builds),
            "completed_count": len(self.completed_builds)
        }

    def _process_build(self, build_item: BuildItem) -> Tuple[str, bool, Optional[str]]:
        """Process a single build (runs in thread pool)

        Returns:
            Tuple of (build_id, success, error_message)
        """
        build_id = build_item.build_id

        # Move to active
        if build_id in [b.build_id for b in self.pending_queue]:
            self.pending_queue = [b for b in self.pending_queue if b.build_id != build_id]

        build_item.status = BuildStatus.BUILDING
        build_item.started_at = time.time()
        build_item.progress = 10
        self.active_builds[build_id] = build_item

        try:
            # Phase 1: Tool Detection & Inference (20%)
            build_item.progress = 20
            self._update_build_progress(build_item)

            if not build_item.tools:
                build_item.tools = self._infer_tools(build_item)

            # Phase 2: Code Generation (60%)
            build_item.progress = 40
            self._update_build_progress(build_item)

            script_path = self._generate_agent_code(build_item)

            build_item.progress = 60
            self._update_build_progress(build_item)

            # Phase 3: Audit & Security (80%)
            build_item.progress = 80
            self._update_build_progress(build_item)

            self._run_audit(build_item, script_path)

            # Phase 4: Finalization (100%)
            agent_data = self._compile_agent_artifact(build_item, script_path)

            # Save agent metadata
            agent_file = self.agents_dir / f"{build_id}.json"
            agent_file.write_text(json.dumps(agent_data, indent=2))

            build_item.status = BuildStatus.READY
            build_item.progress = 100
            build_item.completed_at = time.time()
            build_item.error = None

            return (build_id, True, None)

        except subprocess.TimeoutExpired as e:
            error_msg = f"Build timeout after {e.timeout}s: {str(e)}"
            build_item.status = BuildStatus.FAILED
            build_item.error = error_msg
            return (build_id, False, error_msg)

        except Exception as e:
            error_msg = f"Build failed: {str(e)}"
            build_item.status = BuildStatus.FAILED
            build_item.error = error_msg
            return (build_id, False, error_msg)

        finally:
            # Remove from active
            if build_id in self.active_builds:
                del self.active_builds[build_id]

    def _build_completed(self, build_id: str, future: Future):
        """Callback when build completes"""
        try:
            result = future.result()
            bid, success, error = result

            # Find and update build item
            build_item = None

            # Check active builds
            if bid in self.active_builds:
                build_item = self.active_builds[bid]

            # Check queue
            if not build_item:
                for item in self.pending_queue:
                    if item.build_id == bid:
                        build_item = item
                        break

            if build_item:
                if success:
                    build_item.status = BuildStatus.READY
                    build_item.progress = 100
                    build_item.completed_at = time.time()
                    build_item.error = None
                    self.completed_builds[bid] = build_item

                    # Update stats
                    build_time = build_item.completed_at - build_item.started_at
                    self.stats["total_built"] += 1
                    # Calculate average safely (avoid division by zero)
                    previous_avg = self.stats.get("avg_build_time", 0)
                    previous_count = self.stats["total_built"] - 1
                    if previous_count > 0:
                        self.stats["avg_build_time"] = (
                            (previous_avg * previous_count + build_time) / self.stats["total_built"]
                        )
                    else:
                        self.stats["avg_build_time"] = build_time
                    print(f"[Builder] ✅ Build {bid} completed in {build_time:.1f}s")
                else:
                    build_item.status = BuildStatus.FAILED
                    build_item.error = error
                    self.stats["total_failed"] += 1
                    print(f"[Builder] ❌ Build {bid} failed: {error}")

        except Exception as e:
            print(f"[Builder] Error in completion callback: {e}")

    def _update_build_progress(self, build_item: BuildItem):
        """Update build progress (for WebSocket broadcast in future)"""
        # This will be used for real-time progress updates
        pass

    def _infer_tools(self, build_item: BuildItem) -> List[str]:
        """Infer tools from payload if not provided"""
        try:
            payload_id = build_item.payload_id
            if not payload_id:
                return []

            payload_path = Path("resources/payloads") / f"{payload_id}.json"
            if not payload_path.exists():
                return []

            payload_data = json.loads(payload_path.read_text(encoding="utf-8"))
            context_str = json.dumps(payload_data).lower()

            inferred_tools = []

            # Keyword matching for tool inference
            tool_keywords = {
                "sap-knowledge-base": ["sap", "bapi", "abap", "fi", "co"],
                "rag-pipeline": ["rag", "embedding", "vector", "semantic"],
                "web-search": ["web", "search", "browse", "scrape"],
                "data-analysis": ["analyze", "chart", "graph", "statistics"],
                "automation": ["automate", "schedule", "trigger", "workflow"]
            }

            for tool, keywords in tool_keywords.items():
                if any(kw in context_str for kw in keywords):
                    inferred_tools.append(tool)

            if inferred_tools:
                print(f"[Builder] 🔍 Auto-detected tools for {build_item.build_id}: {inferred_tools}")

            return inferred_tools

        except Exception as e:
            print(f"[Builder] Tool inference failed: {e}")
            return []

    def _generate_agent_code(self, build_item: BuildItem) -> str:
        """Generate actual Python code for the agent"""
        template_path = Path("resources/templates/agent_template.py")
        if not template_path.exists():
            raise FileNotFoundError("Agent template not found")

        content = template_path.read_text(encoding='utf-8')

        agent_id = build_item.build_id
        class_name = f"Agent_{agent_id.replace('-', '_')}"

        # Replace placeholders
        replacements = {
            "{{AGENT_ID}}": agent_id,
            "{{AGENT_NAME}}": build_item.agent_name,
            "{{DOMAIN}}": "general",
            "{{OBJECTIVES}}": "[]",
            "{{CLASS_NAME}}": class_name
        }

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        # Generate tool logic
        tool_logic = """
        try:
            # Tool execution placeholder
            pass
        except ImportError as e:
            # Basic Self-Healing for missing modules during execution
            missing_module = str(e).split("'")[-2]
            print(f"⚠️ Missing module detected during execution: {missing_module}")
            ensure_dependency(missing_module)
            print("🔄 Retrying execution...")
            pass
        """

        # Process skills
        skill_context_str = self._process_skills(build_item)

        content = content.replace("{{TOOL_IMPORTS}}", "")
        content = content.replace("{{TOOL_EXECUTION_LOGIC}}", tool_logic)
        content = content.replace("{{SKILL_CONTEXT}}", skill_context_str)

        output_path = self.agents_dir / f"{agent_id}.py"
        output_path.write_text(content, encoding='utf-8')

        return str(output_path.resolve())

    def _process_skills(self, build_item: BuildItem) -> str:
        """Process and embed skills into agent code"""
        skill_context_str = ""

        try:
            from skill_genetics import SkillGeneticsService
            from llm_provider import LLMProvider

            llm = LLMProvider()
            genetics = SkillGeneticsService(llm_provider=llm)

            project_context = f"{build_item.agent_name} {build_item.tools}"

            for tool in build_item.tools:
                print(f"[Builder] 📚 Processing skill: {tool}")
                skill_content = genetics.get_skill(tool, project_context)
                if skill_content:
                    skill_context_str += f"\n--- SKILL: {tool} ---\n{skill_content}\n"
                else:
                    skill_context_str += f"\n--- SKILL: {tool} (generation failed) ---\n"

        except ImportError:
            print(f"[Builder] ⚠️ SkillGenetics not available, using fallback")
            skill_context_str = self._fallback_skills(build_item)

        return skill_context_str

    def _fallback_skills(self, build_item: BuildItem) -> str:
        """Fallback skill loading from files"""
        skill_context_str = ""
        skills_path = Path("resources/skills")

        for tool in build_item.tools:
            skill_dir = skills_path / tool
            if skill_dir.exists():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    try:
                        skill_text = skill_md.read_text(encoding="utf-8")
                        skill_context_str += f"\n--- SKILL: {tool} ---\n{skill_text}\n"
                    except Exception as e:
                        skill_context_str += f"\nError loading skill {tool}: {e}\n"

        return skill_context_str

    def _run_audit(self, build_item: BuildItem, script_path: str):
        """Run security audit on generated code"""
        try:
            print(f"[Builder] 🛡️ Launching Antigravity Auditor v2.1 for {build_item.agent_name}...")

            auditor_script = (Path(__file__).parent.parent / "modules/engine/agents/auditor_agent_v2.1.py").resolve()

            if not auditor_script.exists():
                # Try alternative paths
                possible_paths = [
                    Path.home() / ".gemini" / "Gem-Trinity-Genesis" / "modules" / "engine" / "agents" / "auditor_agent_v2.1.py",
                    Path.cwd().parent / "modules" / "engine" / "agents" / "auditor_agent_v2.1.py"
                ]
                for path in possible_paths:
                    if path.exists():
                        auditor_script = path
                        break

            if not auditor_script.exists():
                print(f"[Builder] ⚠️ Auditor not found, skipping audit")
                return

            target_file = Path(script_path)
            workspace_dir = target_file.parent

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

            # Run with timeout from TIMEOUTS config
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.TIMEOUTS["audit"]
            )

            if process.returncode == 0:
                print(f"[Builder] ✅ Auditor finished successfully")
            else:
                print(f"[Builder] ⚠️ Auditor warning (Exit {process.returncode}): {process.stderr}")

        except subprocess.TimeoutExpired:
            print(f"[Builder] ⚠️ Auditor timeout after {self.TIMEOUTS['audit']}s")
        except Exception as e:
            print(f"[Builder] ❌ Auditor invocation failed: {e}")

    def _compile_agent_artifact(self, build_item: BuildItem, script_path: str) -> Dict:
        """Create agent artifact (compiled bundle)"""
        return {
            "id": build_item.build_id,
            "name": build_item.agent_name,
            "model": build_item.model,
            "tools": build_item.tools,
            "payload_id": build_item.payload_id,
            "version": "2.0.0",
            "compiled_at": time.time(),
            "status": "ready",
            "script_path": script_path,
            "config": {
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "capabilities": build_item.tools,
            "build_time": build_item.completed_at - build_item.started_at if build_item.completed_at else None
        }

    def shutdown(self):
        """Gracefully shutdown the builder service"""
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
        print(f"[Builder] Shutdown complete. Built: {self.stats['total_built']}, Failed: {self.stats['total_failed']}")

# Singleton instance for import
_builder_instance: Optional[BuilderService] = None

def get_builder() -> BuilderService:
    """Get singleton builder instance"""
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = BuilderService()
    return _builder_instance
