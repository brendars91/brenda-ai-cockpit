from fastapi import APIRouter

from github_sync import github_sync

router = APIRouter()


@router.get("/api/github/status")
async def github_status():
    result = await github_sync.test_connection()
    result["is_production"] = github_sync.is_production
    result["is_configured"] = github_sync.is_configured()
    return result


@router.post("/api/github/sync")
async def github_sync_resources():
    result = await github_sync.sync_all_resources()
    return result


@router.get("/api/github/agents")
async def github_get_agents():
    result = await github_sync.get_agent_folders()
    return {"agents": result}
