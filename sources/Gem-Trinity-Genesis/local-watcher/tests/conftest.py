"""
Pytest configuration for local-watcher tests.

This file contains shared fixtures and configuration
for all test modules.
"""

import pytest
import sys
from pathlib import Path

# Add local-watcher directory to Python path for imports
local_watcher_dir = Path(__file__).parent.parent
sys.path.insert(0, str(local_watcher_dir))


@pytest.fixture
def sample_circuit_config():
    """Sample circuit breaker configuration for testing."""
    return {
        "failure_threshold": 3,
        "success_threshold": 2,
        "timeout": 1.0,
        "rolling_window": 300
    }


@pytest.fixture
def sample_cache_config():
    """Sample cache configuration for testing."""
    return {
        "max_entries": 100,
        "default_ttl": 3600,
        "similarity_threshold": 0.85
    }


@pytest.fixture
def sample_prompts():
    """Sample prompts for testing semantic cache."""
    return {
        "simple": "What is Python?",
        "complex": "How do I implement a REST API with authentication using FastAPI?",
        "code": "Write a function to calculate fibonacci numbers"
    }
