"""
Progress Tracker v2.0 - Real-time Workflow Progress
Detailed progress tracking for Gem-Trinity Genesis workflows.
"""
import time
import asyncio
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from state_store import StateStore, WorkflowStage, WorkflowStatus
from websocket_manager import EventType, WebSocketEvent, get_websocket_manager

logger = logging.getLogger(__name__)

class ProgressPhase(str, Enum):
    """Progress phases for different operations"""
    # Architect phases
    ARCHITECT_ANALYZE = "architect.analyze"
    ARCHITECT_PRD = "architect.prd"
    ARCHITECT_SPEC = "architect.spec"
    ARCHITECT_FINALIZE = "architect.finalize"

    # Builder phases
    BUILDER_QUEUE = "builder.queue"
    BUILDER_DETECT_TOOLS = "builder.detect_tools"
    BUILDER_GENERATE_CODE = "builder.generate_code"
    BUILDER_AUDIT = "builder.audit"
    BUILDER_FINALIZE = "builder.finalize"

    # Engine phases
    ENGINE_QUEUE = "engine.queue"
    ENGINE_LOAD = "engine.load"
    ENGINE_EXECUTE = "engine.execute"
    ENGINE_HEAL = "engine.heal"
    ENGINE_FINALIZE = "engine.finalize"

