#!/usr/bin/env python3
"""
AGCCE Changelog Generator v1.0
Genera CHANGELOG.md automáticamente desde commits de Git.

Uso:
  python changelog_generator.py              # Genera desde último tag
  python changelog_generator.py --all        # Genera todo el historial
  python changelog_generator.py --since v1.0 # Desde tag específico
"""

import os
import sys
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

# Importar utilidades
try:
    from common import Colors, Symbols, log_pass, log_fail, log_warn, log_info
except ImportError:
    def log_pass(msg): print(f"[OK] {msg}")
    def log_fail(msg): print(f"[X] {msg}")
    def log_warn(msg): print(f"[!] {msg}")
    def log_info(msg): print(f"[i] {msg}")


CHANGELOG_FILE = "CHANGELOG.md"

# Mapeo de prefijos de commit a categorías
COMMIT_TYPES = {
    "feat": ("Features", "✨"),
    "fix": ("Bug Fixes", "🐛"),
    "docs": ("Documentation", "📚"),
    "style": ("Styles", "💄"),
    "refactor": ("Code Refactoring", "♻️"),
    "perf": ("Performance", "⚡"),
    "test": ("Tests", "✅"),
    "build": ("Build", "🔧"),
    "ci": ("CI/CD", "👷"),
    "chore": ("Chores", "🔨"),
    "security": ("Security", "🔒"),
}


def run_git_command(args: List[str]) -> Tuple[bool, str]:
    """Ejecuta comando git."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def get_commits(since_tag: str = None, all_history: bool = False) -> List[Dict]:
    """Obtiene commits del repositorio."""
    format_str = "%H||%s||%an||%ai"
    
    if all_history:
        args = ["log", f"--pretty=format:{format_str}"]
    elif since_tag:
        args = ["log", f"{since_tag}..HEAD", f"--pretty=format:{format_str}"]
    else:
        # Obtener último tag
        success, last_tag = run_git_command(["describe", "--tags", "--abbrev=0"])
        if success and last_tag:
            args = ["log", f"{last_tag}..HEAD", f"--pretty=format:{format_str}"]
        else:
            # Sin tags, usar últimos 50 commits
            args = ["log", "-50", f"--pretty=format:{format_str}"]
    
    success, output = run_git_command(args)
    if not success or not output:
        return []
    
    commits = []
    for line in output.split('\n'):
        if not line.strip():
            continue
        
        parts = line.split('||')
        if len(parts) >= 4:
            commits.append({
                "hash": parts[0][:8],
                "message": parts[1],
                "author": parts[2],
                "date": parts[3][:10]
            })
    
    return commits


def parse_commit_message(message: str) -> Tuple[str, str, str]:
    """
    Parsea mensaje de commit en formato Conventional Commits.
    Returns: (type, scope, description)
    """
    # Patrón: type(scope): description
    pattern = r'^(\w+)(?:\(([^)]+)\))?\s*:\s*(.+)$'
    match = re.match(pattern, message)
    
    if match:
        return match.group(1), match.group(2) or "", match.group(3)
    
    # Si no sigue el formato, intentar detectar tipo por palabras clave
    message_lower = message.lower()
    if message_lower.startswith(("add", "new", "implement")):
        return "feat", "", message
    elif message_lower.startswith(("fix", "bug", "resolve")):
        return "fix", "", message
    elif message_lower.startswith(("doc", "readme")):
        return "docs", "", message
    elif message_lower.startswith(("refactor", "clean")):
        return "refactor", "", message
    
    return "other", "", message


def categorize_commits(commits: List[Dict]) -> Dict[str, List[Dict]]:
    """Categoriza commits por tipo."""
    categorized = defaultdict(list)
    
    for commit in commits:
        commit_type, scope, description = parse_commit_message(commit["message"])
        
        category = COMMIT_TYPES.get(commit_type, ("Other", "📦"))[0]
        
        categorized[category].append({
            **commit,
            "type": commit_type,
            "scope": scope,
            "description": description
        })
    
    return categorized


def generate_changelog(
    commits: List[Dict],
    version: str = None,
    prepend: bool = True
) -> str:
    """Genera contenido del CHANGELOG."""
    if not commits:
        return ""
    
    categorized = categorize_commits(commits)
    
    # Header
    lines = []
    if version:
        lines.append(f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n")
    else:
        lines.append(f"## [Unreleased] - {datetime.now().strftime('%Y-%m-%d')}\n")
    
    # Ordenar categorías
    category_order = ["Features", "Bug Fixes", "Security", "Performance", 
                      "Code Refactoring", "Documentation", "Tests", "Other"]
    
    for category in category_order:
        if category not in categorized:
            continue
        
        emoji = next((v[1] for k, v in COMMIT_TYPES.items() if v[0] == category), "📦")
        lines.append(f"\n### {emoji} {category}\n")
        
        for commit in categorized[category]:
            scope = f"**{commit['scope']}**: " if commit.get('scope') else ""
            lines.append(f"- {scope}{commit['description']} ({commit['hash']})")
    
    lines.append("\n")
    
    return '\n'.join(lines)


def update_changelog(new_content: str, prepend: bool = True) -> None:
    """Actualiza el archivo CHANGELOG."""
    existing = ""
    
    if os.path.exists(CHANGELOG_FILE):
        with open(CHANGELOG_FILE, 'r', encoding='utf-8') as f:
            existing = f.read()
    
    header = """# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""
    
    if prepend:
        # Buscar donde insertar (después del header)
        if "# Changelog" in existing:
            # Encontrar el primer ## para insertar antes
            match = re.search(r'\n## ', existing)
            if match:
                content = existing[:match.start()] + "\n" + new_content + existing[match.start():]
            else:
                content = existing + "\n" + new_content
        else:
            content = header + new_content
    else:
        content = header + new_content
    
    with open(CHANGELOG_FILE, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    print("=" * 60)
    print("  AGCCE Changelog Generator v1.0")
    print("=" * 60)
    
    since_tag = None
    all_history = False
    version = None
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--all":
            all_history = True
        elif arg == "--since" and i < len(sys.argv) - 1:
            since_tag = sys.argv[i + 1]
        elif arg.startswith("--version="):
            version = arg.split("=")[1]
    
    # Obtener commits
    log_info("Obteniendo commits...")
    commits = get_commits(since_tag=since_tag, all_history=all_history)
    
    if not commits:
        log_warn("No se encontraron commits")
        return
    
    log_info(f"Encontrados {len(commits)} commits")
    
    # Generar changelog
    log_info("Generando changelog...")
    content = generate_changelog(commits, version=version)
    
    if not content:
        log_warn("No se generó contenido")
        return
    
    # Actualizar archivo
    update_changelog(content, prepend=True)
    log_pass(f"CHANGELOG actualizado: {CHANGELOG_FILE}")
    
    # Mostrar preview
    print("\n--- Preview ---")
    print(content[:500])
    if len(content) > 500:
        print("...")


if __name__ == '__main__':
    main()
