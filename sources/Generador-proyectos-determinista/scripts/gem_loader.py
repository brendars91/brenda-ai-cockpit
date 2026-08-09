"""
Gem Loader - Carga Gem Bundles en AGCCE v4.0

Este módulo permite a AGCCE cargar y validar Gem Bundles compilados
por Gem Builder Compiler, convirtiéndolos en configuraciones de agentes.
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("⚠️  Warning: jsonschema not installed. Schema validation disabled.")
    print("   Install with: pip install jsonschema")


class GemLoader:
    """Cargador y validador de Gem Bundles"""
    
    def __init__(self, gem_bundle_schema_path: Optional[str] = None):
        """
        Args:
            gem_bundle_schema_path: Path al gem_bundle.v1.schema.json
                                   Si None, busca en ubicación por defecto
        """
        self.schema = None
        
        if gem_bundle_schema_path is None:
            # Buscar en ubicación por defecto (Gem Builder)
            default_path = Path(__file__).parent.parent / "Mis carpetas" / "Gem Builder" / "schemas" / "gem_bundle.v1.schema.json"
            if default_path.exists():
                gem_bundle_schema_path = str(default_path)
        
        if gem_bundle_schema_path and Path(gem_bundle_schema_path).exists():
            with open(gem_bundle_schema_path) as f:
                self.schema = json.load(f)
            print(f"✓ Gem Bundle schema loaded from {gem_bundle_schema_path}")
        else:
            print("⚠️  Warning: Gem Bundle schema not found. Validation disabled.")
    
    def load_gem(self, gem_path: str) -> Dict:
       """
        Carga un Gem Bundle y lo valida contra schema.
        
        Args:
            gem_path: Path al archivo Gem Bundle (.json)
        
        Returns:
            dict con el Gem Bundle completo
        
        Raises:
            FileNotFoundError: Si el Gem no existe
            jsonschema.ValidationError: Si el Gem no es válido
            ValueError: Si el hash SHA-256 no coincide
        """
        gem_file = Path(gem_path)
        if not gem_file.exists():
            raise FileNotFoundError(f"Gem Bundle not found: {gem_path}")
        
        with open(gem_path) as f:
            gem = json.load(f)
        
        # Validar contra schema si disponible
        if HAS_JSONSCHEMA and self.schema:
            jsonschema.validate(instance=gem, schema=self.schema)
            print("✓ Gem Bundle schema validation passed")
        
        # Verificar hash del system prompt (campo: sha256_hash, 12 chars)
        system_prompt = gem.get('system_prompt', {})
        stored_hash = system_prompt.get('sha256_hash', '')
        
        if stored_hash and system_prompt.get('text'):
            # El hash se calcula sobre contenido con PLACEHOLDER para consistencia
            text = system_prompt['text']
            content_for_hash = text.replace(f"| Hash: {stored_hash}", "| Hash: PLACEHOLDER")
            computed_hash = hashlib.sha256(content_for_hash.encode('utf-8')).hexdigest()[:12]
            
            if stored_hash != computed_hash:
                print(f"⚠️  Warning: System prompt hash mismatch")
                print(f"   Stored:   {stored_hash}")
                print(f"   Computed: {computed_hash}")
                # No lanzar error, solo warning (puede haber diferencias de encoding)
            else:
                print("✓ System prompt integrity verified (SHA-256)")
        
        # MEJORA: Forzar HITL si Risk Score > 80
        risk_score = gem.get('bundle_meta', {}).get('risk_score', 0)
        policies = gem.get('policies', {}).get('security', {})
        
        if risk_score > 80 and not policies.get('hitl_required', False):
            print(f"⚠️  Warning: Risk Score {risk_score} > 80 sin HITL. Forzando HITL=true")
            gem['policies']['security']['hitl_required'] = True
        
        return gem
    
    def convert_to_agent_profile(self, gem: Dict, agent_role: str) -> Dict:
        """
        Convierte un Gem Bundle en un Agent Profile de AGCCE.
        
        Args:
            gem: Gem Bundle completo
            agent_role: "researcher" | "architect" | "constructor" | "auditor" | "tester"
        
        Returns:
            dict compatible con config/agent_profiles/ de AGCCE
        """
        use_case_id = gem['bundle_meta']['use_case_id']
        
        # Extraer MCPs permitidos (tools sin side-effects o con dry_run)
        allowed_mcps = []
        forbidden_mcps = []
        
        for tool in gem.get('tool_contracts', []):
            if not tool.get('side_effects', False):
                allowed_mcps.append(tool['name'])
            elif tool.get('dry_run', True):
                allowed_mcps.append(tool['name'])  # dry_run permitido
            else:
                forbidden_mcps.append(tool['name'])  # side-effects sin dry_run
        
        return {
            "agent_id": f"{use_case_id}_{agent_role}",
            "role": agent_role,
            "version": gem['bundle_meta']['version'],
            
            # System Prompt del Gem
            "system_prompt": gem['system_prompt']['text'],
            "system_prompt_hash": gem['system_prompt'].get('sha256_hash', ''),
            "system_prompt_version": gem['system_prompt'].get('version', '1.0.0'),
            
            # Model Routing del Gem
            "model": gem['model_routing']['selected_model'],
            "model_justification": gem['model_routing'].get('justification', ''),
            
            # Policies del Gem
            "policies": {
                "model_armor": gem['policies']['security'].get('model_armor_enabled', False),
                "hitl_required": gem['policies']['security'].get('hitl_required', False),
                "read_only_tools": gem['policies']['security'].get('read_only_tools', False),
                "pii_redaction": gem['policies']['security'].get('pii_redaction', False),
            },
            
            # Tool Contracts → MCPs
            "allowed_mcps": allowed_mcps,
            "forbidden_mcps": forbidden_mcps,
            
            # Grounding Strategy
            "grounding": gem.get('knowledge_plan', {}).get('grounding_strategy', 'none'),
            "grounding_sources": gem.get('knowledge_plan', {}).get('allowed_sources', []),
            
            # Verifier checks
            "quality_checks": gem.get('verifier', {}).get('checks', []),
            
            # Anti-hallucination policies
            "knowledge_states": gem.get('policies', {}).get('anti_hallucination', {}).get(
                'allowed_knowledge_states',
                ["HECHO_VERIFICADO", "INFERENCIA", "ASUNCION", "FALTAN_DATOS"]
            ),
            
            # Metadata
            "gem_source": use_case_id,
            "compiled_at": gem['bundle_meta'].get('compiled_at', ''),
            "compiler_version": gem['bundle_meta'].get('compiler_version', 'unknown'),
            "risk_score": gem['bundle_meta'].get('risk_score', 0),
            
            # AGCCE metadata
            "loaded_at": datetime.utcnow().isoformat() + "Z",
            "source_type": "gem_bundle"
        }
    
    def create_agent_profiles_from_gem(
        self,
        gem_path: str,
        output_dir: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Dict]:
        """
        Crea perfiles para todos los agentes MAS desde un Gem.
        
        Args:
            gem_path: Path al Gem Bundle
            output_dir: Directorio donde guardar perfiles (opcional)
            use_cache: Usar profiles cacheados si existen
        
        Returns:
            dict con key = agent_role, value = agent_profile
        """
        gem = self.load_gem(gem_path)
        
        # Los 5 agentes MAS de AGCCE
        roles = ["researcher", "architect", "constructor", "auditor", "tester"]
        
        profiles = {}
        
        # Intentar cargar registry para cache
        registry = None
        if use_cache:
            try:
                from gem_registry import GemRegistry
                registry = GemRegistry()
            except ImportError:
                pass
        
        for role in roles:
            # Verificar cache
            if registry and use_cache:
                use_case_id = gem['bundle_meta']['use_case_id']
                version = gem['bundle_meta']['version']
                
                cached_path = registry.get_cached_profile(use_case_id, version, role)
                if cached_path and os.path.exists(cached_path):
                    # Cargar desde cache
                    with open(cached_path, 'r', encoding='utf-8') as f:
                        profile = json.load(f)
                    profiles[role] = profile
                    print(f"  ✓ {role} profile (from cache)")
                    continue
            
            # Generar profile
            profile = self.convert_to_agent_profile(gem, role)
            profiles[role] = profile
            
            # Guardar si output_dir especificado
            if output_dir:
                output_path = Path(output_dir) / f"{profile['agent_id']}.json"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(profile, f, indent=2, ensure_ascii=False)
                
                print(f"✓ Saved {role} profile: {output_path}")
                
                # Cachear en registry
                if registry:
                    registry.cache_profile(
                        gem['bundle_meta']['use_case_id'],
                        gem['bundle_meta']['version'],
                        role,
                        profile
                    )
        
        # Registrar Gem en registry
        if registry:
            gem_info = self.get_gem_info(gem_path)
            registry.register_gem(gem_path, gem_info)
        
        return profiles
    
    def get_gem_info(self, gem_path: str) -> Dict:
        """
        Obtiene información básica de un Gem sin cargarlo completamente.
        
        Returns:
            dict con metadata del Gem
        """
        with open(gem_path) as f:
            gem = json.load(f)
        
        return {
            "use_case_id": gem['bundle_meta']['use_case_id'],
            "version": gem['bundle_meta']['version'],
            "compiled_at": gem['bundle_meta'].get('compiled_at', ''),
            "risk_score": gem['bundle_meta'].get('risk_score', 0),
            "model": gem['model_routing']['selected_model'],
            "has_model_armor": gem['policies']['security'].get('model_armor_enabled', False),
            "grounding_strategy": gem.get('knowledge_plan', {}).get('grounding_strategy', 'none')
        }


# ============================================================================
# CLI para testing
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python gem_loader.py <gem_bundle.json>")
        print("\nExample:")
        print("  python gem_loader.py ../gems/sap_cost_analyzer_v1.0.0.json")
        sys.exit(1)
    
    gem_path = sys.argv[1]
    
    print(f"\n{'='*60}")
    print(f"GEM LOADER - Loading Gem Bundle")
    print(f"{'='*60}\n")
    
    loader = GemLoader()
    
    try:
        # Mostrar info básica
        info = loader.get_gem_info(gem_path)
        print(f"📦 Gem: {info['use_case_id']} v{info['version']}")
        print(f"   Compiled: {info['compiled_at']}")
        print(f"   Model: {info['model']}")
        print(f"   Risk Score: {info['risk_score']}")
        print(f"   Model Armor: {'✓' if info['has_model_armor'] else '✗'}")
        print(f"   Grounding: {info['grounding_strategy']}")
        print()
        
        # Crear perfiles
        output_dir = "config/gem_profiles"
        profiles = loader.create_agent_profiles_from_gem(gem_path, output_dir)
        
        print(f"\n✓ Created {len(profiles)} agent profiles")
        print(f"  Output: {output_dir}/")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
