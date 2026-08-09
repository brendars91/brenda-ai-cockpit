"""
Prompt Compiler - Fase 5 del Pipeline Gem Builder

Genera el System Prompt del agente basándose en:
- Use Case Spec (objetivo, dominio, acciones)
- Risk Assessment (políticas de seguridad)
- Model Routing (capacidades del modelo)
- Tool Contracts (herramientas disponibles)

Implementa el protocolo anti-alucinación con Knowledge States.
"""
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class CompiledPrompt:
    """Sistema prompt compilado"""
    text: str
    sha256_hash: str
    tokens_approx: int
    sections: Dict[str, str]


class PromptCompiler:
    """Compilador de System Prompts para Gem Builder"""
    
    def __init__(self):
        self.template_path = Path(__file__).parent.parent / "templates" / "system_prompt.j2"

    def compile(
        self,
        spec: Dict,
        risk_score: int,
        model: str,
        tools: List[Dict]
    ) -> CompiledPrompt:
        """
        Compila el System Prompt del agente.
        
        Args:
            spec: Use Case Spec normalizado
            risk_score: Risk Score del caso de uso
            model: Modelo seleccionado
            tools: Tool Contracts en formato dict
        
        Returns:
            CompiledPrompt con texto, hash y metadata
        """
        sections = {}
        
        # Sección: Domain
        domain = spec.get('domain', 'tareas generales')
        
        # Sección: Goal
        goal = spec.get('goal', 'Completar la tarea solicitada')
        
        # Sección: Data Sources
        sections['data_sources'] = self._compile_data_sources(spec)
        
        # Sección: Actions
        sections['actions'] = self._compile_actions(spec)
        
        # Sección: Tools
        sections['tools'] = self._compile_tools(tools)
        
        # Sección: Rules
        sections['rules'] = self._compile_rules(spec, risk_score)
        
        # Sección: Security
        sections['security'] = self._compile_security(spec, risk_score)
        
        # Sección: Constraints
        sections['constraints'] = self._compile_constraints(spec)
        
        # Generar prompt (primero sin hash para calcular hash correcto)
        prompt_without_hash = self.TEMPLATE.format(
            domain=domain,
            goal=goal,
            data_sources_section=sections['data_sources'],
            actions_section=sections['actions'],
            tools_section=sections['tools'],
            rules_section=sections['rules'],
            security_section=sections['security'],
            constraints_section=sections['constraints'],
            version="1.0.0",
            prompt_hash=""  # Vacío para cálculo de hash
        )
        sections['constraints'] = self._format_constraints(spec)
        
        # Leer template
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")
            
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Renderizar usando simple string replacement por ahora (o Jinja2 si se añade a deps)
        # Para compatibilidad con el formato anterior, usamos .replace manual o f-string simulation
        # Dado que el template usa {{ variable }}, vamos a usar replace simple 
        # NOTA: En un futuro, añadir Jinja2 a requirements.txt
        
        version = "1.0.0" # Define version here
        
        prompt_text = template_content
        replacements = {
            "{{ domain }}": domain,
            "{{ goal }}": goal,
            "{{ data_sources_section }}": sections['data_sources'],
            "{{ actions_section }}": sections['actions'],
            "{{ tools_section }}": sections['tools'],
            "{{ rules_section }}": sections['rules'],
            "{{ security_section }}": sections['security'],
            "{{ constraints_section }}": sections['constraints'],
            "{{ version }}": version,
            "{{ prompt_hash }}": "PENDING_HASH" # Se calcula después
        }
        
        for placeholder, value in replacements.items():
            prompt_text = prompt_text.replace(placeholder, str(value))
        
        # Calcular hash SHA-256 del contenido (sin el hash placeholder)
        # Usamos el texto antes del footer para consistencia
        content_for_hash = prompt_text.replace("| Hash: PENDING_HASH", "| Hash: PLACEHOLDER")
        prompt_hash = hashlib.sha256(content_for_hash.encode('utf-8')).hexdigest()[:12]
        
        # Reemplazar el placeholder del hash con el hash real
        prompt_text = prompt_text.replace("PENDING_HASH", prompt_hash)
        
        # Estimar tokens (aproximación: 4 chars = 1 token)
        tokens_approx = len(prompt_text) // 4
        
        return CompiledPrompt(
            text=prompt_text,
            sha256_hash=prompt_hash,
            tokens_approx=tokens_approx,
            sections=sections
        )
    
    def _compile_data_sources(self, spec: Dict) -> str:
        """Compila sección de data sources"""
        lines = []
        
        for ds in spec.get('data_sources', []):
            ds_type = ds.get('type', 'unknown')
            access = ds.get('access', 'read')
            sensitivity = ds.get('sensitivity', 'internal')
            description = ds.get('description', '')
            
            line = f"- **{ds_type.upper()}** [{access}]: {description}"
            line += f" (Sensibilidad: {sensitivity})"
            lines.append(line)
        
        if not lines:
            return "No hay fuentes de datos definidas."
        
        return "\n".join(lines)
    
    def _compile_actions(self, spec: Dict) -> str:
        """Compila sección de acciones"""
        lines = []
        
        for action in spec.get('actions', []):
            action_type = action.get('type', 'unknown')
            description = action.get('description', '')
            side_effects = action.get('side_effects', False)
            
            icon = "⚠️" if side_effects else "✓"
            line = f"- {icon} **{action_type.upper()}**: {description}"
            if side_effects:
                line += " (SIDE EFFECTS)"
            lines.append(line)
        
        if not lines:
            return "No hay acciones definidas."
        
        return "\n".join(lines)
    
    def _compile_tools(self, tools: List[Dict]) -> str:
        """Compila sección de herramientas"""
        if not tools:
            return "No hay herramientas configuradas."
        
        lines = []
        for tool in tools:
            name = tool.get('name', 'unknown')
            description = tool.get('description', '')
            permissions = tool.get('permissions', ['read'])
            
            perms_str = ", ".join(permissions)
            lines.append(f"- **{name}**: {description} [{perms_str}]")
        
        return "\n".join(lines)
    
    def _compile_rules(self, spec: Dict, risk_score: int) -> str:
        """Compila reglas inviolables"""
        rules = [
            "1. NUNCA inventar datos no verificados",
            "2. NUNCA ejecutar acciones de escritura sin confirmación explícita",
            "3. SIEMPRE citar fuentes de información",
            "4. SIEMPRE usar Knowledge States apropiados",
        ]
        
        # Reglas adicionales según risk score
        if risk_score > 60:
            rules.append("5. SIEMPRE usar dry-run antes de ejecutar")
            rules.append("6. NUNCA proceder sin HITL en operaciones críticas")
        
        if risk_score > 80:
            rules.append("7. MODO READ-ONLY activo - NO modificar datos")
        
        # Reglas del spec
        if spec.get('security', {}).get('read_only'):
            rules.append("⚠️ MODO READ-ONLY: Solo lectura permitida")
        
        return "\n".join(rules)
    
    def _compile_security(self, spec: Dict, risk_score: int) -> str:
        """Compila sección de seguridad"""
        lines = [f"- **Risk Score**: {risk_score}/100"]
        
        if risk_score <= 30:
            lines.append("- **Risk Level**: LOW - Políticas estándar")
        elif risk_score <= 60:
            lines.append("- **Risk Level**: MEDIUM - Model Armor activado")
        else:
            lines.append("- **Risk Level**: HIGH - HITL obligatorio, dry-run activo")
        
        # HITL
        hitl = spec.get('security', {}).get('hitl_required', 'auto')
        lines.append(f"- **HITL**: {hitl.upper()}")
        
        # Model Armor
        armor = risk_score > 30
        lines.append(f"- **Model Armor**: {'ON' if armor else 'OFF'}")
        
        return "\n".join(lines)
    
    def _compile_constraints(self, spec: Dict) -> str:
        """Compila sección de restricciones"""
        constraints = spec.get('constraints', {})
        lines = []
        
        latency = constraints.get('latency_ms', 5000)
        lines.append(f"- **Latencia máxima**: {latency}ms")
        
        cost_tier = constraints.get('cost_tier', 'medium')
        lines.append(f"- **Cost tier**: {cost_tier.upper()}")
        
        max_tokens = constraints.get('max_tokens')
        if max_tokens:
            lines.append(f"- **Tokens máximos**: {max_tokens}")
        
        # Output type
        output_type = spec.get('output', {}).get('type', 'text')
        lines.append(f"- **Formato output**: {output_type.upper()}")
        
        return "\n".join(lines)
    
    def to_bundle_format(self, compiled: CompiledPrompt) -> Dict:
        """
        Convierte CompiledPrompt a formato del Gem Bundle.
        
        Args:
            compiled: CompiledPrompt
        
        Returns:
            Dict para el bundle
        """
        return {
            "text": compiled.text,
            "sha256_hash": compiled.sha256_hash,
            "tokens_approx": compiled.tokens_approx,
            "sections": list(compiled.sections.keys())
        }


