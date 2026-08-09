from fastapi import APIRouter, HTTPException
from pathlib import Path
import json

from api_models import BuilderCompileRequest
from runtime import builder
from agent_transparency import get_transparency_logger

router = APIRouter()


@router.post("/api/builder/compile")
async def builder_compile(req: BuilderCompileRequest):
    # Initialize transparency logger
    transparency = get_transparency_logger()

    # Log execution start
    input_data = {
        "payload_id": req.payload_id,
        "agent_name": req.agent_name,
        "llm_config": req.llm_config,
        "tools": req.tools
    }
    execution_id = transparency.log_execution_start(
        agent_name=req.agent_name,
        agent_type="builder",
        input_data=input_data
    )

    try:
        result = builder.compile_agent(
            payload_id=req.payload_id,
            agent_name=req.agent_name,
            model_config=req.llm_config,
            tools=req.tools
        )

        # Log execution complete
        output_data = {
            "build_id": result.get("build_id"),
            "status": result.get("status"),
            "position": result.get("position")
        }
        transparency.log_execution_complete(execution_id, output_data, status="success")

        # Include execution_id in response for transparency
        result["_execution_id"] = execution_id

        return result
    except Exception as e:
        transparency.log_execution_complete(execution_id, {}, status="failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/builder/queue")
async def builder_get_queue():
    queue = builder.get_queue()
    return {"queue": queue}


@router.get("/api/builder/agents")
async def builder_get_agents():
    agents = builder.get_agents()
    return {"agents": agents}


@router.get("/api/builder/agent/{agent_id}")
async def builder_get_agent(agent_id: str):
    """Get agent by build_id or payload_id."""
    # First try to get by build_id (direct file lookup)
    agent = builder.get_agent(agent_id)

    # If not found, try to find by payload_id in agent metadata
    if not agent:
        agents_dir = Path("artifacts/builder_agents")
        for agent_file in agents_dir.glob("*.json"):
            try:
                agent_data = json.loads(agent_file.read_text())
                if agent_data.get("payload_id") == agent_id or agent_data.get("build_id") == agent_id:
                    return {
                        "agent_id": agent_data.get("build_id"),
                        "payload_id": agent_data.get("payload_id"),
                        "name": agent_data.get("name"),
                        "status": agent_data.get("status", "ready"),
                        "script_path": agent_data.get("script_path"),
                        "created_at": agent_data.get("created_at")
                    }
            except Exception:
                pass

        # If still not found, return 404
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found. It may still be building or the ID is incorrect.")

    return agent
