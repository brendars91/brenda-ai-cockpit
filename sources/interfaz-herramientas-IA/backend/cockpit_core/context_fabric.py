from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .contracts import CanonicalEvent, stable_hash


@dataclass(frozen=True)
class AppendResult:
    inserted: bool
    event_id: str


class EventLog:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def append_event(self, event: CanonicalEvent) -> AppendResult:
        with self._connect() as conn:
            if event.idempotency_key is not None:
                existing = conn.execute(
                    "SELECT event_id FROM canonical_events WHERE idempotency_key = ?",
                    (event.idempotency_key,),
                ).fetchone()
                if existing is not None:
                    return AppendResult(inserted=False, event_id=str(existing[0]))
            conn.execute(
                """
                INSERT INTO canonical_events (
                  event_id, schema_version, event_type, aggregate_id, occurred_at,
                  payload_json, causation_id, correlation_id, idempotency_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.schema_version,
                    event.event_type,
                    event.aggregate_id,
                    event.occurred_at.isoformat(),
                    json.dumps(event.payload, sort_keys=True, separators=(",", ":")),
                    event.causation_id,
                    event.correlation_id,
                    event.idempotency_key,
                ),
            )
            return AppendResult(inserted=True, event_id=event.event_id)

    def list_events(self) -> list[CanonicalEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT event_id, schema_version, event_type, aggregate_id, occurred_at,
                       payload_json, causation_id, correlation_id, idempotency_key
                FROM canonical_events
                ORDER BY sequence ASC
                """
            ).fetchall()
        return [
            CanonicalEvent(
                event_id=str(row[0]),
                schema_version=row[1],
                event_type=str(row[2]),
                aggregate_id=str(row[3]),
                occurred_at=datetime.fromisoformat(str(row[4])),
                payload=json.loads(str(row[5])),
                causation_id=row[6],
                correlation_id=row[7],
                idempotency_key=row[8],
            )
            for row in rows
        ]

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS canonical_events (
                  sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                  event_id TEXT NOT NULL UNIQUE,
                  schema_version TEXT NOT NULL,
                  event_type TEXT NOT NULL,
                  aggregate_id TEXT NOT NULL,
                  occurred_at TEXT NOT NULL,
                  payload_json TEXT NOT NULL,
                  causation_id TEXT,
                  correlation_id TEXT,
                  idempotency_key TEXT UNIQUE
                )
                """
            )


class ProjectionEngine:
    def replay(self, events: list[CanonicalEvent]) -> dict[str, Any]:
        state: dict[str, Any] = {"tasks": {}, "quota": {"frozen": False}}
        for event in events:
            if event.event_type == "task.created":
                state["tasks"][event.aggregate_id] = dict(event.payload)
            elif event.event_type == "quota.freeze":
                state["quota"] = {"frozen": True, **event.payload}
        return state


def replay_hash(state: dict[str, Any]) -> str:
    return stable_hash(state)
