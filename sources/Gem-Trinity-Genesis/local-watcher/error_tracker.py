"""
Error Tracker v2.0 - Centralized Error Logging
Tracks and categorizes all errors with context for debugging.
"""
import time
import traceback
import json
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from enum import Enum
import logging
import threading
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class ErrorSeverity(str, Enum):
    """Severity levels for errors"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ErrorCategory(str, Enum):
    """Categories of errors for filtering"""
    LLM_API = "llm_api"
    BUILDER = "builder"
    ENGINE = "engine"
    ARCHITECT = "architect"
    WEBSOCKET = "websocket"
    DATABASE = "database"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    VALIDATION = "validation"
    UNKNOWN = "unknown"

@dataclass
class ErrorContext:
    """Context information for an error"""
    timestamp: float
    severity: ErrorSeverity
    category: ErrorCategory
    component: str
    message: str
    error_type: str
    traceback: Optional[str] = None
    user_id: Optional[str] = None
    workflow_id: Optional[str] = None
    request_data: Optional[Dict] = None
    additional_info: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp,
            "iso_timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "severity": self.severity.value,
            "category": self.category.value,
            "component": self.component,
            "message": self.message,
            "error_type": self.error_type,
            "user_id": self.user_id,
            "workflow_id": self.workflow_id,
            "request_data": self.request_data,
            "additional_info": self.additional_info
        }

class ErrorTracker:
    """
    Centralized error tracking for Gem-Trinity Genesis.

    Features:
    - Error logging with full context
    - Severity categorization
    - Statistics tracking
    - Persistent error history
    - Per-category filtering
    - Aggregation and reporting
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize error tracker.

        Args:
            max_history: Maximum number of errors to keep in memory
        """
        self.max_history = max_history
        self.errors: List[ErrorContext] = []
        self.stats: Dict[str, Dict[str, int]] = {
            "total": 0,
            "by_severity": {s: 0 for s in ErrorSeverity},
            "by_category": {c: 0 for c in ErrorCategory},
            "by_component": {}
        }

        self.lock = threading.Lock()

        # Error history file
        self.error_file = Path("artifacts/error_history.jsonl")
        self.error_file.parent.mkdir(parents=True, exist_ok=True)

    def track(
        self,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        component: str = "unknown",
        user_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        request_data: Optional[Dict] = None,
        additional_info: Optional[Dict] = None
    ) -> str:
        """
        Track an error with full context.

        Args:
            error: The exception that occurred
            severity: Error severity level
            category: Error category
            component: Component/service name
            user_id: Associated user ID
            workflow_id: Associated workflow ID
            request_data: Request data that caused the error
            additional_info: Additional context information

        Returns:
            Error ID for reference
        """
        error_id = f"ERR_{int(time.time() * 1000)}"

        # Get error details
        error_type = type(error).__name__
        message = str(error)

        # Get traceback
        tb_str = None
        if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            tb_str = "".join(traceback.format_exception(type(error), error, error.__traceback__))

        # Create error context
        context = ErrorContext(
            timestamp=time.time(),
            severity=severity,
            category=category,
            component=component,
            message=message,
            error_type=error_type,
            traceback=tb_str,
            user_id=user_id,
            workflow_id=workflow_id,
            request_data=request_data,
            additional_info=additional_info or {}
        )

        # Add to history
        with self.lock:
            self.errors.append(context)
            self.stats["total"] += 1
            self.stats["by_severity"][severity.value] += 1
            self.stats["by_category"][category.value] += 1
            self.stats["by_component"][component] = \
                self.stats["by_component"].get(component, 0) + 1

            # Keep only recent errors
            if len(self.errors) > self.max_history:
                self.errors.pop(0)

        # Log error
        log_msg = f"[{severity.value.upper()}] {component}: {message}"
        if severity == ErrorSeverity.CRITICAL:
            logger.critical(log_msg)
        elif severity == ErrorSeverity.HIGH:
            logger.error(log_msg)
        elif severity == ErrorSeverity.MEDIUM:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        # Save to file
        self._save_to_file(context)

        return error_id

    def track_llm_error(
        self,
        error: Exception,
        model: str,
        prompt: str,
        tokens_used: int = 0,
        user_id: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> str:
        """Track LLM API error with specific context"""
        return self.track(
            error=error,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.LLM_API,
            component=f"llm_provider_{model}",
            user_id=user_id,
            workflow_id=workflow_id,
            request_data={"prompt_length": len(prompt), "tokens_used": tokens_used},
            additional_info={"model": model, "prompt_preview": prompt[:200]}
        )

    def track_builder_error(
        self,
        error: Exception,
        build_id: str,
        stage: str,
        user_id: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> str:
        """Track builder error with specific context"""
        return self.track(
            error=error,
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.BUILDER,
            component="builder_service",
            user_id=user_id,
            workflow_id=workflow_id,
            request_data={"build_id": build_id, "stage": stage},
            additional_info={"build_id": build_id, "stage": stage}
        )

    def track_engine_error(
        self,
        error: Exception,
        execution_id: str,
        agent_id: str,
        task: str,
        user_id: Optional[str] = None,
        workflow_id: Optional[str] = None
    ) -> str:
        """Track engine error with specific context"""
        return self.track(
            error=error,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.ENGINE,
            component="engine_service",
            user_id=user_id,
            workflow_id=workflow_id,
            request_data={"execution_id": execution_id, "agent_id": agent_id, "task_length": len(task)},
            additional_info={"execution_id": execution_id, "agent_id": agent_id, "task": task[:100]}
        )

    def track_websocket_error(
        self,
        error: Exception,
        client_id: str,
        user_id: Optional[str] = None
    ) -> str:
        """Track WebSocket error with specific context"""
        return self.track(
            error=error,
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.WEBSOCKET,
            component="websocket_manager",
            user_id=user_id,
            request_data={"client_id": client_id},
            additional_info={"client_id": client_id}
        )

    def get_recent_errors(
        self,
        limit: int = 50,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        component: Optional[str] = None
    ) -> List[Dict]:
        """
        Get recent errors with optional filtering.

        Args:
            limit: Maximum number of errors to return
            severity: Filter by severity
            category: Filter by category
            component: Filter by component name

        Returns:
            List of error dictionaries
        """
        with self.lock:
            filtered = self.errors.copy()

            # Apply filters
            if severity:
                filtered = [e for e in filtered if e.severity == severity]
            if category:
                filtered = [e for e in filtered if e.category == category]
            if component:
                filtered = [e for e in filtered if e.component == component]

            # Sort by timestamp (newest first) and limit
            filtered.sort(key=lambda e: e.timestamp, reverse=True)
            result = filtered[:limit]

        return [e.to_dict() for e in result]

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        with self.lock:
            return {
                "total": self.stats["total"],
                "recent_errors": len(self.errors),
                "by_severity": {k.value: v for k, v in self.stats["by_severity"].items()},
                "by_category": {k.value: v for k, v in self.stats["by_category"].items()},
                "top_components": dict(sorted(
                    self.stats["by_component"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10])
            }

    def get_error_rate(
        self,
        window_seconds: int = 300,
        component: Optional[str] = None
    ) -> float:
        """
        Calculate error rate in a time window.

        Args:
            window_seconds: Time window in seconds
            component: Optional component filter

        Returns:
            Errors per second in the window
        """
        cutoff = time.time() - window_seconds

        with self.lock:
            errors = self.errors
            if component:
                errors = [e for e in errors if e.component == component]

            recent = [e for e in errors if e.timestamp > cutoff]
            return len(recent) / window_seconds if window_seconds > 0 else 0

    def clear_history(self, before_timestamp: Optional[float] = None):
        """Clear error history before a timestamp"""
        with self.lock:
            if before_timestamp:
                self.errors = [e for e in self.errors if e.timestamp < before_timestamp]
            else:
                self.errors.clear()

        # Reset stats
        self.stats = {
            "total": 0,
            "by_severity": {s: 0 for s in ErrorSeverity},
            "by_category": {c: 0 for c in ErrorCategory},
            "by_component": {}
        }

        logger.info(f"[ErrorTracker] Cleared {'all' if not before_timestamp else 'old'} errors")

    def _save_to_file(self, context: ErrorContext):
        """Save error to history file"""
        try:
            entry = json.dumps(context.to_dict())
            self.error_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.error_file, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception as e:
            logger.error(f"[ErrorTracker] Failed to save error to file: {e}")

# Singleton instance
_tracker: Optional[ErrorTracker] = None

def get_error_tracker() -> ErrorTracker:
    """Get singleton error tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = ErrorTracker()
    return _tracker

# Convenience functions
def track_error(error: Exception, **kwargs) -> str:
    """Convenience function to track an error"""
    tracker = get_error_tracker()
    return tracker.track(error=error, **kwargs)

def track_llm_error(error: Exception, model: str, prompt: str, **kwargs) -> str:
    """Convenience function to track LLM error"""
    tracker = get_error_tracker()
    return tracker.track_llm_error(error=error, model=model, prompt=prompt, **kwargs)

def get_error_stats() -> Dict[str, Any]:
    """Get error statistics"""
    tracker = get_error_tracker()
    return tracker.get_error_stats()
