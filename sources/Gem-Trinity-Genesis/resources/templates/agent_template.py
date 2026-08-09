import os
import sys
import json
import asyncio
from typing import Dict, Any
from pathlib import Path

# Fix imports to allow finding local-watcher modules
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root / "local-watcher"))
sys.path.append(str(project_root)) # Also add root for resources

# --- Agent Configuration ---
AGENT_ID = "{{AGENT_ID}}"
AGENT_NAME = "{{AGENT_NAME}}"
DOMAIN = "{{DOMAIN}}"
OBJECTIVES = {{OBJECTIVES}}

# --- Skill Context (Injected) ---
SKILL_CONTEXT = """
{{SKILL_CONTEXT}}
"""

# --- Tool Imports (Dynamic) ---
{{TOOL_IMPORTS}}

# --- LLM Provider ---
try:
    from llm_provider import LLMProvider
except ImportError:
    # Fallback/Mock if running standalone without correct path
    class LLMProvider:
        async def generate(self, prompt, system_prompt=""):
            return f"[Mock Standalone] {prompt[:50]}..."

class {{CLASS_NAME}}:
    def __init__(self):
        self.llm = LLMProvider()
        self.context = {}
        
    async def run(self, task: str):
        print(f"[Agent] {AGENT_NAME} starting task: {task}")
        
        # 1. Understand Task
        prompt_text = (
            f"Task: {task}\n"
            f"Context: {self.context}\n"
            f"Objectives: {OBJECTIVES}\n"
            f"Available Skills & Instructions:\n{SKILL_CONTEXT}\n"
            f"Create a step-by-step execution plan using available tools."
            f"\n\nCRITICAL INSTRUCTION: DO NOT attempt to import skills as Python modules (e.g. 'from resources.skills...'). "
            f"The skills provided above are TEXT INSTRUCTIONS. You must IMPLEMENT the logic using standard Python libraries "
            f"(like 'requests', 'json', 'subprocess') based on the instructions provided in the skill documentation."
        )
        
        plan = await self.llm.generate(
            prompt=prompt_text,
            system_prompt="You are an autonomous agent."
        )
        print(f"📋 Plan: {plan}")

        # --- Self-Healing Dependency Logic ---
        import subprocess
        import importlib

        def ensure_dependency(module_name):
            try:
                importlib.import_module(module_name)
            except ImportError:
                print(f"🔧 Auto-Installing missing dependency: {module_name}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
                    importlib.invalidate_caches()
                    print(f"✅ Installed {module_name}")
                except Exception as e:
                    print(f"❌ Failed to install {module_name}: {e}")

        # Scan plan/skills for obvious python packages (naive heuristic for prototype)
        # In a real scenario, the LLM would explicitly list dependencies.
        # Here we just catch execution errors.
        
        # 2. Execute Tools (with Auto-Fix)
        # 2. Execute Tools (with Auto-Fix)
        {{TOOL_EXECUTION_LOGIC}}
        
        return "Execution Complete"

        
        return "Execution Complete"

if __name__ == "__main__":
    agent = {{CLASS_NAME}}()
    if len(sys.argv) > 1:
        asyncio.run(agent.run(sys.argv[1]))
    else:
        print("Please provide a task argument.")