# CLI para testing standalone
if __name__ == "__main__":
    import json
    
    # Test
    test_spec = {
        "use_case_id": "doc_analyzer",
        "domain": "document-analysis",
        "goal": "Analizar documentos de proyecto y generar resúmenes ejecutivos",
        "data_sources": [
            {"type": "drive", "access": "read", "sensitivity": "internal", 
             "description": "Documentos de Drive"}
        ],
        "actions": [
            {"type": "read", "description": "Leer documentos"},
            {"type": "summarize", "description": "Generar resumen"}
        ],
        "constraints": {"latency_ms": 5000, "cost_tier": "low"},
        "security": {"hitl_required": "auto"},
        "output": {"type": "markdown"}
    }
    
    test_tools = [
        {"name": "google-drive", "description": "Acceso a Drive", "permissions": ["read"]},
        {"name": "filesystem", "description": "Archivos locales", "permissions": ["read"]}
    ]
    
    compiler = PromptCompiler()
    result = compiler.compile(test_spec, risk_score=25, model="gemini-flash", tools=test_tools)
    
    print("\n" + "="*60)
    print("  PROMPT COMPILER TEST")
    print("="*60)
    
    print(f"\nPrompt length: {len(result.text)} chars")
    print(f"Tokens approx: {result.tokens_approx}")
    print(f"SHA-256: {result.sha256_hash}")
    print(f"Sections: {list(result.sections.keys())}")
    
    print("\n--- COMPILED PROMPT ---\n")
    print(result.text[:2000] + "..." if len(result.text) > 2000 else result.text)
