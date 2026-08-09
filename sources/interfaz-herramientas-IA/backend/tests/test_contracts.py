from datetime import UTC, datetime

from cockpit_core.contracts import CanonicalEvent, CommandEnvelope, ContextPacket


def test_canonical_event_requires_versioned_contract() -> None:
    event = CanonicalEvent(
        event_type="task.created",
        aggregate_id="task-1",
        occurred_at=datetime(2026, 6, 7, tzinfo=UTC),
        payload={"title": "Hire first engineer"},
        idempotency_key="idem-1",
    )

    assert event.schema_version == "v1"
    assert event.event_id.startswith("evt_")
    assert event.payload["title"] == "Hire first engineer"


def test_command_envelope_requires_idempotency_key() -> None:
    command = CommandEnvelope(
        command_type="task.create",
        aggregate_id="task-1",
        issued_at=datetime(2026, 6, 7, tzinfo=UTC),
        payload={"title": "Build cockpit"},
        idempotency_key="task.create:task-1",
    )

    assert command.schema_version == "v1"
    assert command.command_id.startswith("cmd_")
    assert command.idempotency_key == "task.create:task-1"


def test_context_packet_content_hash_is_stable() -> None:
    packet_a = ContextPacket.create(
        task="Implement quota governor",
        parent_goals=["Phase 0"],
        file_snapshot_hash="sha256:abc",
        promoted_prompts=["Use strict gates"],
        permissions=["read", "write-workspace"],
        enabled_mcps=["paperclip"],
        output_contract={"format": "diff+tests"},
    )
    packet_b = ContextPacket.create(
        task="Implement quota governor",
        parent_goals=["Phase 0"],
        file_snapshot_hash="sha256:abc",
        promoted_prompts=["Use strict gates"],
        permissions=["read", "write-workspace"],
        enabled_mcps=["paperclip"],
        output_contract={"format": "diff+tests"},
    )

    assert packet_a.content_hash == packet_b.content_hash
    assert packet_a.packet_id.startswith("pkt_")
