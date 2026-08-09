"""
Tool Planner - Fase 4 del Pipeline Gem Builder

Selecciona y configura herramientas (MCPs) necesarias basándose en:
- Fuentes de datos del Use Case Spec
- Risk Score y políticas de seguridad
- Whitelist de MCPs permitidos

Genera Tool Contracts compatibles con MCP Protocol.
"""
from typing import Dict, List
from dataclasses import dataclass, field


@dataclass
class ToolContract:
    """Contrato de herramienta para el Gem Bundle"""
    name: str
    description: str
    side_effects: bool = False
    dry_run_default: bool = False
    timeout_ms: int = 5000
    permissions: List[str] = field(default_factory=list)


class ToolPlanner:
    """Planificador de herramientas para Gem Builder"""
    
    # Mapeo de data source types a MCPs
    DATASOURCE_TO_MCP = {
        'file': 'filesystem',
        'db': 'database',
        'api': 'fetch',
        'url': 'fetch',
        'drive': 'google-drive',
        'notion': 'notion',
        'mcp': 'filesystem'  # Generic MCP access
    }
    
    # MCPs de seguridad (siempre incluidos si Risk > 30)
    SECURITY_MCPS = ['snyk']
    
    # MCPs de grounding (si se requiere grounding)
    GROUNDING_MCPS = ['context7', 'google-search']
    
    # MCPs de alto riesgo (requieren dry_run)
    HIGH_RISK_MCPS = ['execute', 'code-sandbox', 'deploy']
    
    # Whitelist de MCPs permitidos (configurables)
    DEFAULT_WHITELIST = {
        'filesystem', 'fetch', 'database', 'snyk', 
        'context7', 'google-drive', 'opa'
    }
    
    def __init__(self, whitelist: set = None):
        """
        Args:
            whitelist: Set de MCPs permitidos. Si None, usa whitelist por defecto.
        """
        self.whitelist = whitelist or self.DEFAULT_WHITELIST
    
    def plan(
        self, 
        spec: Dict, 
        risk_score: int
    ) -> List[ToolContract]:
        """
        Planifica herramientas necesarias para el Use Case.
        
        Args:
            spec: Use Case Spec normalizado
            risk_score: Risk Score del caso de uso
        
        Returns:
            Lista de ToolContracts
        """
        tools = []
        added_mcps = set()
        
        # 1. MCPs de data sources
        for ds in spec.get('data_sources', []):
            ds_type = ds.get('type', 'file')
            mcp_name = self.DATASOURCE_TO_MCP.get(ds_type, 'filesystem')
            
            if mcp_name in self.whitelist and mcp_name not in added_mcps:
                tools.append(self._create_contract(
                    name=mcp_name,
                    description=f"Acceso a {ds_type}: {ds.get('description', '')}",
                    side_effects=ds.get('access') in ['write', 'read_write'],
                    dry_run_default=risk_score > 60
                ))
                added_mcps.add(mcp_name)
        
        # 2. MCPs de seguridad (si Risk > 30)
        if risk_score > 30:
            for mcp in self.SECURITY_MCPS:
                if mcp in self.whitelist and mcp not in added_mcps:
                    tools.append(self._create_contract(
                        name=mcp,
                        description="Escaneo de seguridad y vulnerabilidades",
                        side_effects=False,
                        timeout_ms=30000  # Scans pueden tardar
                    ))
                    added_mcps.add(mcp)
        
        # 3. MCPs de grounding (si se requiere)
        grounding_config = spec.get('grounding', {})
        if grounding_config.get('required'):
            grounding_sources = grounding_config.get('sources', ['context7'])
            for source in grounding_sources:
                if source in self.whitelist and source not in added_mcps:
                    tools.append(self._create_contract(
                        name=source,
                        description=f"Grounding: {source}",
                        side_effects=False
                    ))
                    added_mcps.add(source)
        
        # 4. Filesystem siempre incluido (core)
        if 'filesystem' in self.whitelist and 'filesystem' not in added_mcps:
            tools.append(self._create_contract(
                name='filesystem',
                description="Lectura y escritura de archivos locales",
                side_effects=self._has_write_actions(spec),
                dry_run_default=risk_score > 60
            ))
            added_mcps.add('filesystem')
        
        # 5. Fetch siempre incluido (core - acceso HTTP)
        if 'fetch' in self.whitelist and 'fetch' not in added_mcps:
            tools.append(self._create_contract(
                name='fetch',
                description="Acceso HTTP a URLs y APIs externas",
                side_effects=False,
                dry_run_default=False
            ))
            added_mcps.add('fetch')
        
        # 5. Ajustar permissions según security config
        security_config = spec.get('security', {})
        allowed_tools = security_config.get('allowed_tools', [])
        read_only = security_config.get('read_only', False)
        
        # Filtrar herramientas por whitelist explícita del spec
        if allowed_tools:
            tools = [t for t in tools if t.name in allowed_tools or t.name in self.SECURITY_MCPS]
        
        # Si read_only, marcar todas como sin side_effects
        if read_only:
            for tool in tools:
                tool.side_effects = False
                tool.dry_run_default = True
                tool.permissions = ['read']
        
        return tools
    
    def _create_contract(
        self,
        name: str,
        description: str,
        side_effects: bool = False,
        dry_run_default: bool = False,
        timeout_ms: int = 5000
    ) -> ToolContract:
        """Crea un ToolContract con configuración estándar"""
        permissions = ['read']
        if side_effects:
            permissions.append('write')
        
        return ToolContract(
            name=name,
            description=description,
            side_effects=side_effects,
            dry_run_default=dry_run_default,
            timeout_ms=timeout_ms,
            permissions=permissions
        )
    
    def _has_write_actions(self, spec: Dict) -> bool:
        """Verifica si hay acciones de escritura"""
        return any(
            action.get('type') in ['write', 'execute', 'transform']
            or action.get('side_effects', False)
            for action in spec.get('actions', [])
        )
    
    def to_bundle_format(self, tools: List[ToolContract]) -> List[Dict]:
        """
        Convierte ToolContracts a formato del Gem Bundle.
        
        Args:
            tools: Lista de ToolContracts
        
        Returns:
            Lista de dicts para el bundle
        """
        return [
            {
                "name": t.name,
                "description": t.description,
                "side_effects": t.side_effects,
                "dry_run_default": t.dry_run_default,
                "timeout_ms": t.timeout_ms,
                "permissions": t.permissions
            }
            for t in tools
        ]


# CLI para testing standalone
if __name__ == "__main__":
    import json
    
    # Test spec
    test_spec = {
        "use_case_id": "doc_analyzer",
        "data_sources": [
            {"type": "drive", "access": "read", "sensitivity": "internal"},
            {"type": "api", "access": "read"}
        ],
        "actions": [
            {"type": "read"},
            {"type": "analyze"}
        ],
        "grounding": {"required": True, "sources": ["context7"]},
        "security": {"read_only": True}
    }
    
    planner = ToolPlanner()
    tools = planner.plan(test_spec, risk_score=45)
    
    print("\n" + "="*60)
    print("  TOOL PLANNER TEST")
    print("="*60)
    
    print(f"\nTools selected ({len(tools)}):")
    for tool in tools:
        print(f"\n  📦 {tool.name}")
        print(f"     Description: {tool.description}")
        print(f"     Side Effects: {tool.side_effects}")
        print(f"     Dry Run: {tool.dry_run_default}")
        print(f"     Permissions: {tool.permissions}")
    
    print(f"\n\nBundle format:")
    print(json.dumps(planner.to_bundle_format(tools), indent=2))
