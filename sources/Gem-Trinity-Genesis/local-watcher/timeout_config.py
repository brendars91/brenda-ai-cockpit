"""
Timeout Configuration Module
Centralized timeout management for all operations.
"""
from typing import Dict, Optional
from enum import Enum
from dataclasses import dataclass

class OperationType(str, Enum):
    """Types of operations with different timeout requirements"""
    # Architect operations
    ARCHITECT_GENERATE = "architect_generate"
    ARCHITECT_PRD = "architect_prd"
    ARCHITECT_SPEC = "architect_spec"

    # Builder operations
    BUILDER_COMPILE = "builder_compile"
    BUILDER_AUDIT = "builder_audit"
    BUILDER_SKILL_GENETICS = "builder_skill_genetics"

    # Engine operations
    ENGINE_EXECUTE = "engine_execute"
    ENGINE_HEAL = "engine_heal"
    ENGINE_SIMULATION = "engine_simulation"

    # LLM operations
    LLM_GENERATE = "llm_generate"
    LLM_STREAM = "llm_stream"

    # System operations
    SYNC_MIRROR = "sync_mirror"
    GITHUB_SYNC = "github_sync"

@dataclass
class TimeoutConfig:
    """Configuration for a specific operation type"""
    operation: OperationType
    default_timeout: int  # seconds
    min_timeout: int
    max_timeout: int
    description: str

# Default timeout configurations
TIMEOUT_CONFIGS: Dict[OperationType, TimeoutConfig] = {
    # Architect: Quick operations, mostly LLM calls
    OperationType.ARCHITECT_GENERATE: TimeoutConfig(
        operation=OperationType.ARCHITECT_GENERATE,
        default_timeout=60,
        min_timeout=30,
        max_timeout=120,
        description="Generate context payload from use case"
    ),
    OperationType.ARCHITECT_PRD: TimeoutConfig(
        operation=OperationType.ARCHITECT_PRD,
        default_timeout=45,
        min_timeout=20,
        max_timeout=90,
        description="Generate PRD document"
    ),
    OperationType.ARCHITECT_SPEC: TimeoutConfig(
        operation=OperationType.ARCHITECT_SPEC,
        default_timeout=30,
        min_timeout=15,
        max_timeout=60,
        description="Generate spec contract"
    ),

    # Builder: Compilation can take longer
    OperationType.BUILDER_COMPILE: TimeoutConfig(
        operation=OperationType.BUILDER_COMPILE,
        default_timeout=120,
        min_timeout=60,
        max_timeout=300,
        description="Compile agent from payload"
    ),
    OperationType.BUILDER_AUDIT: TimeoutConfig(
        operation=OperationType.BUILDER_AUDIT,
        default_timeout=180,
        min_timeout=60,
        max_timeout=300,
        description="Run security audit on generated code"
    ),
    OperationType.BUILDER_SKILL_GENETICS: TimeoutConfig(
        operation=OperationType.BUILDER_SKILL_GENETICS,
        default_timeout=60,
        min_timeout=30,
        max_timeout=120,
        description="Generate skill code from genetics"
    ),

    # Engine: Execution times vary widely
    OperationType.ENGINE_EXECUTE: TimeoutConfig(
        operation=OperationType.ENGINE_EXECUTE,
        default_timeout=300,
        min_timeout=60,
        max_timeout=600,
        description="Execute agent task"
    ),
    OperationType.ENGINE_HEAL: TimeoutConfig(
        operation=OperationType.ENGINE_HEAL,
        default_timeout=120,
        min_timeout=30,
        max_timeout=180,
        description="Heal broken agent code"
    ),
    OperationType.ENGINE_SIMULATION: TimeoutConfig(
        operation=OperationType.ENGINE_SIMULATION,
        default_timeout=60,
        min_timeout=30,
        max_timeout=120,
        description="Run simulation mode"
    ),

    # LLM: API calls with retries
    OperationType.LLM_GENERATE: TimeoutConfig(
        operation=OperationType.LLM_GENERATE,
        default_timeout=60,
        min_timeout=15,
        max_timeout=120,
        description="LLM generation call"
    ),
    OperationType.LLM_STREAM: TimeoutConfig(
        operation=OperationType.LLM_STREAM,
        default_timeout=180,
        min_timeout=30,
        max_timeout=300,
        description="LLM streaming call"
    ),

    # System: Background operations
    OperationType.SYNC_MIRROR: TimeoutConfig(
        operation=OperationType.SYNC_MIRROR,
        default_timeout=30,
        min_timeout=10,
        max_timeout=60,
        description="Mirror sync operation"
    ),
    OperationType.GITHUB_SYNC: TimeoutConfig(
        operation=OperationType.GITHUB_SYNC,
        default_timeout=120,
        min_timeout=30,
        max_timeout=300,
        description="GitHub resource sync"
    ),
}

