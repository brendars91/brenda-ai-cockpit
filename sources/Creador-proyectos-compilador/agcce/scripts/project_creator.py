#!/usr/bin/env python3
"""
AGCCE Project Creator
Crea nuevos proyectos estandarizados y los registra automáticamente en el Dashboard.

Uso:
  python scripts/project_creator.py "Nombre del Proyecto" [--path "C:/Ruta/Opcional"]
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Agregar directorio actual al path para importar register_project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from register_project import register_project
except ImportError:
    print("Error: No se pudo importar 'register_project'. Asegurate de que existe.")
    sys.exit(1)

def create_project(name, location=None):
    # Definir ruta destino
    if location:
        project_path = Path(location) / name
    else:
        # Por defecto dentro de Agente Copilot Engine
        root = Path(__file__).parent.parent
        project_path = root / name

    print(f"creando proyecto '{name}' en: {project_path}")
    
    if project_path.exists():
        print(f"Error: La ruta '{project_path}' ya existe.")
        return False

    try:
        # 1. Crear directorios
        os.makedirs(project_path)
        os.makedirs(project_path / "docs", exist_ok=True)
        os.makedirs(project_path / "src", exist_ok=True)
        os.makedirs(project_path / "tests", exist_ok=True)

        # 2. Crear archivos base
        # Marcador AGCCE (para que el dashboard lo detecte)
        with open(project_path / ".agcce_project", "w", encoding="utf-8") as f:
            f.write(f"# AGCCE Project Marker\nCreated: {__import__('datetime').datetime.now().isoformat()}\n")
        
        # README.md
        with open(project_path / "README.md", "w", encoding="utf-8") as f:
            f.write(f"# {name}\n\nProject created with AGCCE Project Creator.\n")
            
        # .gitignore básico
        with open(project_path / ".gitignore", "w", encoding="utf-8") as f:
            f.write("__pycache__/\n*.pyc\n.env\n.DS_Store\n.agcce_project\n")
            
        # task.md inicial
        with open(project_path / "task.md", "w", encoding="utf-8") as f:
            f.write(f"# Tasks for {name}\n\n- [ ] Initialize project <!-- id: 0 -->\n")

        print("✔ Estructura de archivos creada.")

        # 3. Registrar en el Dashboard
        # Si está dentro del engine, el dashboard lo detecta solo, pero si es externo necesita registro.
        # El script register_project maneja la lógica de duplicados, así que llamémoslo siempre para consistencia
        # si es externo.
        
        is_external = False
        try:
            root = Path(__file__).parent.parent
            # Comprobar si project_path es relativo a root
            project_path.relative_to(root)
        except ValueError:
            is_external = True

        if is_external:
            print("Registrando proyecto externo...")
            register_project(name, str(project_path))
        else:
            print("Proyecto interno creado. Será detectado automáticamente por el Dashboard.")

        return True

    except Exception as e:
        print(f"Error creando el proyecto: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="AGCCE Project Creator")
    parser.add_argument("name", help="Nombre del proyecto")
    parser.add_argument("--path", help="Ruta base opcional (por defecto: interno en AGCCE)", default=None)
    
    args = parser.parse_args()
    
    if create_project(args.name, args.path):
        print(f"\n✅ Proyecto '{args.name}' creado exitosamente.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
