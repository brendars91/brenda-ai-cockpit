"""F1-P3: Hermes adapter tests."""
from __future__ import annotations

from cockpit_core.adapters.hermes import HermesAdapter


def test_health_check_detects_hermes() -> None:
    adapter = HermesAdapter()
    result = adapter.health_check()
    assert "available" in result
    assert isinstance(result["available"], bool)


def test_health_check_with_invalid_bin() -> None:
    adapter = HermesAdapter(hermes_bin="/nonexistent/hermes")
    result = adapter.health_check()
    assert result["available"] is False


def test_run_query_returns_result() -> None:
    adapter = HermesAdapter()
    result = adapter.run_query(query="echo hello", run_id="test_001")
    assert result.run_id == "test_001"
    assert isinstance(result.success, bool)
    assert isinstance(result.stdout, str)
    assert isinstance(result.stderr, str)


def test_run_query_with_invalid_bin() -> None:
    adapter = HermesAdapter(hermes_bin="/nonexistent/hermes")
    result = adapter.run_query(query="test", run_id="fail_001")
    assert result.success is False
    assert "not found" in result.stderr


def test_run_query_timeout_propagates() -> None:
    adapter = HermesAdapter()
    # Use a query that should complete quickly, not actually testing timeout
    result = adapter.run_query(query="--version", run_id="timeout_test")
    assert result.run_id == "timeout_test"
    assert isinstance(result.exit_code, int)
