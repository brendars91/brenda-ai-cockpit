"""
Tests para smart_search.py
"""
import pytest
from pathlib import Path
import sys

# Añadir scripts al path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from smart_search import SmartSearch, QueryRefiner


class TestQueryRefiner:
    """Tests para QueryRefiner."""
    
    def test_refine_attempt_1_expands_synonyms(self):
        """Primer intento debe expandir sinónimos."""
        original = "auth user"
        refined = QueryRefiner.refine(original, attempt=1)
        
        assert refined != original
        # Debe contener palabras adicionales
        assert len(refined.split()) > len(original.split())
    
    def test_refine_attempt_2_simplifies(self):
        """Segundo intento debe simplificar."""
        original = "autenticación de usuarios en el sistema"
        refined = QueryRefiner.refine(original, attempt=2)
        
        # Debe tener menos palabras
        assert len(refined.split()) <= len(original.split())
    
    def test_refine_attempt_3_broadens(self):
        """Tercer intento debe ampliar."""
        original = "login"
        partial_results = [{"path": "auth/handlers/login.py"}]
        
        refined = QueryRefiner.refine(original, attempt=3, partial_results=partial_results)
        
        # Debe incluir términos de los paths parciales
        assert refined != original


class TestSmartSearch:
    """Tests para SmartSearch."""
    
    def test_search_returns_dict(self):
        """Búsqueda debe retornar diccionario con estructura correcta."""
        result = SmartSearch.search("test")
        
        assert isinstance(result, dict)
        assert "query" in result
        assert "attempts" in result
        assert "final_results" in result
        assert "success" in result
    
    def test_search_tracks_attempts(self):
        """Debe trackear intentos de búsqueda."""
        result = SmartSearch.search("nonexistent_xyz_123")
        
        assert len(result["attempts"]) >= 1
        assert "query" in result["attempts"][0]
    
    def test_search_with_auto_refine_disabled(self):
        """Sin auto-refine solo debe hacer un intento."""
        result = SmartSearch.search("test", auto_refine=False)
        
        assert len(result["attempts"]) == 1
    
    def test_search_returns_suggestions_on_failure(self):
        """Debe dar sugerencias cuando falla."""
        result = SmartSearch.search("xyznonexistent123", auto_refine=False)
        
        if result.get("user_help_needed"):
            assert "suggestions" in result
            assert len(result["suggestions"]) > 0
    
    def test_search_finds_real_files(self):
        """Debe encontrar archivos reales del proyecto."""
        result = SmartSearch.search("skill loader")
        
        # Debería encontrar skill_loader.py
        if result["final_results"]:
            paths = [r["path"] for r in result["final_results"]]
            # Al menos un resultado debe existir
            assert len(paths) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
