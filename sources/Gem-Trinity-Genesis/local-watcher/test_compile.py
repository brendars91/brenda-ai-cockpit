import httpx
import json

url = "http://localhost:8000/api/builder/compile"
payload = {
    "payload_id": "ffea4538-26c1-48bd-abf3-00988cb31b4e",
    "agent_name": "Antigravity Auditor",
    "llm_config": {"model": "gemini-1.5-pro", "temperature": 0.2},
    "tools": ["filesystem", "sequential-thinking", "grep_search", "write_to_file"]
}

try:
    print("Sending compilation request...")
    res = httpx.post(url, json=payload, timeout=60.0)
    print(f"Status Code: {res.status_code}")
    print("Response Body:")
    print(res.text)
except Exception as e:
    print(f"Error: {e}")
