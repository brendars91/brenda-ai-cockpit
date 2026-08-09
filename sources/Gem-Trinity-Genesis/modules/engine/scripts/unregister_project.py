#!/usr/bin/env python3
"""
AGCCE Project Unregistrar
Elimina proyectos del registro del Dashboard.

Uso:
  python scripts/unregister_project.py "Nombre del Proyecto"
  python scripts/unregister_project.py --list
"""

import sys
import json
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "config" / "projects.json"

def load_registry():
    if not CONFIG_FILE.exists():
        return []
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error leyendo el registro: {e}")
        return []

def save_registry(registry):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def unregister_project(name):
    registry = load_registry()
    
    # Buscar el proyecto
    found = False
    new_registry = []
    for proj in registry:
        if proj['name'] == name:
            found = True
            print(f"✅ Proyecto '{name}' eliminado del registro.")
        else:
            new_registry.append(proj)
    
    if not found:
        print(f"⚠️  Proyecto '{name}' no encontrado en el registro.")
        return False
    
    save_registry(new_registry)
    return True

def list_projects():
    registry = load_registry()
    if not registry:
        print("No hay proyectos externos registrados.")
        return

    print(f"\nProyectos Registrados ({len(registry)}):")
    print("-" * 50)
    for p in registry:
        print(f"• {p['name']}: {p['path']}")
    print("-" * 50)

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        list_projects()
        return

    if len(sys.argv) < 2:
        print(__doc__)
        return

    name = sys.argv[1]
    unregister_project(name)

if __name__ == "__main__":
    main()
