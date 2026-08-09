import asyncio
import sys
import os
import time

# Force UTF-8 for Windows Console
sys.stdout.reconfigure(encoding='utf-8')

# Add local path
sys.path.append(os.getcwd())

from architect_service import ArchitectService
from builder_service import BuilderService
from engine_service import EngineService
from skill_scanner import SkillScanner

async def test_flow():
    print("--- Testing Gem Trinity Genesis Agents (Real Mode) ---")

    # 0. Skills
    print("\n[0] Scanning Skills...")
    scanner = SkillScanner()
    skills_map = scanner.scan()
    print(f"✅ Skills Found: {len(skills_map.get('skills', []))}")
    
    # 1. Builder Setup
    print("\n[1] Testing Builder & Skill Injection...")
    builder = BuilderService()
    builder._start_worker()

    # Case A: SAP Agent (General)
    payload_sap = {
        "payload_id": "test-sap-001",
        "agent_name": "SAP_Bot",
        "model_config": {"model": "gemini-ultra"},
        "tools": ["sap_connector"]
    }
    
    # Case B: PDF Agent (Real Skill)
    payload_pdf = {
        "payload_id": "test-pdf-001",
        "agent_name": "PDF_Reporter",
        "model_config": {"model": "gemini-flash"},
        "tools": ["pdf", "file-system"] 
    }

    print("   Submitting SAP Job...")
    job_sap = builder.compile_agent(**payload_sap)
    id_sap = job_sap['build_id']

    print("   Submitting PDF Job...")
    job_pdf = builder.compile_agent(**payload_pdf)
    id_pdf = job_pdf['build_id']

    # Wait for completion
    print("   Waiting for builds...")
    completed = []
    for _ in range(45):
        q = builder.get_queue()
        
        item_sap = next((i for i in q if i['build_id'] == id_sap), None)
        item_pdf = next((i for i in q if i['build_id'] == id_pdf), None)
        
        if item_sap and item_sap['status'] == 'READY' and id_sap not in completed:
            print(f"✅ SAP Agent Ready: {id_sap}")
            completed.append(id_sap)
            
        if item_pdf and item_pdf['status'] == 'READY' and id_pdf not in completed:
            print(f"✅ PDF Agent Ready: {id_pdf}")
            completed.append(id_pdf)
            
        if len(completed) >= 2:
            break
            
        time.sleep(1)

    if len(completed) < 2:
        print("❌ Timeout waiting for builds")
        return

    # 2. Engine Execution
    print("\n[2] Testing Real Execution...")
    engine = EngineService()
    
    # Run PDF Agent to verify Skill Injection
    print(f"   Executing PDF Agent ({id_pdf})...")
    task = "Create a summary report.pdf with 'Hello World'"
    
    async for event in engine.execute_agent(id_pdf, task):
        print(f"   [PDF-Agent] {event}")
        # Verify if python code is actually executed (logs will show)

    print("\n✅ Verification Complete")

if __name__ == "__main__":
    if not os.path.exists("artifacts"):
        os.makedirs("artifacts")
    asyncio.run(test_flow())