class TimeoutManager:
    """
    Centralized timeout manager with smart adjustments.

    Features:
    - Type-based timeout lookup
    - Dynamic adjustment based on history
    - Timeout validation
    """

    def __init__(self):
        self._history: Dict[OperationType, list] = {op: [] for op in OperationType}
        self._overrides: Dict[OperationType, int] = {}

    def get_timeout(self, operation: OperationType, custom: Optional[int] = None) -> int:
        """
        Get timeout for operation.

        Args:
            operation: Type of operation
            custom: Custom timeout in seconds (overrides default)

        Returns:
            Timeout in seconds

        Raises:
            ValueError: If timeout is out of valid range
        """
        config = TIMEOUT_CONFIGS.get(operation)
        if not config:
            raise ValueError(f"Unknown operation type: {operation}")

        # Use custom timeout if provided
        if custom is not None:
            timeout = custom
        # Use override if set
        elif operation in self._overrides:
            timeout = self._overrides[operation]
        # Use smart timeout based on history
        elif self._history[operation]:
            # Calculate 95th percentile of recent times + 20% buffer
            recent_times = sorted(self._history[operation][-10:])
            percentile_idx = int(len(recent_times) * 0.95)
            base_timeout = recent_times[percentile_idx] if recent_times else config.default_timeout
            timeout = min(int(base_timeout * 1.2), config.max_timeout)
        else:
            timeout = config.default_timeout

        # Validate timeout is within bounds
        if timeout < config.min_timeout:
            raise ValueError(f"Timeout {timeout}s is below minimum {config.min_timeout}s for {operation}")
        if timeout > config.max_timeout:
            raise ValueError(f"Timeout {timeout}s exceeds maximum {config.max_timeout}s for {operation}")

        return timeout

    def record_duration(self, operation: OperationType, duration: float):
        """Record actual operation duration for adaptive timeouts"""
        if operation in self._history:
            self._history[operation].append(duration)
            # Keep only last 50 records
            if len(self._history[operation]) > 50:
                self._history[operation] = self._history[operation][-50:]

    def set_override(self, operation: OperationType, timeout: int):
        """Set a custom timeout override for an operation"""
        config = TIMEOUT_CONFIGS.get(operation)
        if not config:
            raise ValueError(f"Unknown operation type: {operation}")

        if timeout < config.min_timeout or timeout > config.max_timeout:
            raise ValueError(f"Timeout {timeout}s is out of range [{config.min_timeout}, {config.max_timeout}]")

        self._overrides[operation] = timeout

    def clear_override(self, operation: OperationType):
        """Clear timeout override for an operation"""
        self._overrides.pop(operation, None)

    def get_stats(self, operation: Optional[OperationType] = None) -> Dict:
        """Get timeout statistics"""
        if operation:
            history = self._history.get(operation, [])
            if not history:
                return {"operation": operation, "samples": 0}

            return {
                "operation": operation,
                "samples": len(history),
                "avg": sum(history) / len(history),
                "min": min(history),
                "max": max(history),
                "p50": sorted(history)[len(history) // 2],
                "p95": sorted(history)[int(len(history) * 0.95)] if len(history) >= 20 else history[-1],
                "current_timeout": self.get_timeout(operation)
            }
        else:
            return {
                op: self.get_stats(op)
                for op in OperationType
                if self._history[op]
            }

# Singleton instance
_timeout_manager: Optional[TimeoutManager] = None

def get_timeout_manager() -> TimeoutManager:
    """Get singleton timeout manager instance"""
    global _timeout_manager
    if _timeout_manager is None:
        _timeout_manager = TimeoutManager()
    return _timeout_manager

def get_timeout(operation: OperationType, custom: Optional[int] = None) -> int:
    """Convenience function to get timeout for operation"""
    return get_timeout_manager().get_timeout(operation, custom)

def record_duration(operation: OperationType, duration: float):
    """Convenience function to record operation duration"""
    get_timeout_manager().record_duration(operation, duration)
