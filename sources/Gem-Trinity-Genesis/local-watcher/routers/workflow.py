from fastapi import APIRouter, HTTPException

from runtime import progress_tracker, state_store
from state_store import WorkflowStage

router = APIRouter()


@router.get("/api/workflow/{workflow_id}/progress")
async def get_workflow_progress(workflow_id: str):
    workflow = progress_tracker.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow.to_dict()


@router.get("/api/workflows/active")
async def get_active_workflows():
    workflows = state_store.get_active_workflows()

    for wf in workflows:
        progress = progress_tracker.get_workflow(wf["id"])
        if progress:
            wf["progress"] = progress.to_dict()

    return {"workflows": workflows}


@router.get("/api/workflows/history/{workflow_id}")
async def get_workflow_history(workflow_id: str, limit: int = 50):
    history = state_store.get_workflow_history(workflow_id, limit)
    return {"history": history}


@router.post("/api/workflow/{workflow_id}/stage")
async def set_workflow_stage(workflow_id: str, stage: str):
    try:
        workflow_stage = WorkflowStage(stage)
        progress_tracker.set_stage(workflow_id, workflow_stage)
        return {"status": "success", "stage": stage}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {stage}")


@router.get("/api/state/stats")
async def get_state_store_stats():
    return state_store.get_stats()


@router.get("/api/progress/all")
async def get_all_progress():
    return {"workflows": progress_tracker.get_all_progress()}
