"""F1-P2 RED: WebSocket bridge — backend emits events to connected clients."""
from __future__ import annotations

import pathlib

import pytest
from starlette.testclient import TestClient

from cockpit_core.context_fabric import EventLog
from cockpit_core.quota_governor import (
    ProviderPolicy,
    QuotaGovernor,
    QuotaPolicy,
)
from cockpit_web.app import create_app


@pytest.fixture
def app_components(tmp_path: pathlib.Path) -> tuple:
    log = EventLog(tmp_path / "events.db")
    policy = QuotaPolicy(
        zai=ProviderPolicy(rolling_5h_budget=100, weekly_budget=1000, warning_threshold=0.2),
        chatgpt=ProviderPolicy(rolling_5h_budget=200, weekly_budget=2000, warning_threshold=0.2),
        claude=ProviderPolicy(rolling_5h_budget=150, weekly_budget=1500, warning_threshold=0.2),
    )
    governor = QuotaGovernor(policy)
    app = create_app(event_log=log, quota_governor=governor)
    return app, log


def test_ws_receives_event_after_append(app_components: tuple) -> None:
    app, _log = app_components
    client = TestClient(app)

    with client.websocket_connect("/api/ws/events") as ws:
        # Append an event via REST
        resp = client.post(
            "/api/events",
            json={
                "event_type": "task.created",
                "aggregate_id": "task_ws_001",
                "payload": {"title": "WS test"},
                "idempotency_key": "idem_ws_001",
            },
        )
        assert resp.status_code == 201

        # The WS client should receive the broadcast
        data = ws.receive_json(mode="text")
        assert data["event_type"] == "task.created"
        assert data["aggregate_id"] == "task_ws_001"


def test_ws_multiple_clients_receive_broadcast(app_components: tuple) -> None:
    app, _log = app_components
    client = TestClient(app)

    with (
        client.websocket_connect("/api/ws/events") as ws1,
        client.websocket_connect("/api/ws/events") as ws2,
    ):
        client.post(
            "/api/events",
            json={
                "event_type": "agent.spawned",
                "aggregate_id": "agent_001",
                "payload": {"name": "hermes"},
                "idempotency_key": "idem_multi_001",
            },
        )

        d1 = ws1.receive_json(mode="text")
        d2 = ws2.receive_json(mode="text")
        assert d1["event_type"] == "agent.spawned"
        assert d2["event_type"] == "agent.spawned"
