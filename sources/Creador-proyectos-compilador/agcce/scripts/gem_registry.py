"""
Gem Registry - Gestión de versiones de Gem Bundles

Permite:
- Registrar Gems importados
- Validar compatibilidad de versiones
- Cache de Agent Profiles generados
- Tracking de Gems activos
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib


class GemRegistry:
    """Registry local de Gem Bundles"""
    
    def __init__(self, registry_path: str = "config/gem_registry.json"):
        self.registry_path = registry_path
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Carga registry desde disco o crea uno nuevo"""
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "version": "1.0.0",
            "gems": {},
            "profiles_cache": {},
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def _save_registry(self):
        """Guarda registry a disco"""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
    
    def register_gem(
        self,
        gem_path: str,
        gem_metadata: Dict,
        force: bool = False
    ) -> bool:
        """
        Registra un Gem en el registry.
        
        Args:
            gem_path: Path al Gem Bundle
            gem_metadata: Metadata del Gem (de gem_loader.get_gem_info)
            force: Sobrescribir si ya existe
        
        Returns:
            True si se registró exitosamente
        """
        use_case_id = gem_metadata['use_case_id']
        version = gem_metadata['version']
        
        # Verificar si ya existe
        if use_case_id in self.registry['gems']:
            existing_versions = self.registry['gems'][use_case_id].get('versions', {})
            if version in existing_versions and not force:
                print(f"⚠️  Gem {use_case_id} v{version} ya registrado. Use force=True para sobrescribir.")
                return False
        
        # Calcular hash del archivo
        with open(gem_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Registrar
        if use_case_id not in self.registry['gems']:
            self.registry['gems'][use_case_id] = {
                "name": use_case_id,
                "versions": {},
                "latest_version": version
            }
        
        self.registry['gems'][use_case_id]['versions'][version] = {
            "file_path": gem_path,
            "file_hash": file_hash,
            "model": gem_metadata['model'],
            "risk_score": gem_metadata['risk_score'],
            "registered_at": datetime.utcnow().isoformat() + "Z",
            "last_used": None,
            "usage_count": 0
        }
        
        # Actualizar latest_version si es mayor (SemVer)
        if self._is_newer_version(version, self.registry['gems'][use_case_id]['latest_version']):
            self.registry['gems'][use_case_id]['latest_version'] = version
        
        self._save_registry()
        print(f"✓ Gem registrado: {use_case_id} v{version}")
        return True
    
    def _is_newer_version(self, v1: str, v2: str) -> bool:
        """Compara versiones SemVer (simple)"""
        def parse_version(v):
            return tuple(map(int, v.split('.')))
        
        try:
            return parse_version(v1) > parse_version(v2)
        except:
            return False
    
    def get_gem(self, use_case_id: str, version: Optional[str] = None) -> Optional[Dict]:
        """
        Obtiene info de un Gem registrado.
        
        Args:
            use_case_id: ID del Gem
            version: Versión específica (None = latest)
        
        Returns:
            Metadata del Gem o None
        """
        if use_case_id not in self.registry['gems']:
            return None
        
        gem_entry = self.registry['gems'][use_case_id]
        
        if version is None:
            version = gem_entry['latest_version']
        
        if version not in gem_entry['versions']:
            return None
        
        return {
            "use_case_id": use_case_id,
            "version": version,
            **gem_entry['versions'][version]
        }
    
    def list_gems(self) -> List[Dict]:
        """Lista todos los Gems registrados"""
        gems = []
        for use_case_id, gem_data in self.registry['gems'].items():
            for version, version_data in gem_data['versions'].items():
                gems.append({
                    "use_case_id": use_case_id,
                    "version": version,
                    "is_latest": version == gem_data['latest_version'],
                    **version_data
                })
        return sorted(gems, key=lambda x: (x['use_case_id'], x['version']))
    
    def record_usage(self, use_case_id: str, version: str):
        """Registra uso de un Gem"""
        if use_case_id not in self.registry['gems']:
            return
        
        if version not in self.registry['gems'][use_case_id]['versions']:
            return
        
        gem_version = self.registry['gems'][use_case_id]['versions'][version]
        gem_version['last_used'] = datetime.utcnow().isoformat() + "Z"
        gem_version['usage_count'] = gem_version.get('usage_count', 0) + 1
        
        self._save_registry()
    
    def cache_profile(self, use_case_id: str, version: str, role: str, profile: Dict):
        """
        Cachea un Agent Profile generado desde un Gem.
        
        Evita regenerar profiles cada vez que se carga el mismo Gem.
        """
        cache_key = f"{use_case_id}_{version}_{role}"
        
        # Calcular hash del profile
        profile_str = json.dumps(profile, sort_keys=True)
        profile_hash = hashlib.sha256(profile_str.encode()).hexdigest()
        
        self.registry['profiles_cache'][cache_key] = {
            "use_case_id": use_case_id,
            "version": version,
            "role": role,
            "profile_hash": profile_hash,
            "cached_at": datetime.utcnow().isoformat() + "Z"
        }
        
        self._save_registry()
        print(f"  ✓ Profile cacheado: {cache_key}")
    
    def get_cached_profile(self, use_case_id: str, version: str, role: str) -> Optional[str]:
        """
        Obtiene path del profile cacheado (si existe y es válido).
        
        Returns:
            Path al profile cacheado o None
        """
        cache_key = f"{use_case_id}_{version}_{role}"
        
        if cache_key not in self.registry['profiles_cache']:
            return None
        
        # Verificar que el archivo existe
        profile_path = f"config/gem_profiles/{use_case_id}_{role}.json"
        if not os.path.exists(profile_path):
            return None
        
        return profile_path
    
    def stats(self) -> Dict:
        """Estadísticas del registry"""
        total_gems = sum(len(g['versions']) for g in self.registry['gems'].values())
        total_use_cases = len(self.registry['gems'])
        cached_profiles = len(self.registry['profiles_cache'])
        
        most_used = None
        max_usage = 0
        for use_case_id, gem_data in self.registry['gems'].items():
            for version, version_data in gem_data['versions'].items():
                usage = version_data.get('usage_count', 0)
                if usage > max_usage:
                    max_usage = usage
                    most_used = f"{use_case_id} v{version}"
        
        return {
            "total_gems": total_gems,
            "total_use_cases": total_use_cases,
            "cached_profiles": cached_profiles,
            "most_used_gem": most_used if most_used else "N/A",
            "most_used_count": max_usage
        }


# CLI para testing
if __name__ == "__main__":
    import sys
    
    registry = GemRegistry()
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python gem_registry.py list")
        print("  python gem_registry.py stats")
        print("  python gem_registry.py show <use_case_id>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "list":
        print("\n=== GEM REGISTRY ===\n")
        gems = registry.list_gems()
        if not gems:
            print("No hay Gems registrados")
        else:
            for gem in gems:
                latest = " (LATEST)" if gem['is_latest'] else ""
                print(f"📦 {gem['use_case_id']} v{gem['version']}{latest}")
                print(f"   Model: {gem['model']}, Risk: {gem['risk_score']}")
                print(f"   Usado: {gem.get('usage_count', 0)} veces")
                print()
    
    elif cmd == "stats":
        print("\n=== ESTADÍSTICAS ===\n")
        stats = registry.stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    elif cmd == "show" and len(sys.argv) >= 3:
        use_case_id = sys.argv[2]
        gem = registry.get_gem(use_case_id)
        if gem:
            print(json.dumps(gem, indent=2))
        else:
            print(f"Gem '{use_case_id}' no encontrado")
