
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def check_status():
    try:
        print("Checking API Status...")
        resp = requests.get(f"{BASE_URL}/api/status")
        print(f"Status: {resp.status_code}")
        print(resp.json())
        return True
    except Exception as e:
        print(f"Failed to connect: {e}")
        return False

def list_agents():
    try:
        print("\nListing Agents...")
        resp = requests.get(f"{BASE_URL}/api/builder/agents")
        agents = resp.json().get("agents", [])
        print(f"Agents Found: {len(agents)}")
        for agent in agents:
            print(f"- {agent}")
        return agents
    except Exception as e:
        print(f"Failed to list agents: {e}")
        return []

def main():
    # Wait for server to start
    for i in range(10):
        if check_status():
            break
        print("Waiting for server...")
        time.sleep(2)
    
    agents = list_agents()
    
    if agents:
        first_agent = agents[0]
        print(f"DEBUG: First agent data: {first_agent}, Type: {type(first_agent)}")
        
        if isinstance(first_agent, dict):
             agent_id = first_agent.get("id") or first_agent.get("agent_id") or first_agent.get("name")
        else:
             agent_id = str(first_agent)
             
        print(f"\nTesting Agent Execution: {agent_id}")
        payload = {
            "agent_id": agent_id,
            "task": "Read the README.md file in the project root and suggest one security improvement based on OWASP.",
            "stream": False 
        }
        # Note: API might stream, but requests handling streaming needs special care. 
        # The code usually returns a StreamingResponse. 
        # For this test, we just want to see if it accepts the request.
        
        try:
            print(f"Sending request to {BASE_URL}/api/engine/execute...")
            resp = requests.post(f"{BASE_URL}/api/engine/execute", json=payload, stream=True)
            print(f"Execute Response Status: {resp.status_code}")
            
            with open("verification_result.log", "w", encoding="utf-8") as f:
                for line in resp.iter_lines():
                    if line:
                        decoded = line.decode('utf-8')
                        print(decoded) # Still print to stdout
                        f.write(decoded + "\n")
            print("Logs saved to verification_result.log")
                        
        except Exception as e:
            print(f"Execution failed: {e}")
    else:
        print("\nNo agents found. Cannot test execution without an agent.")

if __name__ == "__main__":
    main()
