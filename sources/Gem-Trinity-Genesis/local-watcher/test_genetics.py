
import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000"

def test_skill_adaptation():
    print("[TEST] Starting Skill Adaptation Test (Genetics Protocol)...")
    
    # 1. Define a request with a NON-EXISTENT skill to force adaptation
    # "quantum-encryption-node" does not exist in the resources/skills folder.
    payload = {
        "payload_id": "test-genetics-01",
        "agent_name": "CipherGuardian",
        "llm_config": {"model": "gemini-2.0-flash"},
        "tools": ["quantum-encryption-node", "security-auditor"] 
    }
    
    try:
        # 2. Trigger Compilation (Builder)
        print(f"[BUILD] Sending Compilation Request for: {payload['agent_name']}")
        print(f"   forcing adaptation for unknown skill: 'quantum-encryption-node'")
        
        resp = requests.post(f"{BASE_URL}/api/builder/compile", json=payload)
        if resp.status_code != 200:
            print(f"[ERROR] Build Request Failed: {resp.text}")
            return

        build_data = resp.json()
        build_id = build_data.get("build_id")
        print(f"[OK] Build Started: ID {build_id}")
        
        # 3. Wait for Build (Should be fast now, no sleeps!)
        print("[WAIT] Waiting for compilation...")
        for _ in range(10):
            time.sleep(1)
            status_resp = requests.get(f"{BASE_URL}/api/builder/queue")
            queue = status_resp.json().get("queue", [])
            
            # Find our build
            my_build = next((item for item in queue if item["build_id"] == build_id), None)
            
            if not my_build: 
                # If gone from queue, check list of agents
                agent_resp = requests.get(f"{BASE_URL}/api/builder/agent/{build_id}")
                if agent_resp.status_code == 200:
                   print("[DONE] Compilation Complete!")
                   break
            elif my_build["status"] == "READY":
                 print("[DONE] Compilation Complete (In Queue)!")
                 break
            elif my_build["status"] == "FAILED":
                 print(f"[ERROR] Build Failed: {my_build.get('error')}")
                 return

        # 4. Verify Execution & Adaptation Log
        # We want to see if the system actually tries to use/simulate it.
        print("\n[EXEC] Executing Agent to verify Adaptation...")
        exec_payload = {
            "agent_id": build_id,
            "task": "Encrypt the string 'SECRET_DATA' using the quantum-cipher.",
            "stream": True
        }
        
        with requests.post(f"{BASE_URL}/api/engine/execute", json=exec_payload, stream=True) as r:
            print("--- Execution Logs ---")
            for line in r.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    # Look for specific signals
                    if "SKILL" in decoded or "adapt" in decoded.lower():
                        print(f"[GENETICS] DETECTED: {decoded}")
                    else:
                        print(decoded)
            print("----------------------")
            
    except Exception as e:
        print(f"[ERROR] Test Failed: {e}")

if __name__ == "__main__":
    test_skill_adaptation()
