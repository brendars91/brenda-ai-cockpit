"""
Gem Registry Remote - Sincronización con Repositorios Git

Permite sincronizar Gem Bundles con repositorios remotos (GitHub, GitLab).
Features:
- Push/Pull de Gem Bundles
- Comparación de versiones local vs remoto
- Auto-sync configurable
- Conflict resolution
"""
import os
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class RemoteConfig:
    """Configuración de repositorio remoto"""
    name: str
    url: str
    branch: str = "main"
    path: str = "gems"  # Path dentro del repo
    auto_sync: bool = False
    last_sync: Optional[str] = None


@dataclass
class SyncResult:
    """Resultado de sincronización"""
    success: bool
    action: str  # pushed, pulled, conflict, up-to-date
    gems_synced: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    message: str = ""


class GemRegistryRemote:
    """Gestor de sincronización remota de Gems"""
    
    def __init__(self, gems_dir: str = None, config_file: str = None):
        """
        Args:
            gems_dir: Directorio local de gems
            config_file: Archivo de configuración de remotes
        """
        if gems_dir is None:
            gems_dir = Path(__file__).parent.parent / "gems"
        
        self.gems_dir = Path(gems_dir)
        self.gems_dir.mkdir(parents=True, exist_ok=True)
        
        if config_file is None:
            config_file = self.gems_dir / ".remotes.json"
        
        self.config_file = Path(config_file)
        self.remotes = self._load_remotes()
    
    def _load_remotes(self) -> Dict[str, RemoteConfig]:
        """Carga configuración de remotes"""
        if not self.config_file.exists():
            return {}
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            name: RemoteConfig(**config)
            for name, config in data.items()
        }
    
    def _save_remotes(self):
        """Guarda configuración de remotes"""
        data = {
            name: {
                "name": r.name,
                "url": r.url,
                "branch": r.branch,
                "path": r.path,
                "auto_sync": r.auto_sync,
                "last_sync": r.last_sync
            }
            for name, r in self.remotes.items()
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def add_remote(
        self,
        name: str,
        url: str,
        branch: str = "main",
        path: str = "gems",
        auto_sync: bool = False
    ) -> bool:
        """
        Añade un repositorio remoto.
        
        Args:
            name: Nombre identificador del remote
            url: URL del repositorio Git
            branch: Branch a usar
            path: Path dentro del repo donde están los gems
            auto_sync: Si sincronizar automáticamente
        
        Returns:
            True si se añadió correctamente
        """
        if name in self.remotes:
            return False
        
        self.remotes[name] = RemoteConfig(
            name=name,
            url=url,
            branch=branch,
            path=path,
            auto_sync=auto_sync
        )
        
        self._save_remotes()
        return True
    
    def remove_remote(self, name: str) -> bool:
        """Elimina un remote"""
        if name not in self.remotes:
            return False
        
        del self.remotes[name]
        self._save_remotes()
        return True
    
    def list_remotes(self) -> List[RemoteConfig]:
        """Lista todos los remotes configurados"""
        return list(self.remotes.values())
    
    def _run_git(self, args: List[str], cwd: str = None) -> Tuple[bool, str]:
        """Ejecuta comando git"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=cwd,
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout + result.stderr
        except FileNotFoundError:
            return False, "Git no encontrado en el sistema"
    
    def _get_local_gems(self) -> Dict[str, Dict]:
        """Obtiene lista de gems locales con hash"""
        gems = {}
        
        for gem_file in self.gems_dir.glob("*.json"):
            if gem_file.name.startswith("."):
                continue
            
            with open(gem_file, 'r', encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)
            
            # Calcular hash del contenido
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
            
            gems[gem_file.stem] = {
                "file": str(gem_file),
                "hash": content_hash,
                "version": data.get("bundle_meta", {}).get("version", "0.0.0"),
                "use_case_id": data.get("bundle_meta", {}).get("use_case_id", "unknown")
            }
        
        return gems
    
    def push(self, remote_name: str, gem_names: List[str] = None) -> SyncResult:
        """
        Push gems al repositorio remoto.
        
        Args:
            remote_name: Nombre del remote
            gem_names: Lista de gems a pushear (None = todos)
        
        Returns:
            SyncResult con detalles de la operación
        """
        if remote_name not in self.remotes:
            return SyncResult(
                success=False,
                action="error",
                message=f"Remote '{remote_name}' no encontrado"
            )
        
        remote = self.remotes[remote_name]
        local_gems = self._get_local_gems()
        
        if gem_names is None:
            gem_names = list(local_gems.keys())
        
        # Crear directorio temporal para clonar
        temp_dir = self.gems_dir / ".temp_sync"
        temp_dir.mkdir(exist_ok=True)
        
        # Clonar repo
        success, output = self._run_git(
            ["clone", "--depth", "1", "-b", remote.branch, remote.url, str(temp_dir)],
            cwd=str(self.gems_dir.parent)
        )
        
        if not success:
            return SyncResult(
                success=False,
                action="error",
                message=f"Error clonando repositorio: {output}"
            )
        
        # Copiar gems al repo clonado
        remote_gems_path = temp_dir / remote.path
        remote_gems_path.mkdir(parents=True, exist_ok=True)
        
        pushed_gems = []
        for gem_name in gem_names:
            if gem_name not in local_gems:
                continue
            
            src = Path(local_gems[gem_name]["file"])
            dst = remote_gems_path / src.name
            
            # Copiar archivo
            with open(src, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(dst, 'w', encoding='utf-8') as f:
                f.write(content)
            
            pushed_gems.append(gem_name)
        
        # Git add, commit, push
        self._run_git(["add", "."], cwd=str(temp_dir))
        
        commit_msg = f"Sync gems: {', '.join(pushed_gems)} [{datetime.now(timezone.utc).isoformat()}]"
        success, _ = self._run_git(["commit", "-m", commit_msg], cwd=str(temp_dir))
        
        if success:
            success, output = self._run_git(["push"], cwd=str(temp_dir))
        
        # Limpiar temp
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Actualizar last_sync
        remote.last_sync = datetime.now(timezone.utc).isoformat()
        self._save_remotes()
        
        return SyncResult(
            success=success,
            action="pushed",
            gems_synced=pushed_gems,
            message=f"Pushed {len(pushed_gems)} gems a {remote_name}"
        )
    
    def pull(self, remote_name: str, gem_names: List[str] = None) -> SyncResult:
        """
        Pull gems desde repositorio remoto.
        
        Args:
            remote_name: Nombre del remote
            gem_names: Lista de gems a pullear (None = todos)
        
        Returns:
            SyncResult con detalles de la operación
        """
        if remote_name not in self.remotes:
            return SyncResult(
                success=False,
                action="error",
                message=f"Remote '{remote_name}' no encontrado"
            )
        
        remote = self.remotes[remote_name]
        
        # Crear directorio temporal para clonar
        temp_dir = self.gems_dir / ".temp_sync"
        
        # Clonar repo
        success, output = self._run_git(
            ["clone", "--depth", "1", "-b", remote.branch, remote.url, str(temp_dir)],
            cwd=str(self.gems_dir.parent)
        )
        
        if not success:
            return SyncResult(
                success=False,
                action="error",
                message=f"Error clonando repositorio: {output}"
            )
        
        # Obtener gems del repo
        remote_gems_path = temp_dir / remote.path
        
        if not remote_gems_path.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            return SyncResult(
                success=False,
                action="error",
                message=f"Path '{remote.path}' no existe en el repositorio"
            )
        
        pulled_gems = []
        conflicts = []
        local_gems = self._get_local_gems()
        
        for gem_file in remote_gems_path.glob("*.json"):
            if gem_file.name.startswith("."):
                continue
            
            gem_name = gem_file.stem
            
            if gem_names is not None and gem_name not in gem_names:
                continue
            
            # Leer gem remoto
            with open(gem_file, 'r', encoding='utf-8') as f:
                remote_content = f.read()
            
            local_path = self.gems_dir / gem_file.name
            
            # Verificar conflictos
            if local_path.exists():
                with open(local_path, 'r', encoding='utf-8') as f:
                    local_content = f.read()
                
                if local_content != remote_content:
                    # Hay diferencias - verificar versiones
                    remote_data = json.loads(remote_content)
                    local_data = json.loads(local_content)
                    
                    remote_version = remote_data.get("bundle_meta", {}).get("version", "0.0.0")
                    local_version = local_data.get("bundle_meta", {}).get("version", "0.0.0")
                    
                    # Si versión remota es mayor, actualizar
                    if self._compare_versions(remote_version, local_version) > 0:
                        with open(local_path, 'w', encoding='utf-8') as f:
                            f.write(remote_content)
                        pulled_gems.append(gem_name)
                    else:
                        conflicts.append(gem_name)
            else:
                # Gem nuevo, copiar
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(remote_content)
                pulled_gems.append(gem_name)
        
        # Limpiar temp
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Actualizar last_sync
        remote.last_sync = datetime.now(timezone.utc).isoformat()
        self._save_remotes()
        
        return SyncResult(
            success=True,
            action="pulled",
            gems_synced=pulled_gems,
            conflicts=conflicts,
            message=f"Pulled {len(pulled_gems)} gems de {remote_name}" +
                    (f", {len(conflicts)} conflictos" if conflicts else "")
        )
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compara versiones semánticas. Returns: >0 si v1>v2, <0 si v1<v2, 0 si iguales"""
        def parse(v):
            parts = v.split(".")
            return [int(p) for p in parts[:3]] + [0] * (3 - len(parts))
        
        p1, p2 = parse(v1), parse(v2)
        
        for a, b in zip(p1, p2):
            if a > b:
                return 1
            if a < b:
                return -1
        return 0
    
    def status(self, remote_name: str = None) -> Dict:
        """
        Obtiene estado de sincronización.
        
        Args:
            remote_name: Remote específico o None para todos
        
        Returns:
            Dict con estado de sincronización
        """
        local_gems = self._get_local_gems()
        
        status = {
            "local_gems_count": len(local_gems),
            "local_gems": list(local_gems.keys()),
            "remotes": {}
        }
        
        remotes_to_check = (
            [self.remotes[remote_name]] if remote_name else list(self.remotes.values())
        )
        
        for remote in remotes_to_check:
            status["remotes"][remote.name] = {
                "url": remote.url,
                "branch": remote.branch,
                "auto_sync": remote.auto_sync,
                "last_sync": remote.last_sync
            }
        
        return status


# CLI para testing standalone
if __name__ == "__main__":
    import sys
    
    registry = GemRegistryRemote()
    
    print("\n" + "="*60)
    print("  GEM REGISTRY REMOTE")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nComandos:")
        print("  add <name> <url> [branch]  - Añadir remote")
        print("  remove <name>              - Eliminar remote")
        print("  list                       - Listar remotes")
        print("  push <remote> [gem...]     - Push gems")
        print("  pull <remote> [gem...]     - Pull gems")
        print("  status                     - Estado de sync")
    else:
        cmd = sys.argv[1]
        
        if cmd == "list":
            remotes = registry.list_remotes()
            print(f"\nRemotes configurados ({len(remotes)}):")
            for r in remotes:
                print(f"  - {r.name}: {r.url} [{r.branch}]")
                print(f"    Last sync: {r.last_sync or 'never'}")
        
        elif cmd == "status":
            status = registry.status()
            print(f"\nLocal gems: {status['local_gems_count']}")
            for gem in status['local_gems']:
                print(f"  - {gem}")
            print(f"\nRemotes: {len(status['remotes'])}")
            for name, info in status['remotes'].items():
                print(f"  - {name}: {info['url']}")
        
        elif cmd == "add" and len(sys.argv) >= 4:
            name, url = sys.argv[2], sys.argv[3]
            branch = sys.argv[4] if len(sys.argv) > 4 else "main"
            if registry.add_remote(name, url, branch):
                print(f"✓ Remote '{name}' añadido")
            else:
                print(f"✗ Remote '{name}' ya existe")
