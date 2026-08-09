from cockpit_core.telemetry import InMemoryMetricSink, InMemorySpanExporter, redact_attributes


def test_redacts_secret_like_attributes() -> None:
    redacted = redact_attributes(
        {"api_key": "secret", "normal": "visible", "nested": {"token": "x"}}
    )

    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["normal"] == "visible"
    assert redacted["nested"] == {"token": "[REDACTED]"}


def test_in_memory_span_and_metric_sinks_capture_data() -> None:
    spans = InMemorySpanExporter()
    metrics = InMemoryMetricSink()

    spans.record("command.execute", {"provider": "zai"})
    metrics.increment("quota.units", 12, {"provider": "zai"})

    assert spans.spans[0].name == "command.execute"
    assert metrics.measurements[0].value == 12
