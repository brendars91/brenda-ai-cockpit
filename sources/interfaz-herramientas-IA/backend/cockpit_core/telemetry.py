from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SECRET_MARKERS = ("key", "token", "secret", "password", "credential")


def redact_attributes(attributes: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in attributes.items():
        if any(marker in key.lower() for marker in SECRET_MARKERS):
            redacted[key] = "[REDACTED]"
        elif isinstance(value, dict):
            redacted[key] = redact_attributes(value)
        else:
            redacted[key] = value
    return redacted


@dataclass(frozen=True)
class SpanRecord:
    name: str
    attributes: dict[str, Any]


@dataclass(frozen=True)
class MetricRecord:
    name: str
    value: int | float
    attributes: dict[str, Any]


class InMemorySpanExporter:
    def __init__(self) -> None:
        self.spans: list[SpanRecord] = []

    def record(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        self.spans.append(SpanRecord(name=name, attributes=redact_attributes(attributes or {})))


class InMemoryMetricSink:
    def __init__(self) -> None:
        self.measurements: list[MetricRecord] = []

    def increment(
        self,
        name: str,
        value: int | float = 1,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        self.measurements.append(
            MetricRecord(name=name, value=value, attributes=redact_attributes(attributes or {}))
        )
