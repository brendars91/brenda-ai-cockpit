"""
Gem Auto-Update - Sistema de notificaciones y actualizaciones automáticas

Features:
- Detecta nuevas versiones de Gems en remotes
- Notifica al usuario de actualizaciones disponibles
- Auto-update configurable por Gem
- Changelog tracking
- Rollback support
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class UpdateInfo:
    """Información de una actualización disponible"""
    gem_name: str
    current_version: str
    new_version: str
    remote_name: str
    changes: List[str] = field(default_factory=list)
    risk_delta: int = 0  # Cambio en Risk Score
    breaking_changes: bool = False


@dataclass 
class UpdateResult:
    """Resultado de una actualización"""
    success: bool
    gem_name: str
    old_version: str
    new_version: str
    backup_path: Optional[str] = None
    message: str = ""


class GemAutoUpdate:
    """Sistema de auto-actualización de Gems"""
    
    def __init__(self, gems_dir: str = None, config_file: str = None):
        """
        Args:
            gems_dir: Directorio local de gems
            config_file: Archivo de configuración
        """
        if gems_dir is None:
            gems_dir = Path(__file__).parent.parent / "gems"
        
        self.gems_dir = Path(gems_dir)
        self.gems_dir.mkdir(parents=True, exist_ok=True)
        
        self.backups_dir = self.gems_dir / ".backups"
        self.backups_dir.mkdir(exist_ok=True)
        
        if config_file is None:
            config_file = self.gems_dir / ".auto_update.json"
        
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Carga configuración de auto-update"""
        if not self.config_file.exists():
            return {
                "enabled": True,
                "check_interval_hours": 24,
                "auto_update_gems": [],  # Lista de gems con auto-update
                "notify_only_gems": [],  # Lista de gems que solo notifican
                "last_check": None,
                "update_history": []
            }
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_config(self):
        """Guarda configuración"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def configure(
        self,
        enabled: bool = None,
        check_interval_hours: int = None,
        auto_update_gems: List[str] = None,
        notify_only_gems: List[str] = None
    ):
        """Configura el sistema de auto-update"""
        if enabled is not None:
            self.config["enabled"] = enabled
        if check_interval_hours is not None:
            self.config["check_interval_hours"] = check_interval_hours
        if auto_update_gems is not None:
            self.config["auto_update_gems"] = auto_update_gems
        if notify_only_gems is not None:
            self.config["notify_only_gems"] = notify_only_gems
        
        self._save_config()
    
    def _get_local_gem_info(self, gem_name: str) -> Optional[Dict]:
        """Obtiene información de un gem local"""
        gem_file = self.gems_dir / f"{gem_name}.json"
        
        if not gem_file.exists():
            # Buscar con versión
            for f in self.gems_dir.glob(f"{gem_name}_v*.json"):
                gem_file = f
                break
        
        if not gem_file.exists():
            return None
        
        with open(gem_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "file": str(gem_file),
            "version": data.get("bundle_meta", {}).get("version", "0.0.0"),
            "risk_score": data.get("bundle_meta", {}).get("risk_score", 0),
            "compiled_at": data.get("bundle_meta", {}).get("compiled_at", ""),
            "data": data
        }
    
    def check_updates(self, remote_registry=None) -> List[UpdateInfo]:
        """
        Verifica actualizaciones disponibles.
        
        Args:
            remote_registry: Instancia de GemRegistryRemote (opcional)
        
        Returns:
            Lista de UpdateInfo con actualizaciones disponibles
        """
        updates = []
        
        # Obtener gems locales
        local_gems = {}
        for gem_file in self.gems_dir.glob("*.json"):
            if gem_file.name.startswith("."):
                continue
            
            with open(gem_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            use_case_id = data.get("bundle_meta", {}).get("use_case_id", gem_file.stem)
            local_gems[use_case_id] = {
                "version": data.get("bundle_meta", {}).get("version", "0.0.0"),
                "risk_score": data.get("bundle_meta", {}).get("risk_score", 0)
            }
        
        # Si hay remote_registry, verificar contra remotes
        if remote_registry:
            for remote_name, remote in remote_registry.remotes.items():
                # Aquí se haría pull temporal para comparar
                # Por ahora, simulación
                pass
        
        # Actualizar última verificación
        self.config["last_check"] = datetime.now(timezone.utc).isoformat()
        self._save_config()
        
        return updates
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compara versiones semánticas"""
        def parse(v):
            parts = v.replace("-", ".").split(".")
            result = []
            for p in parts[:3]:
                try:
                    result.append(int(p))
                except ValueError:
                    result.append(0)
            return result + [0] * (3 - len(result))
        
        p1, p2 = parse(v1), parse(v2)
        
        for a, b in zip(p1, p2):
            if a > b:
                return 1
            if a < b:
                return -1
        return 0
    
    def create_backup(self, gem_name: str) -> Optional[str]:
        """
        Crea backup de un gem antes de actualizar.
        
        Args:
            gem_name: Nombre del gem
        
        Returns:
            Path del backup o None si falla
        """
        gem_info = self._get_local_gem_info(gem_name)
        if not gem_info:
            return None
        
        # Crear nombre de backup con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{gem_name}_v{gem_info['version']}_{timestamp}.json"
        backup_path = self.backups_dir / backup_name
        
        # Copiar archivo
        shutil.copy2(gem_info["file"], backup_path)
        
        return str(backup_path)
    
    def update_gem(
        self,
        gem_name: str,
        new_content: Dict,
        create_backup: bool = True
    ) -> UpdateResult:
        """
        Actualiza un gem con nuevo contenido.
        
        Args:
            gem_name: Nombre del gem
            new_content: Nuevo contenido del bundle
            create_backup: Si crear backup antes de actualizar
        
        Returns:
            UpdateResult con detalles de la operación
        """
        # Obtener info actual
        current_info = self._get_local_gem_info(gem_name)
        
        old_version = "0.0.0"
        backup_path = None
        
        if current_info:
            old_version = current_info["version"]
            
            # Crear backup si se requiere
            if create_backup:
                backup_path = self.create_backup(gem_name)
        
        # Obtener nueva versión
        new_version = new_content.get("bundle_meta", {}).get("version", "1.0.0")
        
        # Determinar archivo de destino
        gem_file = self.gems_dir / f"{gem_name}_v{new_version}.json"
        
        # Guardar nuevo contenido
        with open(gem_file, 'w', encoding='utf-8') as f:
            json.dump(new_content, f, indent=2, ensure_ascii=False)
        
        # Registrar en historial
        self.config["update_history"].append({
            "gem_name": gem_name,
            "old_version": old_version,
            "new_version": new_version,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "backup_path": backup_path
        })
        
        # Mantener solo últimos 50 registros
        self.config["update_history"] = self.config["update_history"][-50:]
        self._save_config()
        
        return UpdateResult(
            success=True,
            gem_name=gem_name,
            old_version=old_version,
            new_version=new_version,
            backup_path=backup_path,
            message=f"Gem '{gem_name}' actualizado de v{old_version} a v{new_version}"
        )
    
    def rollback(self, gem_name: str, target_version: str = None) -> UpdateResult:
        """
        Rollback a una versión anterior.
        
        Args:
            gem_name: Nombre del gem
            target_version: Versión específica o None para última
        
        Returns:
            UpdateResult con detalles
        """
        # Buscar backup
        backups = list(self.backups_dir.glob(f"{gem_name}_*.json"))
        
        if not backups:
            return UpdateResult(
                success=False,
                gem_name=gem_name,
                old_version="",
                new_version="",
                message=f"No hay backups disponibles para '{gem_name}'"
            )
        
        # Ordenar por fecha (más reciente primero)
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if target_version:
            # Buscar versión específica
            backup_file = None
            for b in backups:
                if f"_v{target_version}_" in b.name:
                    backup_file = b
                    break
            
            if not backup_file:
                return UpdateResult(
                    success=False,
                    gem_name=gem_name,
                    old_version="",
                    new_version="",
                    message=f"Backup v{target_version} no encontrado para '{gem_name}'"
                )
        else:
            backup_file = backups[0]
        
        # Obtener versión actual
        current_info = self._get_local_gem_info(gem_name)
        current_version = current_info["version"] if current_info else "unknown"
        
        # Restaurar backup
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        backup_version = backup_data.get("bundle_meta", {}).get("version", "0.0.0")
        
        # Guardar como versión actual
        dest_file = self.gems_dir / f"{gem_name}_v{backup_version}.json"
        shutil.copy2(backup_file, dest_file)
        
        return UpdateResult(
            success=True,
            gem_name=gem_name,
            old_version=current_version,
            new_version=backup_version,
            backup_path=str(backup_file),
            message=f"Rollback de '{gem_name}' de v{current_version} a v{backup_version}"
        )
    
    def get_update_history(self, gem_name: str = None, limit: int = 10) -> List[Dict]:
        """
        Obtiene historial de actualizaciones.
        
        Args:
            gem_name: Filtrar por gem específico
            limit: Número máximo de registros
        
        Returns:
            Lista de registros de historial
        """
        history = self.config.get("update_history", [])
        
        if gem_name:
            history = [h for h in history if h.get("gem_name") == gem_name]
        
        return history[-limit:]
    
    def list_backups(self, gem_name: str = None) -> List[Dict]:
        """Lista backups disponibles"""
        pattern = f"{gem_name}_*.json" if gem_name else "*.json"
        backups = []
        
        for backup_file in self.backups_dir.glob(pattern):
            stat = backup_file.stat()
            backups.append({
                "file": str(backup_file),
                "name": backup_file.name,
                "size_kb": stat.st_size / 1024,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)
    
    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """
        Limpia backups antiguos.
        
        Args:
            keep_count: Número de backups a mantener por gem
        
        Returns:
            Número de backups eliminados
        """
        deleted = 0
        
        # Agrupar backups por gem
        gems = {}
        for backup_file in self.backups_dir.glob("*.json"):
            # Extraer nombre del gem (antes de _v)
            parts = backup_file.stem.split("_v")
            if parts:
                gem_name = parts[0]
                if gem_name not in gems:
                    gems[gem_name] = []
                gems[gem_name].append(backup_file)
        
        # Limpiar por gem
        for gem_name, backups in gems.items():
            # Ordenar por fecha
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Eliminar excedentes
            for old_backup in backups[keep_count:]:
                old_backup.unlink()
                deleted += 1
        
        return deleted


# CLI para testing standalone
if __name__ == "__main__":
    import sys
    
    updater = GemAutoUpdate()
    
    print("\n" + "="*60)
    print("  GEM AUTO-UPDATE SYSTEM")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nComandos:")
        print("  check              - Verificar actualizaciones")
        print("  history [gem]      - Ver historial de actualizaciones")
        print("  backups [gem]      - Listar backups")
        print("  rollback <gem>     - Rollback a versión anterior")
        print("  cleanup [keep=5]   - Limpiar backups antiguos")
        print("  config             - Ver configuración")
    else:
        cmd = sys.argv[1]
        
        if cmd == "config":
            print(f"\nConfiguración actual:")
            print(f"  Enabled: {updater.config.get('enabled')}")
            print(f"  Check interval: {updater.config.get('check_interval_hours')}h")
            print(f"  Auto-update gems: {updater.config.get('auto_update_gems')}")
            print(f"  Last check: {updater.config.get('last_check')}")
        
        elif cmd == "history":
            gem = sys.argv[2] if len(sys.argv) > 2 else None
            history = updater.get_update_history(gem)
            print(f"\nHistorial de actualizaciones ({len(history)}):")
            for h in history:
                print(f"  - {h['gem_name']}: v{h['old_version']} → v{h['new_version']}")
                print(f"    {h['updated_at']}")
        
        elif cmd == "backups":
            gem = sys.argv[2] if len(sys.argv) > 2 else None
            backups = updater.list_backups(gem)
            print(f"\nBackups disponibles ({len(backups)}):")
            for b in backups:
                print(f"  - {b['name']} ({b['size_kb']:.1f} KB)")
        
        elif cmd == "cleanup":
            keep = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            deleted = updater.cleanup_old_backups(keep)
            print(f"\n✓ Eliminados {deleted} backups antiguos")
