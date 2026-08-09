import pytest
from cli import cmd_compile
from verifier_gate import VerifierGate
import argparse
import json
import os

def test_verifier_gate_smoke(valid_bundle):
    """Prueba básica del VerifierGate con un bundle válido"""
    verifier = VerifierGate()
    result = verifier.verify(valid_bundle, risk_score=10)
    
    assert result.passed is True, f"Verifier falló: {result.errors}"
    assert "schema" in result.checks_passed

def test_compile_pipeline_smoke(minimal_spec, tmp_path):
    """Smoke Test del pipeline completo de compilación (CLI)"""
    # 1. Crear archivo spec temporal
    spec_file = tmp_path / "smoke_spec.json"
    with open(spec_file, "w", encoding="utf-8") as f:
        json.dump(minimal_spec, f)
    
    output_bundle = tmp_path / "smoke_bundle.json"
    
    # 2. Mockear argumentos
    args = argparse.Namespace(
        spec=str(spec_file),
        output=str(output_bundle),
        dry_run=False,
        verbose=True
    )
    
    # 3. Ejecutar comando compile (debe terminar sin error)
    try:
        cmd_compile(args)
    except SystemExit as e:
        pytest.fail(f"CLI terminó con exit code: {e}")
    
    # 4. Verificar output
    assert output_bundle.exists()
    
    with open(output_bundle, "r", encoding="utf-8") as f:
        bundle = json.load(f)
        
    assert bundle["bundle_meta"]["use_case_id"] == "test-smoke-v1"
    assert bundle["verifier"]["verified"] is True
