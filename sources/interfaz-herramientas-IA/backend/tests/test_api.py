"""F1-P1 RED: API endpoints for health, events, quota, agents."""
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
def app_with_log(tmp_path: pathlib.Path) -> object:
    log = EventLog(tmp_path / "events.db")
    policy = QuotaPolicy(
        zai=ProviderPolicy(rolling_5h_budget=100, weekly_budget=1000, warning_threshold=0.2),
        chatgpt=ProviderPolicy(rolling_5h_budget=200, weekly_budget=2000, warning_threshold=0.2),
        claude=ProviderPolicy(rolling_5h_budget=150, weekly_budget=1500, warning_threshold=0.2),
    )
    governor = QuotaGovernor(policy)
    return create_app(event_log=log, quota_governor=governor)


@pytest.fixture
def client(app_with_log: object) -> AsyncClient:
    transport = ASGITransport(app=app_with_log)  # type: ignore[arg-type]
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


@pytest.mark.asyncio
async def test_list_events_empty(client: AsyncClient) -> None:
    resp = await client.get("/api/events")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_append_and_list_event(client: AsyncClient) -> None:
    payload = {
        "event_type": "task.created",
        "aggregate_id": "task_001",
        "payload": {"title": "Test task"},
        "idempotency_key": "idem_001",
    }
    resp = await client.post("/api/events", json=payload)
    assert resp.status_code == 201
    assert resp.json()["inserted"] is True

    list_resp = await client.get("/api/events")
    events = list_resp.json()
    assert len(events) == 1
    assert events[0]["event_type"] == "task.created"


@pytest.mark.asyncio
async def test_idempotent_append(client: AsyncClient) -> None:
    payload = {
        "event_type": "task.created",
        "aggregate_id": "task_002",
        "payload": {},
        "idempotency_key": "idem_dup",
    }
    r1 = await client.post("/api/events", json=payload)
    assert r1.json()["inserted"] is True
    r2 = await client.post("/api/events", json=payload)
    assert r2.json()["inserted"] is False


@pytest.mark.asyncio
async def test_quota_check(client: AsyncClient) -> None:
    resp = await client.get("/api/quota/zai")
    assert resp.status_code == 200
    body = resp.json()
    assert "rolling_5h" in body
    assert "weekly" in body
    assert body["rolling_5h"]["remaining"] == 100


@pytest.mark.asyncio
async def test_quota_record(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/quota/zai/consume",
        json={"units": 10, "source": "test"},
    )
    assert resp.status_code == 200

    check = await client.get("/api/quota/zai")
    assert check.json()["rolling_5h"]["remaining"] == 90


@pytest.mark.asyncio
async def test_agents_list(client: AsyncClient) -> None:
    resp = await client.get("/api/agents")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


@pytest.mark.asyncio
async def test_freeze_and_unfreeze(client: AsyncClient) -> None:
    freeze_resp = await client.post("/api/quota/freeze", json={"reason": "test freeze"})
    assert freeze_resp.status_code == 200

    check = await client.get("/api/quota/zai")
    assert check.json()["frozen"] is True

    unfreeze_resp = await client.post("/api/quota/unfreeze")
    assert unfreeze_resp.status_code == 200

    check2 = await client.get("/api/quota/zai")
    assert check2.json()["frozen"] is False
