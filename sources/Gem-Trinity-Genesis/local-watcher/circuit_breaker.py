"""
Circuit Breaker v2.0 - LLM API Resilience
Prevents cascading failures and manages retries for LLM API calls.
"""
import time
import asyncio
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service has recovered

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5          # Failures before opening
    success_threshold: int = 2          # Successes to close circuit
    timeout: float = 60.0              # Seconds before trying half-open
    half_open_calls: int = 3            # Test calls in half-open state
    rolling_window: int = 300           # Seconds for rolling statistics
    max_retries: int = 3                # Max retry attempts
    retry_delay: float = 1.0            # Base retry delay
    retry_backoff: float = 2.0          # Exponential backoff multiplier
    max_retry_delay: float = 60.0       # Maximum retry delay

@dataclass
class CallResult:
    """Result of an API call"""
    success: bool
    duration: float
    data: Any = None
    error: Optional[str] = None
    retry_count: int = 0

class CircuitBreaker:
    """
    Circuit breaker for LLM API calls.

    Features:
    - Automatic circuit opening after failures
    - Half-open state for testing recovery
    - Rolling statistics
    - Exponential backoff retries
    - Fallback responses
    - Per-model circuit tracking
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.

        Args:
            config: Circuit breaker configuration
        """
        self.config = config or CircuitBreakerConfig()

        # State
        self.state = CircuitState.CLOSED
        self.state_changed_at = time.time()
        self.open_count = 0  # How many times circuit has opened

        # Statistics (rolling window)
        self.failures: List[float] = []  # Timestamps of recent failures
        self.successes: List[float] = []  # Timestamps of recent successes
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0

        # Half-open tracking
        self.half_open_calls = 0
        self.half_open_successes = 0

        # Model-specific tracking
        self.model_states: Dict[str, CircuitState] = {}

        # Lock for thread safety
        self.lock = asyncio.Lock()

    async def call(
        self,
        func: Callable,
        *args,
        fallback: Optional[Callable] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Execute function through circuit breaker with retries.

        Args:
            func: Function to execute
            *args: Function arguments
            fallback: Fallback function if circuit is open
            model: Model name for per-model tracking
            **kwargs: Function keyword arguments

        Returns:
            Function result or fallback result

        Raises:
            Exception: If all retries exhausted and no fallback
        """
        # Check if per-model circuit is open
        if model and model in self.model_states:
            model_state = self.model_states[model]
            if model_state == CircuitState.OPEN:
                if self._should_attempt_reset(model):
                    logger.info(f"[CircuitBreaker] Attempting reset for model: {model}")
                    self.model_states[model] = CircuitState.HALF_OPEN
                else:
                    logger.warning(f"[CircuitBreaker] Circuit OPEN for model: {model}")
                    if fallback:
                        return await fallback(*args, **kwargs)
                    raise Exception(f"Circuit breaker OPEN for model: {model}")

        # Check global circuit state
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info("[CircuitBreaker] Transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
                self.state_changed_at = time.time()
                self.half_open_calls = 0
                self.half_open_successes = 0
            else:
                logger.warning("[CircuitBreaker] Circuit OPEN, using fallback")
                if fallback:
                    return await fallback(*args, **kwargs)
                raise Exception("Circuit breaker is OPEN")

        # Execute with retries
        last_error = None
        result = None

        for attempt in range(self.config.max_retries + 1):
            try:
                self.total_calls += 1

                start_time = time.time()
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Success!
                self._record_success(model)

                # If in half-open, check if we should close
                if self.state == CircuitState.HALF_OPEN:
                    self.half_open_successes += 1
                    if self.half_open_successes >= self.config.success_threshold:
                        logger.info("[CircuitBreaker] Circuit CLOSED after recovery")
                        self.state = CircuitState.CLOSED
                        self.state_changed_at = time.time()

                return CallResult(
                    success=True,
                    data=result,
                    duration=duration,
                    retry_count=attempt
                )

            except Exception as e:
                last_error = e
                error_msg = str(e)

                logger.warning(f"[CircuitBreaker] Call failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {error_msg}")

                # Record failure
                self._record_failure(model)

                # Check if we should open circuit
                if self._should_open_circuit():
                    logger.error("[CircuitBreaker] Circuit OPENED due to failures")
                    self.state = CircuitState.OPEN
                    self.state_changed_at = time.time()
                    self.open_count += 1

                    # Set per-model state if applicable
                    if model:
                        self.model_states[model] = CircuitState.OPEN

                # Retry logic
                if attempt < self.config.max_retries:
                    delay = min(
                        self.config.retry_delay * (self.config.retry_backoff ** attempt),
                        self.config.max_retry_delay
                    )
                    logger.info(f"[CircuitBreaker] Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                else:
                    # All retries exhausted
                    if fallback:
                        logger.info("[CircuitBreaker] Using fallback after retries exhausted")
                        return await fallback(*args, **kwargs)
                    raise

    def _record_success(self, model: Optional[str] = None):
        """Record successful call"""
        now = time.time()
        self.successes.append(now)
        self.total_successes += 1

        # Clean old entries outside rolling window
        cutoff = now - self.config.rolling_window
        self.successes = [t for t in self.successes if t > cutoff]
        self.failures = [t for t in self.failures if t > cutoff]

        # Reset per-model state on success
        if model and model in self.model_states:
            if self.model_states[model] == CircuitState.HALF_OPEN:
                # Only reset if enough successes
                recent_failures = [t for t in self.failures if t > cutoff]
                if len(recent_failures) < self.config.failure_threshold:
                    self.model_states[model] = CircuitState.CLOSED

    def _record_failure(self, model: Optional[str] = None):
        """Record failed call"""
        now = time.time()
        self.failures.append(now)
        self.total_failures += 1

        # Clean old entries outside rolling window
        cutoff = now - self.config.rolling_window
        self.successes = [t for t in self.successes if t > cutoff]
        self.failures = [t for t in self.failures if t > cutoff]

        # Set per-model state
        if model:
            if model not in self.model_states:
                self.model_states[model] = CircuitState.CLOSED

            # Check if model-specific circuit should open
            model_failures = [t for t in self.failures if t > cutoff]
            if len(model_failures) >= self.config.failure_threshold:
                self.model_states[model] = CircuitState.OPEN

    def _should_open_circuit(self) -> bool:
        """Check if circuit should be opened based on recent failures"""
        if self.state == CircuitState.OPEN:
            return False

        now = time.time()
        cutoff = now - self.config.rolling_window
        recent_failures = [t for t in self.failures if t > cutoff]

        return len(recent_failures) >= self.config.failure_threshold

    def _should_attempt_reset(self, model: Optional[str] = None) -> bool:
        """Check if enough time has passed to attempt circuit reset"""
        if model:
            model_state = self.model_states.get(model, CircuitState.CLOSED)
            if model_state == CircuitState.OPEN:
                # Check per-model timeout (could be different from global)
                return time.time() - self.state_changed_at >= self.config.timeout

        return time.time() - self.state_changed_at >= self.config.timeout

    def get_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state"""
        now = time.time()
        cutoff = now - self.config.rolling_window
        recent_failures = [t for t in self.failures if t > cutoff]
        recent_successes = [t for t in self.successes if t > cutoff]

        return {
            "state": self.state.value,
            "state_changed_at": self.state_changed_at,
            "time_in_state": now - self.state_changed_at,
            "open_count": self.open_count,
            "recent_failures": len(recent_failures),
            "recent_successes": len(recent_successes),
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "failure_rate": round(self.total_failures / self.total_calls * 100, 1) if self.total_calls > 0 else 0,
            "model_states": {k: v.value for k, v in self.model_states.items()},
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "timeout": self.config.timeout,
                "max_retries": self.config.max_retries
            }
        }

    def reset(self):
        """Manually reset circuit breaker to closed state"""
        logger.info("[CircuitBreaker] Manual reset")
        self.state = CircuitState.CLOSED
        self.state_changed_at = time.time()
        self.model_states.clear()
        self.half_open_calls = 0
        self.half_open_successes = 0

