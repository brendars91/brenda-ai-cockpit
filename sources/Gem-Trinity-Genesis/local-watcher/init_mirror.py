
import shutil
import os
import sys
from pathlib import Path

# Configuración de rutas origen y destino
PATHS = {
    # Origen -> Destino interno
    str(Path.home() / ".gemini/Creador-proyectos-compilador/gem-architect"): "modules/gem-architect",
    str(Path.home() / ".gemini/Creador-proyectos-compilador/gem-builder"): "modules/gem-builder",
    str(Path.home() / ".gemini/Agente Copilot Engine"): "modules/engine",
    str(Path.home() / ".gemini/Skills proyectos"): "resources/skills"
}

IGNORE_PATTERNS = shutil.ignore_patterns('*.git*', '__pycache__', 'node_modules', '.venv', '.env', 'logs', 'tmp', 'artifacts')

def copy_module(src, dest):
    src_path = Path(src)
    dest_path = Path(dest).resolve()
    
    print(f"[COPY] {src_path} -> {dest_path}")
    
    if not src_path.exists():
        print(f"[ERROR] Source not found: {src_path}")
        return

    # Limpiar destino si existe para evitar conflictos
    if dest_path.exists():
        print(f"[INFO] Cleaning destination: {dest_path}")
        # En Windows a veces hay problemas si la carpeta está en uso, intentamos rmtree
        try:
            shutil.rmtree(dest_path)
        except Exception as e:
            print(f"[WARN] Could not fully clean {dest_path}: {e}")

    try:
        shutil.copytree(src_path, dest_path, ignore=IGNORE_PATTERNS, dirs_exist_ok=True)
        print(f"[SUCCESS] Copied {src_path.name}")
    except Exception as e:
        print(f"[FAIL] Error copying {src_path.name}: {e}")

if __name__ == "__main__":
    print("--- Gem Trinity Genesis: Initial Mirror Copy ---")
    base_dir = Path.cwd()
    print(f"Working Directory: {base_dir}")
    
    for src, rel_dest in PATHS.items():
        copy_module(src, base_dir / rel_dest)
        
    print("--- Mirror Initialization Complete ---")
