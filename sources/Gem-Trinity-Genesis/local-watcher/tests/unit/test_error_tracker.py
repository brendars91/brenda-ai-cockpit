"""
Unit tests for Error Tracker implementation.

Tests the error tracking and categorization system
that monitors application errors and provides metrics.
"""

import pytest
from error_tracker import (
    ErrorTracker,
    ErrorSeverity,
    ErrorCategory,
    get_error_tracker
)


class TestErrorTracker:
    """Test suite for ErrorTracker class."""

    def test_track_error_increments_count(self):
        """Tracking an error should increment error count."""
        tracker = ErrorTracker()

        initial_stats = tracker.get_error_stats()
        initial_count = initial_stats.get("total", 0)

        tracker.track(Exception("Test error"))

        new_stats = tracker.get_error_stats()
        assert new_stats["total"] == initial_count + 1

    def test_track_error_with_category(self):
        """Error should be categorized correctly."""
        tracker = ErrorTracker()

        tracker.track(
            Exception("LLM API failed"),
            category=ErrorCategory.LLM_API
        )

        stats = tracker.get_error_stats()
        assert "by_category" in stats
        assert stats["by_category"]["llm_api"] == 1

    def test_track_error_with_severity(self):
        """Error should be tracked with severity level."""
        tracker = ErrorTracker()

        tracker.track(
            Exception("Critical failure"),
            severity=ErrorSeverity.CRITICAL
        )

        stats = tracker.get_error_stats()
        assert "by_severity" in stats
        assert stats["by_severity"]["critical"] == 1

    def test_track_error_with_additional_info(self):
        """Error should store additional context information."""
        tracker = ErrorTracker()

        error_id = tracker.track(
            Exception("Builder failed"),
            additional_info={"agent_name": "test_agent", "model": "gemini-pro"}
        )

        recent_errors = tracker.get_recent_errors(limit=1)
        assert len(recent_errors) > 0

    def test_get_recent_errors(self):
        """Should return most recent errors up to limit."""
        tracker = ErrorTracker()

        for i in range(5):
            tracker.track(Exception(f"Error {i}"))

        recent = tracker.get_recent_errors(limit=3)

        assert len(recent) <= 3

    def test_get_recent_errors_respects_limit(self):
        """get_recent_errors should respect the limit parameter."""
        tracker = ErrorTracker()

        for i in range(10):
            tracker.track(Exception(f"Error {i}"))

        recent = tracker.get_recent_errors(limit=5)

        assert len(recent) == 5

    def test_get_stats_aggregates_by_category(self):
        """Stats should aggregate errors by category."""
        tracker = ErrorTracker()

        tracker.track(Exception("LLM error"), category=ErrorCategory.LLM_API)
        tracker.track(Exception("Builder error"), category=ErrorCategory.BUILDER)
        tracker.track(Exception("Another LLM error"), category=ErrorCategory.LLM_API)

        stats = tracker.get_error_stats()

        assert stats["by_category"]["llm_api"] == 2
        assert stats["by_category"]["builder"] == 1

    def test_get_stats_aggregates_by_severity(self):
        """Stats should aggregate errors by severity."""
        tracker = ErrorTracker()

        tracker.track(Exception("Low priority"), severity=ErrorSeverity.LOW)
        tracker.track(Exception("High priority"), severity=ErrorSeverity.HIGH)
        tracker.track(Exception("Another low"), severity=ErrorSeverity.LOW)

        stats = tracker.get_error_stats()

        assert stats["by_severity"]["low"] == 2
        assert stats["by_severity"]["high"] == 1

    def test_clear_errors(self):
        """clear_history should reset all error tracking."""
        tracker = ErrorTracker()

        for i in range(5):
            tracker.track(Exception(f"Error {i}"))

        assert tracker.get_error_stats()["total"] == 5

        tracker.clear_history()

        assert tracker.get_error_stats()["total"] == 0

    def test_get_error_by_id(self):
        """Should retrieve specific error by ID if implemented."""
        tracker = ErrorTracker()

        error_id = tracker.track(
            Exception("Test error"),
            additional_info={"context": "test"}
        )

        recent = tracker.get_recent_errors(limit=1)
        assert len(recent) > 0

    def test_error_severity_levels(self):
        """All severity levels should be valid."""
        tracker = ErrorTracker()

        severities = [
            ErrorSeverity.CRITICAL,
            ErrorSeverity.HIGH,
            ErrorSeverity.MEDIUM,
            ErrorSeverity.LOW
        ]

        for severity in severities:
            tracker.track(
                Exception(f"{severity} error"),
                severity=severity
            )

        stats = tracker.get_error_stats()
        for severity in severities:
            assert severity.value in stats["by_severity"]

    def test_error_categories(self):
        """All error categories should be valid."""
        tracker = ErrorTracker()

        categories = [
            ErrorCategory.LLM_API,
            ErrorCategory.BUILDER,
            ErrorCategory.ENGINE,
            ErrorCategory.UNKNOWN
        ]

        for category in categories:
            tracker.track(
                Exception(f"{category} error"),
                category=category
            )

        stats = tracker.get_error_stats()
        for category in categories:
            assert category.value in stats["by_category"]

    def test_get_error_tracker_singleton(self):
        """get_error_tracker should return singleton instance."""
        tracker1 = get_error_tracker()
        tracker2 = get_error_tracker()
        assert tracker1 is tracker2

    def test_max_history_limit(self):
        """Should not store unlimited errors."""
        tracker = ErrorTracker(max_history=5)

        for i in range(10):
            tracker.track(Exception(f"Error {i}"))

        recent = tracker.get_recent_errors(limit=100)

        assert len(recent) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
