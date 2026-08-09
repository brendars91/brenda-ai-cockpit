import requests
import time
import json
import sys

BASE_URL = "http://localhost:8000/api"

def print_step(step):
    print(f"\n{'='*50}")
    print(f"STEP: {step}")
    print(f"{'='*50}")

def test_full_flow():
    print_step("1. CHECK SYSTEM HEALTH")
    try:
        r = requests.get(f"{BASE_URL}/status")
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
        if r.status_code != 200:
            print("System not healthy. Aborting.")
            sys.exit(1)
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    print_step("2. ARCHITECT: GENERATE SPEC (Todo App)")
    # Request a simple Todo Spec
    payload = {
        "use_case": "Create a simple Python command line Todo List application. It should allow adding, listing, and deleting tasks. Save tasks to a file.",
        "domain": "custom",
        "complexity": "simple",
        "model": "gemini-pro"
    }
    
    start_time = time.time()
    # Note: creating a dedicated test endpoint or using existing generate
    # Assuming /architect/generate returns the payload directly
    try:
        r = requests.post(f"{BASE_URL}/architect/generate", json=payload)
        if r.status_code == 200:
            architect_response = r.json()
            print("Architect Success!")
            print(f"Project Name: {architect_response.get('name')}")
            print(f"Files proposed: {len(architect_response.get('files', []))}")
        else:
            print(f"Architect Failed: {r.text}")
            # If backend creates dummy automatically, we might proceed? 
            # But let's assume we need this to pass.
            sys.exit(1)
    except Exception as e:
        print(f"Architect Error: {e}")
        sys.exit(1)

    # Let's verify we got a project ID or similar
    project_id = architect_response.get("id") or "todo_app_demo"
    print(f"Project ID: {project_id}")

    print_step("3. BUILDER: COMPILE AGENT")
    # Now we ask the builder to prepare the environment/agent for this project
    # Using /api/execute endpoint which handles async jobs
    build_payload = {
        "action": "compile",
        "target": project_id 
    }
    r = requests.post(f"{BASE_URL}/execute", json=build_payload)
    print(f"Builder Triggered: {r.status_code}")
    print(r.json())
    
    # Wait a bit for "compilation" (simulation)
    time.sleep(2)

    print_step("4. ENGINE: EXECUTE CODING TASK")
    # Now trigger the engine to actually write the code
    run_payload = {
        "action": "run",
        "target": project_id
    }
    r = requests.post(f"{BASE_URL}/execute", json=run_payload)
    print(f"Engine Triggered: {r.status_code}")
    print(r.json())

    # Wait for execution simulation
    time.sleep(5)

    print_step("5. VERIFICATION")
    # Check if files exist
    # Assuming they land in ../projects/{project_id}
    # But current system might output to artifacts/project_outputs
    
    print("Test Flow Completed (Async parts may still be running)")

if __name__ == "__main__":
    test_full_flow()
