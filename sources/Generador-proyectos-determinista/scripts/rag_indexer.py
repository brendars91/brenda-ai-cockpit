#!/usr/bin/env python3
"""
AGCCE RAG Indexer v2.0 - Incremental Indexing
Indexa el codebase usando smart-coding-mcp para busqueda semantica.

MEJORA CRITICA: Incremental Indexing
- Detecta cambios via git diff
- Solo re-indexa archivos modificados
- Mantiene grounding actual sin penalizar latencia

Uso: python rag_indexer.py [--reindex | --status | --incremental]
"""

import subprocess
import sys
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional, Set

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
    def log_warn(msg): print(f"[!] {msg}")
    def make_header(title, width=60): return f"\n{'=' * width}\n  {title}\n{'=' * width}\n"


# Archivo de estado del indice
INDEX_STATE_FILE = ".rag_index_state.json"
FILE_HASHES_FILE = ".rag_file_hashes.json"


def load_index_state() -> Dict[str, Any]:
    """Carga estado del indice."""
    if os.path.exists(INDEX_STATE_FILE):
        with open(INDEX_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_indexed": None,
        "files_indexed": 0,
        "workspace": None,
        "status": "not_indexed"
    }


def save_index_state(state: Dict[str, Any]) -> None:
    """Guarda estado del indice."""
    with open(INDEX_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)


def load_file_hashes() -> Dict[str, str]:
    """Carga hashes de archivos indexados."""
    if os.path.exists(FILE_HASHES_FILE):
        with open(FILE_HASHES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_file_hashes(hashes: Dict[str, str]) -> None:
    """Guarda hashes de archivos."""
    with open(FILE_HASHES_FILE, 'w', encoding='utf-8') as f:
        json.dump(hashes, f, indent=2)


def compute_file_hash(filepath: str) -> Optional[str]:
    """Calcula hash MD5 de un archivo."""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None


def get_git_changed_files() -> Set[str]:
    """
    Obtiene archivos modificados via git diff.
    Incluye staged, modified y untracked.
    """
    changed = set()
    
    try:
        # Archivos modificados (no staged)
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True, text=True,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0:
            changed.update(f.strip() for f in result.stdout.split('\n') if f.strip())
        
        # Archivos staged
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0:
            changed.update(f.strip() for f in result.stdout.split('\n') if f.strip())
        
        # Archivos untracked
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            capture_output=True, text=True,
            encoding='utf-8', errors='replace'
        )
        if result.returncode == 0:
            changed.update(f.strip() for f in result.stdout.split('\n') if f.strip())
    
    except Exception as e:
        log_warn(f"Error ejecutando git: {e}")
    
    return changed


def get_project_files(extensions: List[str] = None) -> List[str]:
    """Obtiene lista de archivos del proyecto."""
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.json', '.md', '.yaml', '.yml']
    
    files = []
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.agent'}
    
    for root, dirs, filenames in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                path = os.path.join(root, filename).replace('\\', '/')
                if path.startswith('./'):
                    path = path[2:]
                files.append(path)
    
    return files


def detect_changed_files(current_files: List[str]) -> Dict[str, List[str]]:
    """
    INCREMENTAL INDEXING: Detecta archivos que necesitan re-indexacion.
    
    Returns:
        Dict con 'added', 'modified', 'deleted'
    """
    old_hashes = load_file_hashes()
    git_changed = get_git_changed_files()
    
    changes = {
        'added': [],
        'modified': [],
        'deleted': []
    }
    
    current_set = set(current_files)
    old_set = set(old_hashes.keys())
    
    # Archivos nuevos
    changes['added'] = list(current_set - old_set)
    
    # Archivos eliminados
    changes['deleted'] = list(old_set - current_set)
    
    # Archivos modificados (check hash o git diff)
    for f in current_set & old_set:
        if f in git_changed:
            changes['modified'].append(f)
        else:
            new_hash = compute_file_hash(f)
            if new_hash and new_hash != old_hashes.get(f):
                changes['modified'].append(f)
    
    return changes