@dataclass
class ProgressStep:
    """Single progress step"""
    phase: ProgressPhase
    name: str
    weight: float  # Weight for overall progress calculation (0-1)
    completed: bool = False
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None

    @property
    def duration(self) -> Optional[float]:
        """Step duration in seconds"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None

@dataclass
class WorkflowProgress:
    """Progress tracker for a workflow"""
    workflow_id: str
    project_name: str
    current_stage: WorkflowStage = WorkflowStage.IDLE
    steps: List[ProgressStep] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    error: Optional[str] = None

    # Callbacks for progress updates
    on_progress_update: Optional[Callable] = None
    on_stage_change: Optional[Callable] = None
    on_complete: Optional[Callable] = None
    on_error: Optional[Callable] = None

    @property
    def overall_progress(self) -> float:
        """Calculate overall progress (0-100)"""
        if not self.steps:
            return 0.0

        total_weight = sum(step.weight for step in self.steps)
        completed_weight = sum(step.weight for step in self.steps if step.completed)

        if total_weight == 0:
            return 0.0

        return (completed_weight / total_weight) * 100

    @property
    def current_step(self) -> Optional[ProgressStep]:
        """Get current active step"""
        for step in reversed(self.steps):
            if not step.completed and step.started_at:
                return step
        return None

    @property
    def eta_seconds(self) -> Optional[float]:
        """Estimated time to completion in seconds"""
        if self.completed_at:
            return 0

        current_step = self.current_step
        if not current_step or not current_step.started_at:
            return None

        # Calculate average step duration from completed steps
        completed_durations = [
            step.duration for step in self.steps
            if step.completed and step.duration
        ]

        if not completed_durations:
            return None

        avg_duration = sum(completed_durations) / len(completed_durations)

        # Count remaining steps
        remaining_steps = sum(1 for step in self.steps if not step.completed)

        return avg_duration * remaining_steps

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "workflow_id": self.workflow_id,
            "project_name": self.project_name,
            "current_stage": self.current_stage.value,
            "overall_progress": round(self.overall_progress, 1),
            "current_step": {
                "phase": self.current_step.phase.value if self.current_step else None,
                "name": self.current_step.name if self.current_step else None,
                "started_at": self.current_step.started_at if self.current_step else None
            },
            "steps": [
                {
                    "phase": step.phase.value,
                    "name": step.name,
                    "weight": step.weight,
                    "completed": step.completed,
                    "duration": step.duration
                }
                for step in self.steps
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "error": self.error,
            "eta_seconds": self.eta_seconds
        }

class ProgressTracker:
    """
    Centralized progress tracker for all workflows.

    Features:
    - Real-time progress tracking per workflow
    - Automatic WebSocket broadcasting
    - State persistence via StateStore
    - ETA calculation
    - Progress callbacks
    """

    def __init__(self):
        self.workflows: Dict[str, WorkflowProgress] = {}
        self.state_store = StateStore()
        self.ws_manager = get_websocket_manager()

    def create_workflow(
        self,
        workflow_id: str,
        project_name: str,
        on_progress_update: Optional[Callable] = None,
        on_stage_change: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None
    ) -> WorkflowProgress:
        """Create a new workflow progress tracker"""
        workflow = WorkflowProgress(
            workflow_id=workflow_id,
            project_name=project_name,
            on_progress_update=on_progress_update,
            on_stage_change=on_stage_change,
            on_complete=on_complete,
            on_error=on_error
        )

        self.workflows[workflow_id] = workflow

        # Save to state store
        self.state_store.create_workflow(
            workflow_id=workflow_id,
            project_name=project_name
        )

        logger.info(f"[Progress] Created workflow: {workflow_id}")
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowProgress]:
        """Get workflow progress"""
        return self.workflows.get(workflow_id)

    def set_stage(self, workflow_id: str, stage: WorkflowStage):
        """Set workflow stage and initialize steps"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            logger.warning(f"[Progress] Workflow not found: {workflow_id}")
            return

        old_stage = workflow.current_stage
        workflow.current_stage = stage
        workflow.updated_at = time.time()

        # Initialize steps for stage
        workflow.steps = self._get_steps_for_stage(stage)

        # Update state store
        self.state_store.update_workflow(
            workflow_id=workflow_id,
            stage=stage,
            status=WorkflowStatus.IN_PROGRESS
        )

        # Broadcast stage change
        asyncio.create_task(self.ws_manager.broadcast_workflow_stage(
            workflow_id, stage.value, "in_progress"
        ))

        # Call callback
        if workflow.on_stage_change:
            workflow.on_stage_change(old_stage, stage)

        logger.info(f"[Progress] {workflow_id} stage: {old_stage.value} -> {stage.value}")

    def start_step(self, workflow_id: str, phase: ProgressPhase):
        """Mark a step as started"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return

        for step in workflow.steps:
            if step.phase == phase:
                step.started_at = time.time()
                workflow.updated_at = time.time()

                # Broadcast progress update
                asyncio.create_task(self._broadcast_progress(workflow))

                logger.info(f"[Progress] {workflow_id} step started: {phase.value}")
                return

        logger.warning(f"[Progress] Step not found: {phase.value}")

    def complete_step(self, workflow_id: str, phase: ProgressPhase):
        """Mark a step as completed"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return

        for step in workflow.steps:
            if step.phase == phase:
                step.completed = True
                step.completed_at = time.time()
                workflow.updated_at = time.time()

                # Broadcast progress update
                asyncio.create_task(self._broadcast_progress(workflow))

                logger.info(f"[Progress] {workflow_id} step completed: {phase.value}")
                return

        logger.warning(f"[Progress] Step not found: {phase.value}")

    def fail_step(self, workflow_id: str, phase: ProgressPhase, error: str):
        """Mark a step as failed"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return

        for step in workflow.steps:
            if step.phase == phase:
                step.error = error
                step.completed_at = time.time()
                workflow.error = error
                workflow.updated_at = time.time()

                # Update state store
                self.state_store.update_workflow(
                    workflow_id=workflow_id,
                    status=WorkflowStatus.FAILED,
                    error=error
                )

                # Broadcast error
                asyncio.create_task(self.ws_manager.broadcast(
                    WebSocketEvent(EventType.SYSTEM_ERROR, {
                        "workflow_id": workflow_id,
                        "phase": phase.value,
                        "error": error
                    })
                ))

                # Call error callback
                if workflow.on_error:
                    workflow.on_error(error)

                logger.error(f"[Progress] {workflow_id} step failed: {phase.value} - {error}")
                return

    def complete_workflow(self, workflow_id: str):
        """Mark workflow as completed"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return

        workflow.completed_at = time.time()
        workflow.updated_at = time.time()

        # Update state store
        self.state_store.update_workflow(
            workflow_id=workflow_id,
            stage=WorkflowStage.COMPLETED,
            status=WorkflowStatus.COMPLETED
        )

        # Broadcast completion
        asyncio.create_task(self.ws_manager.broadcast_workflow_stage(
            workflow_id, "completed", "completed"
        ))

        # Call callback
        if workflow.on_complete:
            workflow.on_complete()

        logger.info(f"[Progress] Workflow completed: {workflow_id}")

    def _get_steps_for_stage(self, stage: WorkflowStage) -> List[ProgressStep]:
        """Get progress steps for a stage"""
        steps = []

        if stage == WorkflowStage.ARCHITECTING:
            steps = [
                ProgressStep(ProgressPhase.ARCHITECT_ANALYZE, "Analyzing requirements", 0.2),
                ProgressStep(ProgressPhase.ARCHITECT_PRD, "Generating PRD", 0.4),
                ProgressStep(ProgressPhase.ARCHITECT_SPEC, "Creating spec contract", 0.3),
                ProgressStep(ProgressPhase.ARCHITECT_FINALIZE, "Finalizing payload", 0.1),
            ]
        elif stage == WorkflowStage.BUILDING:
            steps = [
                ProgressStep(ProgressPhase.BUILDER_QUEUE, "Queuing build", 0.05),
                ProgressStep(ProgressPhase.BUILDER_DETECT_TOOLS, "Detecting tools", 0.15),
                ProgressStep(ProgressPhase.BUILDER_GENERATE_CODE, "Generating code", 0.4),
                ProgressStep(ProgressPhase.BUILDER_AUDIT, "Running security audit", 0.3),
                ProgressStep(ProgressPhase.BUILDER_FINALIZE, "Finalizing agent", 0.1),
            ]
        elif stage == WorkflowStage.ENGINE_ACTIVE:
            steps = [
                ProgressStep(ProgressPhase.ENGINE_QUEUE, "Queuing execution", 0.05),
                ProgressStep(ProgressPhase.ENGINE_LOAD, "Loading agent", 0.1),
                ProgressStep(ProgressPhase.ENGINE_EXECUTE, "Executing task", 0.7),
                ProgressStep(ProgressPhase.ENGINE_FINALIZE, "Finalizing results", 0.15),
            ]

        return steps

    async def _broadcast_progress(self, workflow: WorkflowProgress):
        """Broadcast progress update via WebSocket"""
        event = WebSocketEvent(
            EventType.WORKFLOW_STAGE_CHANGE,
            {
                "workflow_id": workflow.workflow_id,
                "stage": workflow.current_stage.value,
                "progress": workflow.overall_progress,
                "current_step": {
                    "phase": workflow.current_step.phase.value if workflow.current_step else None,
                    "name": workflow.current_step.name if workflow.current_step else None
                } if workflow.current_step else None,
                "eta_seconds": workflow.eta_seconds
            }
        )

        await self.ws_manager.broadcast(event)

    def get_all_progress(self) -> List[Dict]:
        """Get progress for all workflows"""
        return [
            workflow.to_dict()
            for workflow in self.workflows.values()
        ]

    def cleanup_completed(self, max_age_seconds: int = 3600):
        """Remove completed workflows older than specified seconds"""
        cutoff = time.time() - max_age_seconds

        to_remove = [
            workflow_id for workflow_id, workflow in self.workflows.items()
            if workflow.completed_at and workflow.completed_at < cutoff
        ]

        for workflow_id in to_remove:
            del self.workflows[workflow_id]
            logger.info(f"[Progress] Cleaned up workflow: {workflow_id}")

        return len(to_remove)

# Singleton instance
_tracker: Optional[ProgressTracker] = None

def get_progress_tracker() -> ProgressTracker:
    """Get singleton progress tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = ProgressTracker()
    return _tracker

# Convenience functions for common operations
def create_workflow_progress(workflow_id: str, project_name: str) -> WorkflowProgress:
    """Create a new workflow progress tracker"""
    tracker = get_progress_tracker()
    return tracker.create_workflow(workflow_id, project_name)

def update_workflow_stage(workflow_id: str, stage: WorkflowStage):
    """Update workflow stage"""
    tracker = get_progress_tracker()
    tracker.set_stage(workflow_id, stage)

def start_step(workflow_id: str, phase: ProgressPhase):
    """Start a workflow step"""
    tracker = get_progress_tracker()
    tracker.start_step(workflow_id, phase)

def complete_step(workflow_id: str, phase: ProgressPhase):
    """Complete a workflow step"""
    tracker = get_progress_tracker()
    tracker.complete_step(workflow_id, phase)
