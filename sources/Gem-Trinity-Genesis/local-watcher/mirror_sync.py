
import sys
import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
import os

# Cargar configuración básica para saber rutas (hardcoded por ahora hasta tener config_manager)
# En producción esto vendría de config_manager
PATHS_MAP = {
    # Interno -> Externo (Usuario)
    "modules/gem-architect": r"C:\Users\ASUS\.gemini\Creador-proyectos-compilador\gem-architect",
    "modules/gem-builder": r"C:\Users\ASUS\.gemini\Creador-proyectos-compilador\gem-builder",
    "modules/engine": r"C:\Users\ASUS\.gemini\Agente Copilot Engine",
    "resources/skills": r"C:\Users\ASUS\.gemini\Skills proyectos"
}

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'logs', 'tmp', 'artifacts', 'dist', '.next'}

class MirrorHandler(FileSystemEventHandler):
    def __init__(self, source_root, target_root, name):
        self.source_root = Path(source_root).resolve()
        self.target_root = Path(target_root).resolve()
        self.name = name
        self.last_sync = 0

    def _sync(self, src_path):
        # Evitar bucle infinito de sincronización (debounce muy básico)
        if time.time() - self.last_sync < 0.5:
            return

        try:
            rel_path = Path(src_path).relative_to(self.source_root)
            
            # Verificar ignore lists
            if any(part in IGNORE_DIRS for part in rel_path.parts):
                return

            dest_path = self.target_root / rel_path

            if os.path.isdir(src_path):
                # Si es directorio, crearlo
                dest_path.mkdir(parents=True, exist_ok=True)
            elif os.path.isfile(src_path):
                # Si es archivo, copiarlo
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest_path)
                print(f"[{self.name}] Synced: {rel_path}")
            
            self.last_sync = time.time()
            
        except Exception as e:
            # Ignorar errores de archivos efímeros
            pass

    def on_created(self, event):
        self._sync(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._sync(event.src_path)

    def on_moved(self, event):
         # Simplificación: tratar mover como crear en destino. 
         # Una implementación robusta borraría el origen también.
         self._sync(event.dest_path)

def start_mirroring():
    print("--- Gem Trinity: Mirror Engine Started ---")
    observer = Observer()
    
    base_dir = Path.cwd()

    for internal_rel, external_abs in PATHS_MAP.items():
        internal_path = base_dir / internal_rel
        external_path = Path(external_abs)

        if not internal_path.exists() or not external_path.exists():
            print(f"[WARN] Skipping {internal_rel} - Path missing")
            continue

        # Monitor Interno -> Externo
        handler_out = MirrorHandler(internal_path, external_path, f"OUT:{internal_rel}")
        observer.schedule(handler_out, str(internal_path), recursive=True)
        print(f"[WATCH] Monitoring Internal: {internal_rel}")

        # Monitor Externo -> Interno
        handler_in = MirrorHandler(external_path, internal_path, f"IN:{external_path.name}")
        observer.schedule(handler_in, str(external_path), recursive=True)
        print(f"[WATCH] Monitoring External: {external_path}")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_mirroring()
