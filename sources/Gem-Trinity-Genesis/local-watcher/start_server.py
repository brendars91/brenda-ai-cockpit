import os
os.environ["PORT"] = "8002"

import uvicorn
from api_server import app

if __name__ == "__main__":
    print("--- Starting Gem Trinity on port 8002 ---")
    uvicorn.run(app, host="0.0.0.0", port=8002)
