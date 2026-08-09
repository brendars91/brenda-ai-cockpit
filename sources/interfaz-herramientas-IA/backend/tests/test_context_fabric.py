from datetime import UTC, datetime

from cockpit_core.context_fabric import EventLog, ProjectionEngine, replay_hash
from cockpit_core.contracts import CanonicalEvent


def make_event(
    event_type: str,
    aggregate_id: str,
    payload: dict[str, object],
    idem: str,
) -> CanonicalEvent:
    return CanonicalEvent(
        event_type=event_type,
        aggregate_id=aggregate_id,
        occurred_at=datetime(2026, 6, 7, tzinfo=UTC),
        payload=payload,
        idempotency_key=idem,
    )


def test_event_log_is_append_only_and_idempotent(tmp_path) -> None:
    log = EventLog(tmp_path / "canon.sqlite")
    event = make_event("task.created", "task-1", {"title": "Build"}, "idem-1")

    first = log.append_event(event)
    second = log.append_event(event)

    assert first.inserted is True
    assert second.inserted is False
    assert len(log.list_events()) == 1


def test_replay_is_deterministic(tmp_path) -> None:
    log = EventLog(tmp_path / "canon.sqlite")
    log.append_event(make_event("task.created", "task-1", {"title": "Build"}, "idem-1"))
    log.append_event(make_event("quota.freeze", "quota", {"reason": "test"}, "idem-2"))

    events = log.list_events()
    state_a = ProjectionEngine().replay(events)
    state_b = ProjectionEngine().replay(events)

    assert state_a == state_b
    assert replay_hash(state_a) == replay_hash(state_b)
    assert state_a["tasks"]["task-1"]["title"] == "Build"
    assert state_a["quota"]["frozen"] is True
