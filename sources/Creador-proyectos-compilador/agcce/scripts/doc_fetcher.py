#!/usr/bin/env python3
"""
AGCCE Doc Fetcher
Obtiene documentacion relevante de librerias usando context7.

Uso: python doc_fetcher.py --library "nombre_libreria" --query "pregunta"
"""

import subprocess
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Importar utilidades comunes
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info, make_header
except ImportError:
    class Colors:
        GREEN = RED = YELLOW = BLUE = CYAN = RESET = BOLD = ''
    class Symbols:
        CHECK = '[OK]'
        CROSS = '[X]'
        WARN = '[!]'
        INFO = '[i]'
    def log_pass(msg): print(f"[OK] {msg}")
    def log_fail(msg): print(f"[X] {msg}")
    def log_info(msg): print(f"[i] {msg}")
    def make_header(title, width=60): return f"\n{'=' * width}\n  {title}\n{'=' * width}\n"


# Cache de documentacion
DOC_CACHE_FILE = ".doc_cache.json"


def load_doc_cache() -> Dict[str, Any]:
    """Carga cache de documentacion."""
    if os.path.exists(DOC_CACHE_FILE):
        with open(DOC_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"entries": {}}


def save_doc_cache(cache: Dict[str, Any]) -> None:
    """Guarda cache de documentacion."""
    with open(DOC_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)


def get_cache_key(library: str, query: str) -> str:
    """Genera clave de cache."""
    return f"{library}::{query[:50]}"


def fetch_docs(library: str, query: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    Obtiene documentacion de una libreria.
    
    Nota: Esta funcion prepara la solicitud.
    La obtencion real se hace via context7 MCP.
    """
    print(make_header("AGCCE Doc Fetcher v1.0"))
    
    print(f"{Colors.CYAN}Libreria:{Colors.RESET} {library}")
    print(f"{Colors.CYAN}Query:{Colors.RESET} {query}")
    print()
    
    cache = load_doc_cache()
    cache_key = get_cache_key(library, query)
    
    # Verificar cache
    if use_cache and cache_key in cache.get("entries", {}):
        entry = cache["entries"][cache_key]
        log_info("Usando documentacion en cache")
        print(f"  Cacheado: {entry.get('cached_at')}")
        return entry.get("result", {})
    
    # Preparar instrucciones para el agente
    print(f"{Colors.BOLD}Instrucciones para obtener docs:{Colors.RESET}")
    print()
    
    instructions = {
        "step_1": {
            "description": "Resolver ID de libreria",
            "tool": "mcp_context7_resolve-library-id",
            "params": {
                "libraryName": library,
                "query": query
            }
        },
        "step_2": {
            "description": "Obtener documentacion",
            "tool": "mcp_context7_query-docs",
            "params": {
                "libraryId": "<usar ID del paso anterior>",
                "query": query
            }
        }
    }
    
    print(f"{Colors.BLUE}1. Resolver libreria:{Colors.RESET}")
    print(f"   Tool: mcp_context7_resolve-library-id")
    print(f"   libraryName: {library}")
    print(f"   query: {query}")
    print()
    print(f"{Colors.BLUE}2. Consultar docs:{Colors.RESET}")
    print(f"   Tool: mcp_context7_query-docs")
    print(f"   libraryId: (del paso 1)")
    print(f"   query: {query}")
    print()
    
    result = {
        "library": library,
        "query": query,
        "status": "pending",
        "instructions": instructions,
        "note": "Ejecutar via context7 MCP para obtener documentacion real"
    }
    
    log_info("Instrucciones generadas")
    print(f"\n{Colors.YELLOW}[!] Ejecuta las instrucciones via MCP para obtener docs reales{Colors.RESET}\n")
    
    return result


def cache_result(library: str, query: str, result: Dict) -> None:
    """Guarda resultado en cache."""
    cache = load_doc_cache()
    cache_key = get_cache_key(library, query)
    
    cache["entries"][cache_key] = {
        "library": library,
        "query": query,
        "result": result,
        "cached_at": datetime.now().isoformat()
    }
    
    save_doc_cache(cache)
    log_pass("Resultado cacheado")


def list_common_libraries() -> List[str]:
    """Lista librerias comunes para referencia."""
    return [
        "python",
        "fastapi",
        "flask",
        "django",
        "requests",
        "pytest",
        "numpy",
        "pandas",
        "react",
        "next.js",
        "typescript",
        "node.js",
        "express",
        "mongodb",
        "postgresql"
    ]


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} --library \"nombre\" --query \"pregunta\"")
        print(f"\nOpciones:")
        print(f"  --library \"lib\"   Nombre de la libreria")
        print(f"  --query \"texto\"   Pregunta sobre la libreria")
        print(f"  --list            Lista librerias comunes")
        print(f"  --no-cache        No usar cache")
        sys.exit(1)
    
    if "--list" in sys.argv:
        print("Librerias comunes:")
        for lib in list_common_libraries():
            print(f"  - {lib}")
        sys.exit(0)
    
    # Parsear argumentos
    library = None
    query = None
    use_cache = "--no-cache" not in sys.argv
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--library" and i + 1 < len(sys.argv):
            library = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--query" and i + 1 < len(sys.argv):
            query = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    if not library or not query:
        print(f"{Colors.RED}Error: --library y --query son requeridos{Colors.RESET}")
        sys.exit(1)
    
    fetch_docs(library, query, use_cache)


if __name__ == '__main__':
    main()
