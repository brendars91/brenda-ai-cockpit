import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from error_handler import register_error_handlers
from health_checks import router as health_router
from rate_limiter import RateLimitMiddleware
from structured_logger import setup_logging, get_logger
from routers import register_routers
from runtime import start_background_services


def get_cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    return [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://app-eta-fawn-42.vercel.app",
        "https://web-production-3d530.up.railway.app"
    ]


setup_logging(
    log_level=os.environ.get("LOG_LEVEL", "INFO"),
    log_file="logs/api.log",
    json_format=True
)
logger = get_logger("api_server")

app = FastAPI(
    title="Gem Trinity Genesis API",
    version="2026.2.1",
    description="AI Agent Orchestration Platform with Deterministic-First Philosophy"
)

register_error_handlers(app)
app.include_router(health_router)

# Rate limiting: 120 requests per minute, 10 burst (stricter for testing)
app.add_middleware(RateLimitMiddleware, requests_per_minute=120, burst_limit=10)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

start_background_services()
register_routers(app)

static_path = os.path.join(os.getcwd(), "static")
if not os.path.isdir(static_path):
    os.makedirs(static_path, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/dashboard")
async def dashboard():
    return FileResponse("static/dashboard.html")


if __name__ == "__main__":
    import uvicorn

    print("--- Gem Trinity API Server Starting ---")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
