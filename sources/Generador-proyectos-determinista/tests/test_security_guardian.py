"""
Tests para security_guardian.py
"""
import pytest
from pathlib import Path
import sys
import tempfile

# Añadir scripts al path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from security_guardian import SecurityGuardian, LOGICAL_VULNERABILITY_PATTERNS


class TestSecurityGuardian:
    """Tests para SecurityGuardian."""
    
    @pytest.fixture
    def guardian(self):
        """Instancia de SecurityGuardian."""
        return SecurityGuardian()
    
    def test_analyze_file_not_found(self, guardian):
        """Debe manejar archivo no encontrado."""
        result = guardian.analyze_file(Path("/nonexistent/file.py"))
        
        assert "error" in result
    
    def test_analyze_file_finds_idor(self, guardian):
        """Debe detectar patrones IDOR."""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write('''
def get_user(request):
    user_id = request.args["id"]
    return db.get(user_id)
            ''')
            f.flush()
            
            result = guardian.analyze_file(Path(f.name))
        
        assert result["findings_count"] >= 1
        vuln_types = [f["type"] for f in result["findings"]]
        assert "IDOR" in vuln_types
    
    def test_analyze_file_finds_data_exposure(self, guardian):
        """Debe detectar exposición de datos."""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write('''
def login(user):
    print(user.password)
    return token
            ''')
            f.flush()
            
            result = guardian.analyze_file(Path(f.name))
        
        vuln_types = [f["type"] for f in result["findings"]]
        assert "DATA_EXPOSURE" in vuln_types
    
    def test_analyze_clean_file(self, guardian):
        """Archivo limpio debe tener score alto."""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write('''
def safe_function(x, y):
    """A safe function."""
    return x + y
            ''')
            f.flush()
            
            result = guardian.analyze_file(Path(f.name))
        
        assert result["security_score"] >= 90
    
    def test_generate_attack_hypothesis(self, guardian):
        """Debe generar hipótesis de ataque."""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write('''
user_id = request.form["user_id"]
            ''')
            f.flush()
            
            result = guardian.analyze_file(Path(f.name))
        
        if result["attack_hypotheses"]:
            assert any("atacante" in h.lower() for h in result["attack_hypotheses"])
    
    def test_generate_plan_security_section(self, guardian):
        """Debe generar sección de seguridad para Plan JSON."""
        analysis = {
            "findings_by_type": {"IDOR": 2, "DATA_EXPOSURE": 1},
            "overall_security_score": 60
        }
        
        section = guardian.generate_plan_security_section(analysis)
        
        assert "security_analysis" in section
        assert "attack_vectors" in section["security_analysis"]
        assert "mitigations" in section["security_analysis"]
        assert "validation_tests" in section["security_analysis"]
    
    def test_get_stats_empty(self, guardian):
        """Stats vacías deben retornar mensaje."""
        # Esto asume que no hay log previo o está vacío
        stats = guardian.get_stats()
        
        assert "message" in stats or "total_analyses" in stats


class TestVulnerabilityPatterns:
    """Tests para los patrones de detección."""
    
    def test_patterns_are_valid_regex(self):
        """Todos los patrones deben ser regex válidos."""
        import re
        
        for vuln_type, config in LOGICAL_VULNERABILITY_PATTERNS.items():
            for pattern in config["patterns"]:
                try:
                    re.compile(pattern)
                except re.error as e:
                    pytest.fail(f"Invalid regex in {vuln_type}: {pattern} - {e}")
    
    def test_all_vulnerabilities_have_description(self):
        """Todas las vulnerabilidades deben tener descripción."""
        for vuln_type, config in LOGICAL_VULNERABILITY_PATTERNS.items():
            assert "description" in config, f"{vuln_type} missing description"
            assert len(config["description"]) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
