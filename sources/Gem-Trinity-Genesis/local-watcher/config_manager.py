
import os
import json
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.base_dir = Path(__file__).parent.parent # Root del proyecto
        self.modules_dir = self.base_dir / "modules"
        self.resources_dir = self.base_dir / "resources"
        
        # Rutas INTERNAS Autocontenidas (Prioridad Absoluta)
        self.paths = {
            "architect": self.modules_dir / "gem-architect",
            "builder": self.modules_dir / "gem-builder",
            "engine": self.modules_dir / "engine",
            "skills": self.resources_dir / "skills",
            "mcp_config": self.base_dir / "local-watcher" / "mcp_config_local.json", # Copia local
            "artifacts_root": self.base_dir / "artifacts"
        }
        
    def get_path(self, key):
        """Retorna ruta absoluta validada"""
        path = self.paths.get(key)
        if not path:
            raise KeyError(f"Path key '{key}' not found configuration")
        return path

    def validate_integrity(self):
        """Verifica que la estructura interna esté intacta"""
        missing = []
        for key, path in self.paths.items():
            if key == "mcp_config": continue # Opcional al inicio
            if not path.exists():
                missing.append(f"{key} ({path})")
        
        if missing:
            return False, f"Missing modules: {', '.join(missing)}"
        return True, "Integrity OK"

# Singleton instance
config = ConfigManager()
