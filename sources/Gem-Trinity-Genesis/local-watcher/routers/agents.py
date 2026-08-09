from fastapi import APIRouter

from operation_tracker import get_metrics
from runtime import auditor

router = APIRouter()


@router.get("/api/agents/status")
async def get_all_agents_status():
    return {
        "architect": {"status": "idle", "role": "Planning", "version": "2.0"},
        "builder": {"status": "idle", "role": "Construction", "version": "1.5"},
        "engine": {"status": "active", "role": "Core Execution", "version": "4.0"},
        "guardian": {"status": "monitoring", "role": "Security", "version": "1.2"},
        "auditor": auditor.get_status()
    }


@router.get("/api/auditor/status")
async def get_auditor_status():
    return auditor.get_status()


@router.get("/api/engine/status")
async def get_engine_status():
    return {"status": "active", "version": "4.0", "load": get_metrics().get("total_operations", 0)}
