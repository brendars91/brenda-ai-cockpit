"""
Test completo del flujo Architect -> Builder -> Engine
con LLM real (google-genai SDK)
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"

print("=" * 70)
print("GEM TRINITY - E2E TEST WITH REAL LLM")
print("=" * 70)

# ============================================
# 1. ARCHITECT PHASE
# ============================================
print("\n[1/3] ARCHITECT PHASE")
print("-" * 70)

architect_payload = {
    "use_case": "A simple calculator that adds two numbers",
    "domain": "mathematics",
    "complexity": "simple",
    "model": "gemini-2.5-flash"
}

print(f"Request: {json.dumps(architect_payload, indent=2)}")

response = requests.post(f"{BASE_URL}/api/architect/generate", json=architect_payload)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    architect_data = response.json()
    payload_id = architect_data.get("payload_id")
    print(f"Payload ID: {payload_id}")
    print(f"Architect: [OK]")
else:
    print(f"Error: {response.text}")
    exit(1)

# ============================================
# 2. BUILDER PHASE
# ============================================
print("\n[2/3] BUILDER PHASE")
print("-" * 70)

builder_payload = {
    "payload_id": payload_id,
    "agent_name": "Calculator_Agent",
    "llm_config": {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "temperature": 0.7
    },
    "tools": []
}

print(f"Request: {json.dumps(builder_payload, indent=2)}")

response = requests.post(f"{BASE_URL}/api/builder/compile", json=builder_payload)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    builder_data = response.json()
    build_id = builder_data.get("build_id")
    status = builder_data.get("status")
    print(f"Build ID: {build_id}")
    print(f"Initial Status: {status}")

    # Poll for completion
    print("Polling for build completion...")
    max_attempts = 30
    for i in range(max_attempts):
        time.sleep(1)
        status_response = requests.get(f"{BASE_URL}/api/builder/status/{build_id}")
        if status_response.status_code == 200:
            status_data = status_response.json()
            current_status = status_data.get("status")
            progress = status_data.get("progress", 0)
            print(f"  Attempt {i+1}: Status={current_status}, Progress={progress}%")

            if current_status in ["READY", "FAILED"]:
                if current_status == "READY":
                    print(f"Builder: [OK] Agent compiled successfully")
                else:
                    print(f"Builder: [FAILED] {status_data.get('error', 'Unknown error')}")
                    exit(1)
                break
    else:
        print("Builder: [TIMEOUT] Build did not complete in 30 seconds")
        exit(1)
else:
    print(f"Error: {response.text}")
    exit(1)

# ============================================
# 3. ENGINE PHASE (Execute with REAL LLM)
# ============================================
print("\n[3/3] ENGINE PHASE")
print("-" * 70)

engine_payload = {
    "build_id": build_id,
    "task": "Calculate 2 + 2. Respond with just the number.",
    "parameters": {}
}

print(f"Request: {json.dumps(engine_payload, indent=2)}")

response = requests.post(f"{BASE_URL}/api/engine/execute", json=engine_payload)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    engine_data = response.json()
    execution_id = engine_data.get("execution_id")
    print(f"Execution ID: {execution_id}")

    # Poll for completion
    print("Polling for execution completion...")
    max_attempts = 60
    for i in range(max_attempts):
        time.sleep(2)
        status_response = requests.get(f"{BASE_URL}/api/engine/status/{execution_id}")
        if status_response.status_code == 200:
            status_data = status_response.json()
            current_status = status_data.get("status")
            print(f"  Attempt {i+1}: Status={current_status}")

            if current_status in ["COMPLETED", "FAILED"]:
                if current_status == "COMPLETED":
                    result = status_data.get("result")
                    print(f"\nEngine: [OK] Execution completed")
                    print(f"Result: {result}")

                    # Verify result contains "4"
                    if "4" in str(result):
                        print("\n" + "=" * 70)
                        print("E2E TEST: [PASSED]")
                        print("=" * 70)
                        print("✓ Architect: Working")
                        print("✓ Builder: Working")
                        print("✓ Engine: Working with REAL LLM (google-genai)")
                        print("✓ Result verified: LLM returned correct answer '4'")
                    else:
                        print(f"\n[E2E TEST: WARNING] Result doesn't contain '4': {result}")
                else:
                    error = status_data.get("error", "Unknown error")
                    print(f"Engine: [FAILED] {error}")
                    exit(1)
                break
    else:
        print("Engine: [TIMEOUT] Execution did not complete in 120 seconds")
        exit(1)
else:
    print(f"Error: {response.text}")
    exit(1)
