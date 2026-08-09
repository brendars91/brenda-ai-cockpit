import threading
import platform
import psutil
import os
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException

from api_models import ExecuteRequest
from mirror_sync import start_mirroring
from config_manager import config
from runtime import sync_engine, mcp_grid, runner, state

router = APIRouter()


def get_system_boot_time():
    """Get system boot time."""
    try:
        boot_time = psutil.boot_time()
        return datetime.fromtimestamp(boot_time, tz=timezone.utc).isoformat()
    except:
        return datetime.now(timezone.utc).isoformat()


@router.get("/")
async def root():
    return {"status": "online", "message": "Gem Trinity Genesis API v2026.2.1 Running"}


@router.get("/api/status")
async def get_status():
    integrity_ok, integrity_msg = config.validate_integrity()

    return {
        "system": "online",
        "integrity": "ok" if integrity_ok else "error",
        "integrity_msg": integrity_msg,
        "mirror_sync": "active" if state.mirror_active else "idle",
        "mode": "autonomous_mirror"
    }


@router.get("/api/context")
async def get_context():
    payload = sync_engine.pack_context()
    return payload


@router.get("/api/mcp")
async def get_mcp_status():
    return mcp_grid.scan_grid()


@router.post("/api/execute")
async def execute_command(req: ExecuteRequest, background_tasks: BackgroundTasks):
    if req.action == "compile":
        background_tasks.add_task(runner.run_builder_compile, req.target)
        return {"status": "queued", "job": "builder_compile", "target": req.target}

    if req.action == "run":
        background_tasks.add_task(runner.run_engine_execute, req.target)
        return {"status": "queued", "job": "engine_execute", "target": req.target}

    raise HTTPException(status_code=400, detail="Invalid action")


@router.post("/api/mirror/toggle")
async def toggle_mirror():
    if state.mirror_active:
        return {"status": "stopped", "message": "Mirror sync disabled (restart to re-enable)"}

    state.mirror_thread = threading.Thread(target=start_mirroring, daemon=True)
    state.mirror_thread.start()
    state.mirror_active = True
    return {"status": "started", "message": "Mirror Sync Engine activated"}


@router.get("/api/system/info")
async def system_info():
    """Returns comprehensive system information."""
    try:
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)

        return {
            "python_version": platform.python_version(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "hostname": platform.node(),
            },
            "uptime": {
                "boot_time": get_system_boot_time(),
                "current_time": datetime.now(timezone.utc).isoformat(),
            },
            "resources": {
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "free": memory.free,
                    "percent": memory.percent
                },
                "cpu": {
                    "count": psutil.cpu_count(),
                    "percent": cpu_percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            },
            "process": {
                "pid": os.getpid(),
                "cwd": os.getcwd()
            }
        }
    except Exception as e:
        # Fallback if psutil fails
        return {
            "python_version": platform.python_version(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "hostname": platform.node(),
            },
            "error": str(e)
        }
