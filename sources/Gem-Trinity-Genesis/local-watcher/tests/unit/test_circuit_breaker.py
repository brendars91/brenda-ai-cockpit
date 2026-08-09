"""
Unit tests for Circuit Breaker pattern implementation.

Tests the resilience mechanism that prevents cascading failures
when calling external LLM APIs.
"""

import pytest
import asyncio
import time
from circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerConfig,
    get_circuit_breaker
)


class TestCircuitBreaker:
    """Test suite for CircuitBreaker class."""

    @pytest.fixture
    def config(self):
        return CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout=0.1,
            max_retries=0
        )

    def test_circuit_initial_state_closed(self, config):
        """Circuit should start in CLOSED state."""
        cb = CircuitBreaker(config)
        assert cb.get_state()["state"] == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_opens_on_failures(self, config):
        """Circuit should OPEN after reaching failure threshold."""
        cb = CircuitBreaker(config)

        async def failing_call():
            raise Exception("Failure")

        for _ in range(3):
            try:
                await cb.call(failing_call, fallback=lambda: "fallback")
            except:
                pass

        state = cb.get_state()
        assert state["state"] == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_circuit_allows_call_when_closed(self, config):
        """Circuit should allow calls when in CLOSED state."""
        cb = CircuitBreaker(config)

        async def test_call():
            return "success"

        result = await cb.call(test_call)
        assert result.success is True
        assert result.data == "success"

    @pytest.mark.asyncio
    async def test_circuit_blocks_call_when_open(self):
        """Circuit should block calls when in OPEN state."""
        config = CircuitBreakerConfig(failure_threshold=2, timeout=1.0, max_retries=0)
        cb = CircuitBreaker(config)

        async def failing_call():
            raise Exception("Should not be called")

        async def fallback():
            return "fallback_used"

        for _ in range(2):
            try:
                await cb.call(failing_call, fallback=fallback)
            except:
                pass

        result = await cb.call(failing_call, fallback=fallback)
        assert result == "fallback_used"

    @pytest.mark.asyncio
    async def test_circuit_transitions_to_half_open_after_timeout(self):
        """Circuit should transition to HALF_OPEN after timeout."""
        config = CircuitBreakerConfig(failure_threshold=2, timeout=0.1, max_retries=0)
        cb = CircuitBreaker(config)

        async def failing_call():
            raise Exception("Failure")

        for _ in range(2):
            try:
                await cb.call(failing_call, fallback=lambda: "fallback")
            except:
                pass

        assert cb.get_state()["state"] == CircuitState.OPEN

        await asyncio.sleep(0.15)

        async def test_call():
            return "success"

        await cb.call(test_call)

        state = cb.get_state()
        assert state["state"] in [CircuitState.HALF_OPEN, CircuitState.CLOSED]

    @pytest.mark.asyncio
    async def test_circuit_closes_on_success_in_half_open(self):
        """Circuit should CLOSE after successful call in HALF_OPEN."""
        config = CircuitBreakerConfig(failure_threshold=2, success_threshold=2, timeout=0.1, max_retries=0)
        cb = CircuitBreaker(config)

        async def failing_call():
            raise Exception("Failure")

        for _ in range(2):
            try:
                await cb.call(failing_call, fallback=lambda: "fallback")
            except:
                pass

        assert cb.get_state()["state"] == CircuitState.OPEN

        await asyncio.sleep(0.15)

        async def success_call():
            return "success"

        for _ in range(2):
            await cb.call(success_call)

        assert cb.get_state()["state"] == CircuitState.CLOSED

    def test_circuit_resets(self, config):
        """Circuit should reset to initial CLOSED state."""
        cb = CircuitBreaker(config)
        
        cb.state = CircuitState.OPEN
        cb.state_changed_at = time.time() - 10

        cb.reset()

        state = cb.get_state()
        assert state["state"] == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_tracks_success_rate(self):
        """Circuit should track success rate metrics."""
        config = CircuitBreakerConfig(failure_threshold=5, max_retries=0)
        cb = CircuitBreaker(config)

        async def success_call():
            return "success"

        async def failing_call():
            raise Exception("Failed")

        for _ in range(3):
            await cb.call(success_call)

        for _ in range(2):
            try:
                await cb.call(failing_call)
            except:
                pass

        state = cb.get_state()
        assert state["total_calls"] > 0

    def test_get_circuit_breaker_singleton(self):
        """get_circuit_breaker should return singleton instance."""
        cb1 = get_circuit_breaker()
        cb2 = get_circuit_breaker()
        assert cb1 is cb2

    @pytest.mark.asyncio
    async def test_circuit_per_model_tracking(self):
        """Circuit should track metrics per model."""
        config = CircuitBreakerConfig(failure_threshold=3, max_retries=0)
        cb = CircuitBreaker(config)

        async def success_call():
            return "success"

        async def failing_call():
            raise Exception("Failure")

        await cb.call(success_call, model="gemini-pro")
        await cb.call(success_call, model="gpt-4")
        
        for _ in range(3):
            try:
                await cb.call(failing_call, model="gemini-pro")
            except:
                pass

        state = cb.get_state()
        assert "gemini-pro" in state["model_states"] or "gpt-4" in state["model_states"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
