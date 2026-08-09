
import os
import sys
import json
import asyncio
from typing import Dict, Any
from pathlib import Path

# Force UTF-8 output for Windows compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
        def generate(self, prompt, system_prompt=""):
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
        
        plan = self.llm.generate(
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

        # 2. Execute Logic (Code Interpreter Pattern)
        execution_prompt = (
            f"Based on the plan: {plan}\n"
            f"Write a Python script to perform the task: '{task}'.\n"
            f"Requirements:\n"
            f"1. Print the final result explicitly with 'FINAL RESULT: <value>'\n"
            f"2. Use provided tools if necessary.\n"
            f"3. Return ONLY the Python code in a markdown block (```python ... ```).\n"
        )
        
        code_response = str(self.llm.generate(execution_prompt, system_prompt="You are a Python Expert. Write code to solve the task."))
        
        # Extract code
        code_block = ""
        if "```python" in code_response:
            code_block = code_response.split("```python")[1].split("```")[0].strip()
        elif "```" in code_response:
            code_block = code_response.split("```")[1].split("```")[0].strip()
        else:
            if "def " in code_response or "print(" in code_response:
                code_block = code_response
        
        if code_block:
            print(f"💻 Executing Generated Code:\n{code_block}")
            try:
                # Execute in a restricted scope, but allow imports
                local_scope = {"context": self.context, "print": print}
                exec(code_block, globals(), local_scope)
                print("✅ Code execution successful.")
            except Exception as e:
                print(f"❌ Code execution failed: {e}")
        else:
            print("⚠️ No executable code found in LLM response.")

        return "Execution Complete"

if __name__ == "__main__":
    agent = {{CLASS_NAME}}()
    if len(sys.argv) > 1:
        asyncio.run(agent.run(sys.argv[1]))
    else:
        print("Please provide a task argument.")
