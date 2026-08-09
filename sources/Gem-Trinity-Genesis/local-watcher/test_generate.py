import httpx
import json
import time

url = "http://localhost:8000/api/architect/generate"
payload = {
    "use_case": "Project Antigravity: A meta-agent that monitors the Gem-Trinity-Genesis codebase. It uses the filesystem and coding tools to identify redundant code patterns and creates optimizations. It features a Mirror Test capability where it attempts to hack its own API to verify security.",
    "domain": "software_engineering",
    "complexity": "hard",
    "model": "gemini-1.5-pro"
}

try:
    print("Sending request...")
    # Increased timeout significantly as Architect might take time to 'think'
    res = httpx.post(url, json=payload, timeout=60.0)
    print(f"Status Code: {res.status_code}")
    print("Response Body:")
    print(res.text)
except Exception as e:
    print(f"Error: {e}")
