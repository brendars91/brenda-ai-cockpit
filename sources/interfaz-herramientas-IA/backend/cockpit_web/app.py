"""F1-P2 GREEN: WebSocket bridge — broadcasts events to connected clients."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from cockpit_core.adapters.hermes import HermesAdapter
from cockpit_core.context_fabric import EventLog
from cockpit_core.contracts import CanonicalEvent
from cockpit_core.quota_governor import ProviderName, QuotaGovernor


class AppendEventRequest(BaseModel):
    event_type: str
    aggregate_id: str
    payload: dict[str, Any] = {}
    idempotency_key: str | None = None


class ConsumeRequest(BaseModel):
    units: int
    source: str


class FreezeRequest(BaseModel):
    reason: str


class RunAgentRequest(BaseModel):
    query: str
    model: str | None = None
    provider: str | None = None
    toolsets: list[str] | None = None
    skills: list[str] | None = None
    max_turns: int | None = None


class _EventBroadcaster:
    """Fan-out: maintains a set of WebSocket connections and broadcasts events."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.remove(ws)

    async def broadcast(self, event_dict: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_json(event_dict)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self._connections.remove(ws)


def create_app(
    *,
    event_log: EventLog,
    quota_governor: QuotaGovernor,
    version: str = "0.0.1",
) -> FastAPI:
    app = FastAPI(title="Cockpit API", version=version)
    broadcaster = _EventBroadcaster()

    # --- WebSocket: live event stream ---
    @app.websocket("/api/ws/events")
    async def ws_events(ws: WebSocket) -> None:
        await broadcaster.connect(ws)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            broadcaster.disconnect(ws)

    # --- Health ---
    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "version": version}

    # --- Events ---
    @app.get("/api/events")
    def list_events() -> list[dict[str, Any]]:
        events = event_log.list_events()
        return [e.model_dump(mode="json") for e in events]

    @app.post("/api/events", status_code=201)
    async def append_event(body: AppendEventRequest) -> dict[str, Any]:
        event = CanonicalEvent(
            event_type=body.event_type,
            aggregate_id=body.aggregate_id,
            payload=body.payload,
            idempotency_key=body.idempotency_key,
        )
        result = event_log.append_event(event)
        event_dict = event.model_dump(mode="json")
        await broadcaster.broadcast(event_dict)
        return {"inserted": result.inserted, "event_id": result.event_id}

    # --- Quota ---
    @app.get("/api/quota/{provider}")
    def quota_status(provider: ProviderName) -> dict[str, Any]:
        rolling = quota_governor.window(provider=provider, window_type="rolling_5h")
        weekly = quota_governor.window(provider=provider, window_type="weekly")
        return {
            "provider": provider,
            "frozen": quota_governor.is_frozen(),
            "rolling_5h": {
                "budget": rolling.budget,
                "consumed": rolling.consumed,
                "remaining": rolling.remaining,
                "window_start": rolling.window_start.isoformat(),
                "window_end": rolling.window_end.isoformat(),
            },
            "weekly": {
                "budget": weekly.budget,
                "consumed": weekly.consumed,
                "remaining": weekly.remaining,
                "window_start": weekly.window_start.isoformat(),
                "window_end": weekly.window_end.isoformat(),
            },
        }

    @app.post("/api/quota/{provider}/consume")
    def consume_quota(provider: ProviderName, body: ConsumeRequest) -> dict[str, Any]:
        quota_governor.record_consumption(
            provider=provider,
            units=body.units,
            source=body.source,
        )
        return {"status": "recorded"}

    @app.post("/api/quota/freeze")
    def freeze(body: FreezeRequest) -> dict[str, Any]:
        quota_governor.freeze(reason=body.reason)
        return {"frozen": True}

    @app.post("/api/quota/unfreeze")
    def unfreeze() -> dict[str, Any]:
        quota_governor.unfreeze()
        return {"frozen": False}

    # --- Agents ---
    hermes_adapter = HermesAdapter()

    @app.get("/api/agents")
    def list_agents() -> list[dict[str, Any]]:
        health_info = hermes_adapter.health_check()
        return [
            {
                "id": "hermes-local",
                "name": "Hermes Local",
                "status": "available" if health_info["available"] else "offline",
                "adapter": "hermes",
                "version": health_info.get("version", ""),
            }
        ]

    @app.post("/api/agents/run")
    async def run_agent(body: RunAgentRequest) -> dict[str, Any]:
        import uuid

        run_id = str(uuid.uuid4())[:8]

        # Record the task submission event
        submit_event = CanonicalEvent(
            event_type="agent.task.submitted",
            aggregate_id=f"run_{run_id}",
            payload={"query": body.query[:200]},
        )
        event_log.append_event(submit_event)
        await broadcaster.broadcast(submit_event.model_dump(mode="json"))

        result = hermes_adapter.run_query(
            query=body.query,
            model=body.model,
            provider=body.provider,
            toolsets=body.toolsets,
            skills=body.skills,
            max_turns=body.max_turns,
            run_id=run_id,
        )

        # Record the completion event
        complete_event = CanonicalEvent(
            event_type="agent.task.completed" if result.success else "agent.task.failed",
            aggregate_id=f"run_{run_id}",
            payload={
                "exit_code": result.exit_code,
                "output_length": len(result.stdout),
                "error": result.stderr[:200] if result.stderr else None,
            },
        )
        event_log.append_event(complete_event)
        await broadcaster.broadcast(complete_event.model_dump(mode="json"))

        return {
            "run_id": run_id,
            "success": result.success,
            "exit_code": result.exit_code,
            "output": result.stdout[:5000],
            "error": result.stderr[:1000] if result.stderr else None,
        }

    return app
