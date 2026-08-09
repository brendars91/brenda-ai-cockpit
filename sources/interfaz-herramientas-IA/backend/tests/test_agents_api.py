"""F1-P3: Test agents/run endpoint."""
from __future__ import annotations

import pathlib

import pytest
from httpx import ASGITransport, AsyncClient

from cockpit_core.context_fabric import EventLog
from cockpit_core.quota_governor import (
    ProviderPolicy,
    QuotaGovernor,
    QuotaPolicy,
)
from cockpit_web.app import create_app


@pytest.fixture
def components(tmp_path: pathlib.Path) -> tuple:
    log = EventLog(tmp_path / "events.db")
    policy = QuotaPolicy(
        zai=ProviderPolicy(rolling_5h_budget=100, weekly_budget=1000, warning_threshold=0.2),
        chatgpt=ProviderPolicy(rolling_5h_budget=200, weekly_budget=2000, warning_threshold=0.2),
        claude=ProviderPolicy(rolling_5h_budget=150, weekly_budget=1500, warning_threshold=0.2),
    )
    governor = QuotaGovernor(policy)
    app = create_app(event_log=log, quota_governor=governor)
    return app, log


@pytest.mark.anyio
async def test_agents_list_with_health(components: tuple) -> None:
    app, _log = components
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/agents")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["id"] == "hermes-local"
        assert "version" in data[0]


@pytest.mark.anyio
async def test_agents_run_creates_events(components: tuple) -> None:
    app, log = components
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/agents/run",
            json={"query": "--version", "max_turns": 1},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "run_id" in data
        assert isinstance(data["success"], bool)

        # Verify events were created
        events = log.list_events()
        types = [e.event_type for e in events]
        assert "agent.task.submitted" in types
        assert ("agent.task.completed" in types) or ("agent.task.failed" in types)
