
import subprocess
import sys
import json
import shlex
import os
from pathlib import Path
from config_manager import config

class Runner:
    def __init__(self):
        # Validar integridad del entorno interno antes de arrancar
        ok, msg = config.validate_integrity()
        if not ok:
            print(f"[RUNNER ERROR] {msg}")
            
        self.builder_path = config.get_path("builder")
        self.engine_path = config.get_path("engine")
        self.artifacts_dir = config.get_path("artifacts_root")
        
    def _validate_safe_path(self, file_path_str: str) -> Path:
        """
        Garantiza que el archivo esté dentro de los directorios permitidos
        y tenga una extensión válida. Previene Path Traversal.
        """
        if not file_path_str:
            raise ValueError("Empty path provided")
            
        try:
            path = Path(file_path_str).resolve()
        except Exception:
            raise ValueError("Invalid path format")

        # 1. Whitelist de extensiones
        if path.suffix not in ['.json', '.yaml', '.yml']:
            raise ValueError(f"Extension not allowed: {path.suffix}")
            
        # 2. Whitelist de directorios padres (Sandboxing)
        # Permitimos inputs desde artifacts o desde dentro de los módulos mismos
        allowed_parents = [
            self.artifacts_dir.resolve(),
            self.builder_path.resolve(),
            self.engine_path.resolve()
        ]
        
        is_safe = any(str(path).startswith(str(parent)) for parent in allowed_parents)
        if not is_safe:
            raise ValueError(f"Security Block: File {path} is outside allowed scopes.")
            
        return path

    def run_builder_compile(self, spec_file: str) -> bool:
        """
        Runs: python src/cli.py compile --spec <spec_file>
        """
        try:
            safe_spec = self._validate_safe_path(spec_file)
            print(f"[RUNNER] Compiling safe spec: {safe_spec.name}...")
            
            cli_path = self.builder_path / "src" / "cli.py"
            if not cli_path.exists():
                 print(f"[RUNNER ERROR] Builder CLI not found at internal path: {cli_path}")
                 return False

            cmd = [
                sys.executable, 
                str(cli_path),
                "compile",
                "--spec", str(safe_spec)
            ]
            
            # Timeout de 5 minutos para evitar procesos colgados
            env = os.environ.copy()
            # Asegurar PYTHONPATH si es necesario
            env["PYTHONPATH"] = str(self.builder_path)
            
            subprocess.run(cmd, cwd=self.builder_path, check=True, timeout=300, env=env)
            print(f"[RUNNER] Compilation success.")
            return True
            
        except ValueError as ve:
            print(f"[SECURITY ALERT] {ve}")
            return False
        except subprocess.TimeoutExpired:
            print("[RUNNER ERROR] Compilation timed out.")
            return False
        except subprocess.CalledProcessError as e:
            print(f"[RUNNER FAIL] Builder exited with code {e.returncode}")
            return False
        except Exception as e:
            print(f"[RUNNER ERROR] Unexpected error: {e}")
            return False

    def run_engine_execute(self, bundle_file: str) -> bool:
        """
        Runs AGCCE with the given bundle.
        """
        try:
            safe_bundle = self._validate_safe_path(bundle_file)
            print(f"[RUNNER] Launching Engine -> {safe_bundle.name}...")
            
            # Usar entrada correcta de AGCCE
            entry_point = self.engine_path / "scripts" / "agcce_cli.py"
            
            # Fallback si no existe agcce_cli (por compatibilidad)
            if not entry_point.exists():
                entry_point = self.engine_path / "scripts" / "gem_loader.py"
                
            if not entry_point.exists():
                 print(f"[RUNNER ERROR] Engine entry point not found in {self.engine_path}")
                 return False

            # Asumimos CLI v2: run --gem <file>
            # Ajustar según la CLI real de AGCCE
            if "agcce_cli.py" in str(entry_point):
                 cmd = [sys.executable, str(entry_point), "run", "--gem", str(safe_bundle)]
            else:
                 cmd = [sys.executable, str(entry_point), "--bundle", str(safe_bundle)]

            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.engine_path)

            subprocess.run(cmd, cwd=self.engine_path, check=True, timeout=600, env=env)
            print(f"[RUNNER] Execution finished.")
            return True
            
        except ValueError as ve:
            print(f"[SECURITY ALERT] {ve}")
            return False
        except Exception as e:
            print(f"[RUNNER ERROR] Execution failed: {e}")
            return False
            
if __name__ == "__main__":
    runner = Runner()
    print("[INFO] Secure Runner initialized (Internal Mode).")