def index_codebase(force: bool = False, incremental: bool = True) -> Dict[str, Any]:
    """
    Indexa el codebase para busqueda semantica.
    
    Args:
        force: Forzar re-indexacion completa
        incremental: Usar indexacion incremental (git diff + hashes)
    """
    print(make_header("AGCCE RAG Indexer v2.0"))
    
    state = load_index_state()
    workspace = os.getcwd()
    
    log_info(f"Workspace: {workspace}")
    print(f"{Colors.CYAN}Modo:{Colors.RESET} {'Incremental' if incremental and not force else 'Completo'}")
    print()
    
    # Obtener archivos actuales
    print(f"{Colors.BOLD}[1/4] Escaneando archivos...{Colors.RESET}")
    files = get_project_files()
    print(f"  Total archivos: {len(files)}")
    
    # Detectar cambios si modo incremental
    if incremental and not force and state.get("status") == "indexed":
        print(f"\n{Colors.BOLD}[2/4] Detectando cambios (Incremental)...{Colors.RESET}")
        changes = detect_changed_files(files)
        
        added = len(changes['added'])
        modified = len(changes['modified'])
        deleted = len(changes['deleted'])
        
        print(f"  {Colors.GREEN}+ Nuevos:{Colors.RESET} {added}")
        print(f"  {Colors.YELLOW}~ Modificados:{Colors.RESET} {modified}")
        print(f"  {Colors.RED}- Eliminados:{Colors.RESET} {deleted}")
        
        total_changes = added + modified + deleted
        
        if total_changes == 0:
            log_info("Sin cambios desde ultima indexacion")
            print(f"\n{Colors.GREEN}=== INDEX UP TO DATE ==={Colors.RESET}\n")
            return state
        
        # Solo re-indexar archivos cambiados
        files_to_index = changes['added'] + changes['modified']
        print(f"\n  Archivos a re-indexar: {len(files_to_index)}")
        
        for f in files_to_index[:10]:
            status = '+' if f in changes['added'] else '~'
            print(f"    {status} {f}")
        if len(files_to_index) > 10:
            print(f"    ... y {len(files_to_index) - 10} mas")
    
    else:
        print(f"\n{Colors.BOLD}[2/4] Modo completo (sin cache)...{Colors.RESET}")
        files_to_index = files
    
    # Clasificar por tipo
    print(f"\n{Colors.BOLD}[3/4] Clasificando por tipo...{Colors.RESET}")
    by_type = {}
    for f in files:
        ext = os.path.splitext(f)[1] or 'other'
        by_type[ext] = by_type.get(ext, 0) + 1
    
    for ext, count in sorted(by_type.items(), key=lambda x: -x[1])[:5]:
        print(f"  {ext}: {count}")
    
    # Actualizar hashes
    print(f"\n{Colors.BOLD}[4/4] Actualizando indice...{Colors.RESET}")
    
    new_hashes = {}
    for f in files:
        h = compute_file_hash(f)
        if h:
            new_hashes[f] = h
    
    save_file_hashes(new_hashes)
    
    # Actualizar estado
    state = {
        "last_indexed": datetime.now().isoformat(),
        "files_indexed": len(files),
        "workspace": workspace,
        "status": "indexed",
        "file_types": by_type,
        "indexed_files": files[:100],
        "last_incremental": {
            "added": len(changes['added']) if 'changes' in dir() else 0,
            "modified": len(changes['modified']) if 'changes' in dir() else 0,
            "deleted": len(changes['deleted']) if 'changes' in dir() else 0
        } if incremental else None
    }
    
    save_index_state(state)
    
    log_pass(f"Indexacion completada: {len(files)} archivos")
    print(f"\n{Colors.GREEN}=== INDEXING COMPLETE ==={Colors.RESET}")
    
    print(f"\n{Colors.BLUE}[i] Proxima vez usa --incremental para solo indexar cambios{Colors.RESET}\n")
    
    return state


def get_index_status() -> None:
    """Muestra estado actual del indice con estadisticas."""
    print(make_header("RAG Index Status"))
    
    state = load_index_state()
    hashes = load_file_hashes()
    
    if state.get("status") != "indexed":
        log_warn("Codebase no indexado")
        print(f"\n{Colors.YELLOW}Ejecuta: python rag_indexer.py{Colors.RESET}")
        return
    
    print(f"{Colors.CYAN}Workspace:{Colors.RESET} {state.get('workspace')}")
    print(f"{Colors.CYAN}Ultimo indexado:{Colors.RESET} {state.get('last_indexed')}")
    print(f"{Colors.CYAN}Archivos indexados:{Colors.RESET} {state.get('files_indexed')}")
    print(f"{Colors.CYAN}Archivos con hash:{Colors.RESET} {len(hashes)}")
    
    # Mostrar cambios pendientes
    print(f"\n{Colors.BOLD}Cambios pendientes:{Colors.RESET}")
    current_files = get_project_files()
    changes = detect_changed_files(current_files)
    
    print(f"  + Nuevos: {len(changes['added'])}")
    print(f"  ~ Modificados: {len(changes['modified'])}")
    print(f"  - Eliminados: {len(changes['deleted'])}")
    
    if len(changes['added']) + len(changes['modified']) + len(changes['deleted']) > 0:
        log_warn("Hay cambios pendientes de indexar")
        print(f"{Colors.YELLOW}Ejecuta: python rag_indexer.py --incremental{Colors.RESET}")
    else:
        log_pass("Indice actualizado")


def main():
    if len(sys.argv) < 2:
        # Default: indexacion incremental
        index_codebase(incremental=True)
        return
    
    arg = sys.argv[1]
    
    if arg == "--reindex":
        index_codebase(force=True, incremental=False)
    elif arg == "--incremental":
        index_codebase(force=False, incremental=True)
    elif arg == "--status":
        get_index_status()
    elif arg == "--help":
        print(f"Uso: python {sys.argv[0]} [--reindex | --incremental | --status | --help]")
        print("\nOpciones:")
        print("  (sin args)     Indexacion incremental (default)")
        print("  --incremental  Solo indexa archivos modificados (git diff + hashes)")
        print("  --reindex      Fuerza re-indexacion completa")
        print("  --status       Muestra estado del indice y cambios pendientes")
    else:
        print(f"Opcion desconocida: {arg}")
        sys.exit(1)


if __name__ == '__main__':
    main()
