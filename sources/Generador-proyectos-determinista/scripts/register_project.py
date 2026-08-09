#!/usr/bin/env python3
"""
AGCCE Project Registrar
Permite registrar proyectos externos para que aparezcan en el Dashboard.

Uso:
  python scripts/register_project.py "Nombre del Proyecto" "C:/Ruta/Absoluta/Al/Proyecto"
"""

import sys
import json
import os
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
    os.makedirs(CONFIG_FILE.parent, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

def register_project(name, path_str):
    path = Path(path_str).resolve()
    
    if not path.exists():
        print(f"Error: La ruta '{path}' no existe.")
        sys.exit(1)
        
    if not path.is_dir():
        print(f"Error: La ruta '{path}' no es un directorio.")
        sys.exit(1)

    registry = load_registry()
    
    # Verificar si ya existe (por path o nombre)
    for proj in registry:
        if proj['name'] == name:
            print(f"Aviso: Actualizando proyecto existente '{name}'")
            proj['path'] = str(path)
            save_registry(registry)
            print(f"Proyecto '{name}' actualizado exitosamente.")
            return
            
        if Path(proj['path']).resolve() == path:
            print(f"Aviso: Esta ruta ya esta registrada como '{proj['name']}'")
            return

    # Nuevo proyecto
    registry.append({
        "name": name,
        "path": str(path),
        "description": "Registered external project"
    })
    
    save_registry(registry)
    print(f"Proyecto '{name}' registrado exitosamente en: {path}")

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

    if len(sys.argv) < 3:
        print(__doc__)
        return

    name = sys.argv[1]
    path = sys.argv[2]
    register_project(name, path)

if __name__ == "__main__":
    main()
