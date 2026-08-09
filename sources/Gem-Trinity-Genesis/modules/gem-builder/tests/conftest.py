import pytest
import sys
from pathlib import Path

# Agregar src al path para importar módulos
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

@pytest.fixture
def minimal_spec():
    """Retorna un Use Case Spec mínimo válido"""
    return {
        "use_case_id": "test-smoke-v1",
        "goal": "Smoke test for the compiler pipeline",
        "data_sources": [{"type": "file", "access": "read"}],
        "actions": [{"type": "read"}],
        "constraints": {
            "latency_ms": 1000,
            "cost_tier": "low"
        },
        "security": {
            "hitl_required": "auto"
        }
    }

@pytest.fixture
def valid_bundle():
    """Retorna un Gem Bundle mínimo válido"""
    return {
        "bundle_meta": {
            "use_case_id": "test-smoke-v1",
            "version": "1.0.0",
            "risk_score": 10
        },
        "model_routing": {
            "default_model": "gemini-flash"
        },
        "policies": {
            "knowledge_states": ["HECHO_VERIFICADO", "FALTAN_DATOS"],
            "model_armor_enabled": False
        },
        "system_prompt": {
            "text": "You are a test agent."
        },
         "tools": {
            "contracts": []
        }
    }
