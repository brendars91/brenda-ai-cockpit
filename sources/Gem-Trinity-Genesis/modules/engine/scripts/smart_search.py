#!/usr/bin/env python3
"""
AGCCE Smart Search v1.0
Búsqueda semántica con refinamiento automático.

Implementa el patrón "Auto-Evolving Search":
- Si la búsqueda falla (score bajo), refina la query
- Máximo 3 intentos antes de pedir ayuda
- Usa patrones de refinamiento inteligentes

Uso:
  from smart_search import SmartSearch
  results = SmartSearch.search("autenticación de usuarios")
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Importar utilidades
try:
    from common import Colors, log_pass, log_fail, log_warn, log_info
except ImportError:
    def log_pass(msg): print(f"[OK] {msg}")
    def log_fail(msg): print(f"[X] {msg}")
    def log_warn(msg): print(f"[!] {msg}")
    def log_info(msg): print(f"[i] {msg}")


# Umbral mínimo de relevancia
MIN_RELEVANCE_SCORE = 0.5
MAX_REFINEMENT_ATTEMPTS = 3


class QueryRefiner:
    """Refinador de consultas de búsqueda."""
    
    # Patrones de refinamiento
    REFINEMENT_STRATEGIES = [
        {
            "name": "expand_synonyms",
            "description": "Añadir sinónimos comunes",
            "transforms": {
                "auth": ["authentication", "login", "session"],
                "user": ["usuario", "account", "profile"],
                "api": ["endpoint", "rest", "http"],
                "db": ["database", "sql", "conexión"],
                "config": ["configuration", "settings", "options"]
            }
        },
        {
            "name": "simplify",
            "description": "Simplificar a palabras clave",
            "action": "extract_keywords"
        },
        {
            "name": "broaden",
            "description": "Ampliar el alcance",
            "action": "remove_specifics"
        }
    ]
    
    @classmethod
    def refine(cls, query: str, attempt: int, partial_results: List = None) -> str:
        """
        Refina una consulta basándose en el intento actual.
        
        Args:
            query: Consulta original
            attempt: Número de intento (1, 2, 3)
            partial_results: Resultados parciales del intento anterior
        
        Returns:
            Consulta refinada
        """
        if attempt == 1:
            # Primer intento: expandir con sinónimos
            return cls._expand_synonyms(query)
        elif attempt == 2:
            # Segundo intento: simplificar
            return cls._simplify(query)
        elif attempt == 3:
            # Tercer intento: ampliar
            return cls._broaden(query, partial_results)
        
        return query
    
    @classmethod
    def _expand_synonyms(cls, query: str) -> str:
        """Expande query con sinónimos."""
        words = query.lower().split()
        expanded = []
        
        synonyms = cls.REFINEMENT_STRATEGIES[0]["transforms"]
        
        for word in words:
            expanded.append(word)
            for key, values in synonyms.items():
                if key in word:
                    expanded.extend(values[:2])  # Añadir 2 sinónimos max
                    break
        
        return " ".join(set(expanded))
    
    @classmethod
    def _simplify(cls, query: str) -> str:
        """Simplifica a palabras clave principales."""
        # Eliminar palabras comunes
        stopwords = {"de", "la", "el", "en", "para", "con", "que", "the", "and", "or", "a", "an"}
        words = [w for w in query.lower().split() if w not in stopwords and len(w) > 2]
        
        # Mantener solo las 3 palabras más largas (probablemente más significativas)
        words.sort(key=len, reverse=True)
        return " ".join(words[:3])
    
    @classmethod
    def _broaden(cls, query: str, partial_results: List = None) -> str:
        """Amplía el alcance de la búsqueda."""
        # Si hay resultados parciales, extraer términos de ellos
        if partial_results:
            # Extraer paths comunes de resultados
            paths = [r.get("path", "") for r in partial_results[:3] if r.get("path")]
            if paths:
                # Extraer componentes de paths
                components = set()
                for p in paths:
                    parts = Path(p).parts
                    components.update([part for part in parts if len(part) > 3])
                
                if components:
                    return query + " " + " ".join(list(components)[:2])
        
        # Si no hay resultados, buscar términos más genéricos
        return query.split()[0] if query.split() else query


class SmartSearch:
    """Búsqueda semántica con refinamiento automático."""
    
    @classmethod
    def search(
        cls,
        query: str,
        max_results: int = 5,
        auto_refine: bool = True
    ) -> Dict:
        """
        Realiza búsqueda con refinamiento automático.
        
        Args:
            query: Consulta de búsqueda
            max_results: Número máximo de resultados
            auto_refine: Si debe refinar automáticamente
        
        Returns:
            Dict con resultados, intentos y sugerencias
        """
        results = {
            "query": query,
            "attempts": [],
            "final_results": [],
            "success": False,
            "user_help_needed": False
        }
        
        current_query = query
        
        for attempt in range(MAX_REFINEMENT_ATTEMPTS + 1):
            # Ejecutar búsqueda
            search_results = cls._execute_search(current_query, max_results)
            
            results["attempts"].append({
                "attempt": attempt,
                "query": current_query,
                "results_count": len(search_results),
                "avg_score": cls._calculate_avg_score(search_results)
            })
            
            # Verificar si los resultados son buenos
            if cls._results_are_good(search_results):
                results["final_results"] = search_results
                results["success"] = True
                log_pass(f"Búsqueda exitosa en intento {attempt}")
                break
            
            # Si no hay refinamiento automático o es el último intento
            if not auto_refine or attempt >= MAX_REFINEMENT_ATTEMPTS:
                results["final_results"] = search_results
                results["user_help_needed"] = True
                results["suggestions"] = cls._generate_suggestions(query, search_results)
                log_warn(f"Búsqueda no satisfactoria después de {attempt + 1} intentos")
                break
            
            # Refinar query para próximo intento
            current_query = QueryRefiner.refine(current_query, attempt + 1, search_results)
            log_info(f"Refinando query: '{current_query}'")
        
        return results
    
    @classmethod
    def _execute_search(cls, query: str, max_results: int) -> List[Dict]:
        """
        Ejecuta la búsqueda real.
        En producción, esto llamaría a smart-coding-mcp.
        """
        # TODO: Integrar con smart-coding-mcp real
        # Por ahora, simular resultados
        
        # Intentar búsqueda local en archivos
        results = []
        project_root = Path(__file__).parent.parent
        
        # Buscar en archivos Python
        for py_file in project_root.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                content_lower = content.lower()
                query_words = query.lower().split()
                
                # Calcular score simple basado en coincidencias
                matches = sum(1 for word in query_words if word in content_lower)
                if matches > 0:
                    score = matches / len(query_words)
                    results.append({
                        "path": str(py_file.relative_to(project_root)),
                        "score": score,
                        "matches": matches,
                        "preview": content[:200].replace('\n', ' ')[:100]
                    })
            except:
                continue
        
        # Ordenar por score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    @classmethod
    def _results_are_good(cls, results: List[Dict]) -> bool:
        """Determina si los resultados son satisfactorios."""
        if not results:
            return False
        
        # Al menos un resultado con score alto
        high_score_results = [r for r in results if r.get("score", 0) >= MIN_RELEVANCE_SCORE]
        return len(high_score_results) >= 1
    
    @classmethod
    def _calculate_avg_score(cls, results: List[Dict]) -> float:
        """Calcula score promedio de resultados."""
        if not results:
            return 0.0
        
        scores = [r.get("score", 0) for r in results]
        return sum(scores) / len(scores)
    
    @classmethod
    def _generate_suggestions(cls, original_query: str, results: List[Dict]) -> List[str]:
        """Genera sugerencias cuando la búsqueda falla."""
        suggestions = [
            f"Intenta buscar términos más específicos del código",
            f"Verifica que el índice RAG esté actualizado (CLI → Opción 1)",
            f"Busca por nombre de función o clase en lugar de descripción"
        ]
        
        if results:
            paths = [r.get("path", "") for r in results[:3]]
            if paths:
                suggestions.append(f"Resultados parciales encontrados en: {', '.join(paths)}")
        
        return suggestions


def main():
    """CLI para Smart Search."""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python smart_search.py <consulta>")
        print("\nEjemplo:")
        print("  python smart_search.py 'autenticación de usuarios'")
        return
    
    query = " ".join(sys.argv[1:])
    
    print(f"\n{'='*60}")
    print(f"  AGCCE Smart Search v1.0")
    print(f"{'='*60}")
    print(f"\nBuscando: '{query}'")
    
    results = SmartSearch.search(query)
    
    print(f"\n--- Resultados ---")
    print(f"Éxito: {'✅' if results['success'] else '❌'}")
    print(f"Intentos: {len(results['attempts'])}")
    
    if results["final_results"]:
        print(f"\nArchivos encontrados:")
        for r in results["final_results"]:
            print(f"  [{r['score']:.2f}] {r['path']}")
    
    if results.get("user_help_needed"):
        print(f"\n⚠️ Búsqueda no satisfactoria. Sugerencias:")
        for sug in results.get("suggestions", []):
            print(f"  - {sug}")


if __name__ == '__main__':
    main()
