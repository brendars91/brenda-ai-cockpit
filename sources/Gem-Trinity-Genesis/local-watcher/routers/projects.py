import json
from pathlib import Path

from fastapi import APIRouter

from structured_logger import get_logger
from runtime import architect, builder

router = APIRouter()
logger = get_logger("projects")


@router.get("/api/projects")
async def get_all_projects():
    projects = []

    architect_history = architect.get_history()
    for item in architect_history:
        projects.append({
            "id": item["payload_id"],
            "name": item.get("use_case", "")[:50] or f"Project {item['payload_id'][:8]}",
            "stage": "design",
            "domain": item.get("domain", "custom"),
            "created_at": item.get("timestamp", ""),
            "status": "ready"
        })

    agents = builder.get_agents()
    for agent in agents:
        existing = next((p for p in projects if p["id"] == agent.get("payload_id")), None)
        if existing:
            existing["stage"] = "compiled"
            existing["agent_id"] = agent["id"]
            existing["name"] = agent.get("name", existing["name"])
        else:
            projects.append({
                "id": agent.get("payload_id", agent["id"]),
                "agent_id": agent["id"],
                "name": agent.get("name", f"Agent {agent['id'][:8]}"),
                "stage": "compiled",
                "domain": "custom",
                "created_at": str(agent.get("compiled_at", "")),
                "status": "ready"
            })

    return {"projects": projects}


@router.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    deleted = []

    payload_file = Path(f"artifacts/architect_payloads/{project_id}.json")
    if payload_file.exists():
        try:
            payload_file.unlink()
            deleted.append("payload")
        except Exception as e:
            logger.warning("Failed to delete payload", extra={"error": str(e)})

    agents_dir = Path("artifacts/builder_agents")
    for agent_file in agents_dir.glob("*.json"):
        try:
            agent_data = json.loads(agent_file.read_text())
            if agent_data.get("payload_id") == project_id or agent_data.get("id") == project_id:
                agent_file.unlink()
                deleted.append("agent")
                script_path = agent_data.get("script_path")
                if script_path and Path(script_path).exists():
                    Path(script_path).unlink()
        except Exception:
            continue

    output_dir = Path(f"artifacts/project_outputs/{project_id}")
    if output_dir.exists():
        import shutil
        try:
            shutil.rmtree(output_dir)
            deleted.append("workspace")
        except Exception as e:
            logger.warning("Failed to delete workspace", extra={"error": str(e)})

    architect.delete_from_history(project_id)

    return {"status": "success", "deleted": deleted}
