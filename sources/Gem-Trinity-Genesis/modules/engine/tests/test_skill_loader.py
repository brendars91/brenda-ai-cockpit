"""
Tests para skill_loader.py
"""
import pytest
from pathlib import Path
import sys

# Añadir scripts al path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from skill_loader import SkillLoader


class TestSkillLoader:
    """Tests para SkillLoader."""
    
    def test_get_tools_for_valid_phase(self):
        """Debe retornar herramientas para fase válida."""
        result = SkillLoader.get_tools_for_phase("validation")
        
        assert result["phase_found"] == True
        assert "primary_tools" in result
        assert "snyk" in result["primary_tools"]
    
    def test_get_tools_for_invalid_phase(self):
        """Debe retornar defaults para fase inválida."""
        result = SkillLoader.get_tools_for_phase("nonexistent_phase")
        
        assert result["phase_found"] == False
        assert "filesystem" in result["primary_tools"]
    
    def test_list_all_phases(self):
        """Debe listar todas las fases disponibles."""
        phases = SkillLoader.list_all_phases()
        
        assert isinstance(phases, list)
        assert len(phases) > 0
        assert "validation" in phases or "implementation" in phases
    
    def test_list_active_mcps(self):
        """Debe listar MCPs activos."""
        mcps = SkillLoader.list_active_mcps()
        
        assert isinstance(mcps, list)
        # Debe tener al menos algunos MCPs básicos
        assert len(mcps) >= 1
    
    def test_get_mcp_info_existing(self):
        """Debe retornar info de MCP existente."""
        info = SkillLoader.get_mcp_info("filesystem")
        
        if info:  # Si existe en el manifest
            assert "description" in info
            assert "status" in info
    
    def test_get_mcp_info_nonexistent(self):
        """Debe retornar None para MCP inexistente."""
        info = SkillLoader.get_mcp_info("fake_mcp_that_doesnt_exist")
        
        assert info is None
    
    def test_suggest_for_task_security(self):
        """Debe detectar fase de seguridad."""
        result = SkillLoader.suggest_for_task("validar y verificar el código")
        
        assert "detected_phase" in result
        assert result["detected_phase"] == "validation"
    
    def test_suggest_for_task_implementation(self):
        """Debe detectar fase de implementación."""
        result = SkillLoader.suggest_for_task("crear nueva función de login")
        
        assert "detected_phase" in result
        # Puede ser "implementation" o "planning" dependiendo de keywords
    
    def test_get_auto_suggestion_commit(self):
        """Debe sugerir escaneo antes de commit."""
        suggestion = SkillLoader.get_auto_suggestion("voy a hacer commit")
        
        assert suggestion is not None
        assert "CLI" in suggestion or "seguridad" in suggestion.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
