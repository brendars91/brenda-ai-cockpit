import json
import asyncio
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api_models import EngineExecuteRequest
from runtime import engine
from agent_transparency import get_transparency_logger

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/api/engine/execute")
async def engine_execute(req: EngineExecuteRequest):
    # Initialize transparency logger
    transparency = get_transparency_logger()

    # Get agent name for logging
    agent_data = engine._get_agent_data(req.agent_id) if hasattr(engine, '_get_agent_data') else {}
    agent_name = agent_data.get('name', f'agent_{req.agent_id[:8]}') if agent_data else f'agent_{req.agent_id[:8]}'

    # Log execution start
    input_data = {
        "agent_id": req.agent_id,
        "agent_name": agent_name,
        "task": req.task,
        "stream": req.stream
    }
    execution_id = transparency.log_execution_start(
        agent_name=agent_name,
        agent_type="engine",
        input_data=input_data
    )

    collected_output = {"execution_id": execution_id, "logs": [], "result": None}

    async def generate():
        nonlocal collected_output
        status = "unknown"

        try:
            async for event in engine.execute_agent(req.agent_id, req.task, req.stream):
                # Collect output for transparency
                if isinstance(event, dict):
                    if event.get("type") == "result":
                        collected_output["result"] = event.get("output", {})
                        status = "success"
                    elif event.get("type") == "log":
                        msg = event.get("message", "")
                        collected_output["logs"].append(msg)
                    elif event.get("type") == "error":
                        collected_output["error"] = event.get("message", "")
                        status = "failed"

                # Flush each event immediately
                yield json.dumps(event) + "\n"
                # Small delay to ensure buffer flush
                await asyncio.sleep(0)

        except Exception as e:
            logger.error(f"Engine execution error: {e}")
            error_event = {
                "type": "error",
                "message": str(e),
                "status": "failed"
            }
            collected_output["error"] = str(e)
            status = "failed"
            yield json.dumps(error_event) + "\n"

        finally:
            # Always send a completion event
            completion_event = {
                "type": "done",
                "execution_id": execution_id,
                "status": status
            }
            yield json.dumps(completion_event) + "\n"

            # Log execution complete after stream ends
            final_status = "success" if status == "success" else "failed"
            transparency.log_execution_complete(execution_id, collected_output, status=final_status)

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/api/engine/telemetry/{agent_id}")
async def engine_get_telemetry(agent_id: str):
    telemetry = engine.get_telemetry(agent_id)
    return telemetry