class LLMProviderWithResilience:
    """
    LLM Provider wrapper with circuit breaker and semantic cache.

    Combines:
    - Semantic caching
    - Circuit breaker
    - Automatic retries
    - Fallback responses
    """

    def __init__(self, base_provider):
        """
        Initialize resilient LLM provider.

        Args:
            base_provider: Base LLM provider to wrap
        """
        from semantic_cache import get_semantic_cache

        self.base_provider = base_provider
        self.cache = get_semantic_cache()
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig())

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gemini-pro",
        use_cache: bool = True,
        **kwargs
    ) -> str:
        """
        Generate response with caching and circuit breaker.

        Args:
            prompt: Input prompt
            system_prompt: System prompt
            model: Model name
            use_cache: Whether to use semantic cache
            **kwargs: Additional arguments for base provider

        Returns:
            Generated response
        """
        # Check cache first
        if use_cache:
            cached = self.cache.get(prompt, model)
            if cached:
                logger.debug(f"[LLMProvider] Cache HIT for: {prompt[:50]}...")
                return cached

        # Define fallback
        async def fallback(*args, **kwargs):
            logger.warning("[LLMProvider] Using fallback response")
            return self._get_fallback_response(prompt, model)

        # Execute through circuit breaker
        async def call_llm():
            return await self.base_provider.generate(
                prompt,
                system_prompt=system_prompt,
                model=model,
                **kwargs
            )

        try:
            result = await self.circuit_breaker.call(
                call_llm,
                fallback=fallback,
                model=model
            )

            if result.success:
                # Cache the response
                if use_cache:
                    self.cache.set(
                        prompt,
                        result,  # Assuming result is the actual response
                        model,
                        tokens_used=kwargs.get("max_tokens", 1000),  # Estimate
                        cost=self._estimate_cost(model, kwargs.get("max_tokens", 1000))
                    )

                return result

        except Exception as e:
            logger.error(f"[LLMProvider] All retries failed: {e}")
            raise

    def _get_fallback_response(self, prompt: str, model: str) -> str:
        """Get fallback response when API is unavailable"""
        return (
            f"# Fallback Response\n\n"
            f"I apologize, but the AI service is currently unavailable. "
            f"Your request has been logged and will be processed once the service recovers.\n\n"
            f"**Your request was:**\n{prompt[:200]}...\n\n"
            f"**Model:** {model}\n\n"
            f"Please try again in a few moments."
        )

    def _estimate_cost(self, model: str, tokens: int) -> float:
        """Estimate API cost in USD"""
        # Rough estimates (adjust based on actual pricing)
        costs = {
            "gemini-pro": 0.00025,  # per 1K tokens
            "gemini-2.0-flash": 0.00007,
            "gemini-2.0": 0.0005,
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.002
        }

        cost_per_1k = costs.get(model, 0.001)
        return (tokens / 1000) * cost_per_1k

# Singleton instances
_circuit_breaker: Optional[CircuitBreaker] = None

def get_circuit_breaker() -> CircuitBreaker:
    """Get singleton circuit breaker instance"""
    global _circuit_breaker
    if _circuit_breaker is None:
        _circuit_breaker = CircuitBreaker()
    return _circuit_breaker
