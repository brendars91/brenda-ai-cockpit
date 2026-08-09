import uuid

from fastapi import APIRouter, HTTPException

from api_models import ArchitectGenerateRequest
from progress_tracker import ProgressPhase, create_workflow_progress
from state_store import WorkflowStage
from runtime import architect, progress_tracker, state_store
from agent_transparency import get_transparency_logger

router = APIRouter()


@router.get("/api/architect/history")
async def architect_history():
    history = architect.get_history()
    return {"history": history}


@router.get("/api/architect/payload/{payload_id}")
async def architect_get_payload(payload_id: str):
    payload = architect.get_payload(payload_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Payload not found")
    return payload


@router.post("/api/architect/generate")
async def architect_generate_enhanced(req: ArchitectGenerateRequest):
    workflow_id = str(uuid.uuid4())
    project_name = f"{req.domain.upper()}_{workflow_id[:8]}"
    
    # Initialize transparency logger
    transparency = get_transparency_logger()
    
    # Log execution start
    input_data = {
        "use_case": req.use_case,
        "domain": req.domain,
        "complexity": req.complexity,
        "model": req.model,
        "workflow_id": workflow_id
    }
    execution_id = transparency.log_execution_start(
        agent_name=project_name,
        agent_type="architect",
        input_data=input_data
    )
    
    create_workflow_progress(workflow_id, project_name)
    progress_tracker.set_stage(workflow_id, WorkflowStage.ARCHITECTING)

    progress_tracker.start_step(workflow_id, ProgressPhase.ARCHITECT_ANALYZE)

    try:
        payload = architect.generate_payload(
            req.use_case,
            req.domain,
            req.complexity,
            req.model,
            project_name
        )
        
        # Log execution complete
        output_data = {
            "payload_id": payload.get("payload_id"),
            "prd": payload.get("prd", {}),
            "spec_contract": payload.get("spec_contract", {}),
            "context_payload": payload.get("context_payload", {})
        }
        transparency.log_execution_complete(execution_id, output_data, status="success")

        progress_tracker.complete_step(workflow_id, ProgressPhase.ARCHITECT_ANALYZE)
        progress_tracker.start_step(workflow_id, ProgressPhase.ARCHITECT_PRD)
        progress_tracker.complete_step(workflow_id, ProgressPhase.ARCHITECT_PRD)
        progress_tracker.start_step(workflow_id, ProgressPhase.ARCHITECT_SPEC)
        progress_tracker.complete_step(workflow_id, ProgressPhase.ARCHITECT_SPEC)
        progress_tracker.start_step(workflow_id, ProgressPhase.ARCHITECT_FINALIZE)
        progress_tracker.complete_step(workflow_id, ProgressPhase.ARCHITECT_FINALIZE)

        state_store.save_payload(
            payload["payload_id"],
            req.use_case,
            req.domain,
            req.complexity,
            req.model,
            payload
        )

        state_store.update_workflow(
            workflow_id,
            payload_id=payload["payload_id"],
            stage=WorkflowStage.ARCHITECT_REVIEW
        )

        progress_tracker.set_stage(workflow_id, WorkflowStage.ARCHITECT_REVIEW)
        
        # Include execution_id in response for transparency
        payload["_execution_id"] = execution_id
        
        return payload

    except Exception as e:
        progress_tracker.fail_step(workflow_id, ProgressPhase.ARCHITECT_ANALYZE, str(e))
        transparency.log_execution_complete(execution_id, {}, status="failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
