"""
AGCCE Tests - Configuración compartida (fixtures).
"""
import os
import sys
import json
import tempfile
from pathlib import Path

# Añadir scripts al path
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import pytest


@pytest.fixture
def temp_dir():
    """Crea un directorio temporal para tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_plan():
    """Plan JSON de ejemplo válido."""
    return {
        "plan_id": "PLAN-TEST001",
        "version": "1.0",
        "objective": "Test plan",
        "steps": [
            {
                "step_id": 1,
                "action": "analyze",
                "description": "Analyze code",
                "target": "test.py"
            }
        ],
        "metadata": {
            "created_at": "2026-01-18T00:00:00",
            "author": "test"
        }
    }


@pytest.fixture
def sample_plan_file(temp_dir, sample_plan):
    """Crea un archivo de plan temporal."""
    plan_path = temp_dir / "test_plan.json"
    with open(plan_path, 'w') as f:
        json.dump(sample_plan, f)
    return plan_path


@pytest.fixture
def project_root():
    """Retorna la raíz del proyecto."""
    return Path(__file__).parent.parent


@pytest.fixture
def scripts_dir(project_root):
    """Retorna el directorio de scripts."""
    return project_root / "scripts"
