from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

JsonObject = dict[str, Any]


def _prefixed_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def _stable_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def stable_hash(value: object) -> str:
    return "sha256:" + hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


class CanonicalEvent(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["v1"] = "v1"
    event_id: str = Field(default_factory=lambda: _prefixed_id("evt"))
    event_type: str
    aggregate_id: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: JsonObject = Field(default_factory=dict)
    causation_id: str | None = None
    correlation_id: str | None = None
    idempotency_key: str | None = None


class CommandEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["v1"] = "v1"
    command_id: str = Field(default_factory=lambda: _prefixed_id("cmd"))
    command_type: str
    aggregate_id: str
    issued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: JsonObject = Field(default_factory=dict)
    idempotency_key: str


class ContextPacket(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["v1"] = "v1"
    packet_id: str = Field(default_factory=lambda: _prefixed_id("pkt"))
    task: str
    parent_goals: list[str]
    file_snapshot_hash: str
    promoted_prompts: list[str]
    permissions: list[str]
    enabled_mcps: list[str]
    output_contract: JsonObject
    content_hash: str

    @model_validator(mode="after")
    def validate_content_hash(self) -> ContextPacket:
        expected = self.compute_content_hash(
            task=self.task,
            parent_goals=self.parent_goals,
            file_snapshot_hash=self.file_snapshot_hash,
            promoted_prompts=self.promoted_prompts,
            permissions=self.permissions,
            enabled_mcps=self.enabled_mcps,
            output_contract=self.output_contract,
        )
        if self.content_hash != expected:
            raise ValueError("content_hash does not match packet content")
        return self

    @classmethod
    def compute_content_hash(
        cls,
        *,
        task: str,
        parent_goals: list[str],
        file_snapshot_hash: str,
        promoted_prompts: list[str],
        permissions: list[str],
        enabled_mcps: list[str],
        output_contract: JsonObject,
    ) -> str:
        return stable_hash(
            {
                "schema_version": "v1",
                "task": task,
                "parent_goals": parent_goals,
                "file_snapshot_hash": file_snapshot_hash,
                "promoted_prompts": promoted_prompts,
                "permissions": permissions,
                "enabled_mcps": enabled_mcps,
                "output_contract": output_contract,
            }
        )

    @classmethod
    def create(
        cls,
        *,
        task: str,
        parent_goals: list[str],
        file_snapshot_hash: str,
        promoted_prompts: list[str],
        permissions: list[str],
        enabled_mcps: list[str],
        output_contract: JsonObject,
    ) -> ContextPacket:
        content_hash = cls.compute_content_hash(
            task=task,
            parent_goals=parent_goals,
            file_snapshot_hash=file_snapshot_hash,
            promoted_prompts=promoted_prompts,
            permissions=permissions,
            enabled_mcps=enabled_mcps,
            output_contract=output_contract,
        )
        return cls(
            task=task,
            parent_goals=parent_goals,
            file_snapshot_hash=file_snapshot_hash,
            promoted_prompts=promoted_prompts,
            permissions=permissions,
            enabled_mcps=enabled_mcps,
            output_contract=output_contract,
            content_hash=content_hash,
        )
