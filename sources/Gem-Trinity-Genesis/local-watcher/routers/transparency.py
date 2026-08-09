"""
Transparency Router
Provides endpoints for users to inspect agent inputs/outputs.
"""
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel

from agent_transparency import get_transparency_logger


router = APIRouter(prefix="/api/transparency", tags=["Transparency"])


class ExecutionDetailResponse(BaseModel):
    execution_id: str
    agent_name: str
    agent_type: str
    timestamp: str
    status: str
    duration_ms: Optional[int] = None
    error: Optional[str] = None


class InputOutputResponse(BaseModel):
    execution_id: str
    agent_name: str
    agent_type: str
    timestamp: str
    input_data: dict
    output_data: dict
    status: str
    duration_ms: Optional[int] = None
    error: Optional[str] = None


@router.get("/executions", response_model=list[ExecutionDetailResponse])
async def list_executions(
    agent_type: Optional[str] = Query(None, description="Filter by agent type: architect, builder, engine"),
    limit: int = Query(50, ge=1, le=100, description="Number of executions to return")
):
    """List recent agent executions."""
    logger = get_transparency_logger()
    executions = logger.get_agent_executions(agent_type=agent_type, limit=limit)
    
    return [
        ExecutionDetailResponse(
            execution_id=e['execution_id'],
            agent_name=e['agent_name'],
            agent_type=e['agent_type'],
            timestamp=e['timestamp'],
            status=e['status'],
            duration_ms=e.get('duration_ms'),
            error=e.get('error')
        )
        for e in executions
    ]


@router.get("/execution/{execution_id}", response_model=InputOutputResponse)
async def get_execution_detail(execution_id: str):
    """Get full details of a specific execution including input/output."""
    logger = get_transparency_logger()
    execution = logger.get_execution(execution_id)
    
    if not execution:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return InputOutputResponse(
        execution_id=execution['execution_id'],
        agent_name=execution['agent_name'],
        agent_type=execution['agent_type'],
        timestamp=execution['timestamp'],
        input_data=execution['input_data'],
        output_data=execution['output_data'],
        status=execution['status'],
        duration_ms=execution.get('duration_ms'),
        error=execution.get('error')
    )


@router.get("/execution/{execution_id}/input")
async def get_execution_input(execution_id: str):
    """Get only the input data for an execution."""
    logger = get_transparency_logger()
    input_data = logger.get_execution_input(execution_id)
    
    if input_data is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {"execution_id": execution_id, "input": input_data}


@router.get("/execution/{execution_id}/output")
async def get_execution_output(execution_id: str):
    """Get only the output data for an execution."""
    logger = get_transparency_logger()
    output_data = logger.get_execution_output(execution_id)
    
    if output_data is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {"execution_id": execution_id, "output": output_data}


@router.get("/agent-types")
async def list_agent_types():
    """Get list of all agent types that have been executed."""
    logger = get_transparency_logger()
    return {"agent_types": logger.get_all_agent_types()}


@router.post("/execution/{execution_id}/copy-input")
async def copy_input_to_clipboard(execution_id: str):
    """Get formatted input for copying (for user convenience)."""
    logger = get_transparency_logger()
    input_data = logger.get_execution_input(execution_id)
    
    if input_data is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Format as pretty JSON for easy copying
    import json
    formatted = json.dumps(input_data, indent=2, ensure_ascii=False)
    
    return {
        "execution_id": execution_id,
        "formatted_input": formatted,
        "copy_paste_ready": True
    }


@router.post("/execution/{execution_id}/copy-output")
async def copy_output_to_clipboard(execution_id: str):
    """Get formatted output for copying (for user convenience)."""
    logger = get_transparency_logger()
    output_data = logger.get_execution_output(execution_id)
    
    if output_data is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    
    import json
    formatted = json.dumps(output_data, indent=2, ensure_ascii=False)
    
    return {
        "execution_id": execution_id,
        "formatted_output": formatted,
        "copy_paste_ready": True
    }


@router.post("/execution/{execution_id}/copy-full")
async def copy_full_execution(execution_id: str):
    """Get full execution (input + output) formatted for copying."""
    logger = get_transparency_logger()
    execution = logger.get_execution(execution_id)
    
    if not execution:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Execution not found")
    
    import json
    formatted = f"""# Agent Execution: {execution['agent_name']}
# Type: {execution['agent_type']}
# Timestamp: {execution['timestamp']}
# Status: {execution['status']}
# Duration: {execution.get('duration_ms', 'N/A')}ms

## INPUT:
{json.dumps(execution['input_data'], indent=2, ensure_ascii=False)}

## OUTPUT:
{json.dumps(execution['output_data'], indent=2, ensure_ascii=False)}

## ERROR:
{execution.get('error', 'None')}
"""
    
    return {
        "execution_id": execution_id,
        "formatted_execution": formatted,
        "markdown_ready": True
    }


# Alias for backwards compatibility with tests
@router.get("/history")
async def transparency_history_alias(
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    limit: int = Query(50, ge=1, le=100, description="Number of executions to return")
):
    """Alias for /api/transparency/executions for backwards compatibility."""
    return await list_executions(agent_type=agent_type, limit=limit)
