"""
Verifier Gate - Fase 6 del Pipeline Gem Builder

Validaciones finales del Gem Bundle antes de guardarlo:
1. Schema Validation - Validar contra gem_bundle.v1.schema.json
2. Grounding Check - Verificar coherencia de grounding strategy
3. Security Check - Validar políticas según Risk Score
4. Ghost Entity Detection - Buscar referencias a entidades no definidas

Si pasa todas las validaciones, marca el bundle como "verified".
"""
import re
import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class VerificationResult:
    """Resultado de la verificación del Gem Bundle"""
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks_passed: List[str] = field(default_factory=list)


class VerifierGate:
    """Verifier Gate para Gem Builder"""
    
    def __init__(self, schema_path: str = None):
        """
        Args:
            schema_path: Path al schema de Gem Bundle
        """
        if schema_path is None:
            # Resolver path relativo a la raíz del proyecto (asumiendo src/verifier_gate.py)
            project_root = Path(__file__).parent.parent
            schema_path = project_root / "schemas" / "gem_bundle.v1.schema.json"
        else:
            schema_path = Path(schema_path)
            
        self.schema_path = schema_path
        
        # Cargar schema si existe
        if self.schema_path.exists():
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
        else:
            self.schema = None
    
    def verify(self, gem_bundle: Dict, risk_score: int = 0) -> VerificationResult:
        """
        Ejecuta todas las verificaciones del Gem Bundle.
        
        Args:
            gem_bundle: Bundle a verificar
            risk_score: Risk Score original (para validar coherencia)
        
        Returns:
            VerificationResult con resultado de todas las verificaciones
        """
        errors = []
        warnings = []
        checks_passed = []
        
        # Check 1: Schema Validation
        schema_result = self._check_schema(gem_bundle)
        if schema_result[0]:
            checks_passed.append("schema")
        else:
            errors.extend(schema_result[1])
        
        # Check 2: Grounding Coherence
        grounding_result = self._check_grounding(gem_bundle)
        if grounding_result[0]:
            checks_passed.append("grounding")
        else:
            errors.extend(grounding_result[1])
        warnings.extend(grounding_result[2])
        
        # Check 3: Security Policies
        security_result = self._check_security(gem_bundle, risk_score)
        if security_result[0]:
            checks_passed.append("security")
        else:
            errors.extend(security_result[1])
        warnings.extend(security_result[2])
        
        # Check 4: Ghost Entities
        ghost_result = self._check_ghost_entities(gem_bundle)
        if ghost_result[0]:
            checks_passed.append("ghost_entities")
        else:
            errors.extend(ghost_result[1])
        
        # Determinar si pasó
        passed = len(errors) == 0
        
        return VerificationResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            checks_passed=checks_passed
        )
    
    def _check_schema(self, bundle: Dict) -> Tuple[bool, List[str]]:
        """Valida el bundle contra el JSON Schema"""
        errors = []
        
        if self.schema is None:
            # Si no hay schema, hacer validación básica
            required_fields = ['bundle_meta', 'model_routing', 'policies', 'system_prompt']
            for field in required_fields:
                if field not in bundle:
                    errors.append(f"Campo requerido faltante: {field}")
            
            if 'bundle_meta' in bundle:
                meta = bundle['bundle_meta']
                if 'use_case_id' not in meta:
                    errors.append("bundle_meta.use_case_id es requerido")
                if 'version' not in meta:
                    errors.append("bundle_meta.version es requerido")
            
            return len(errors) == 0, errors
        
        # Validar contra schema
        try:
            jsonschema.validate(instance=bundle, schema=self.schema)
            return True, []
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
            return False, errors
    
    def _check_grounding(self, bundle: Dict) -> Tuple[bool, List[str], List[str]]:
        """Verifica coherencia de grounding strategy"""
        errors = []
        warnings = []
        
        prompt_text = bundle.get('system_prompt', {}).get('text', '')
        tools = bundle.get('tools', {}).get('contracts', [])
        tool_names = [t.get('name', '') for t in tools]
        
        # Verificar si menciona grounding y tiene herramientas
        mentions_grounding = any(
            keyword in prompt_text.lower() 
            for keyword in ['grounding', 'verificar', 'fuente', 'confirmar']
        )
        
        has_grounding_tools = any(
            name in ['context7', 'google-search', 'rag']
            for name in tool_names
        )
        
        # Advertencia si menciona grounding sin herramientas
        if mentions_grounding and not has_grounding_tools:
            warnings.append(
                "El prompt menciona grounding pero no hay herramientas de grounding configuradas"
            )
        
        # Verificar knowledge_states en políticas
        policies = bundle.get('policies', {})
        if 'knowledge_states' not in policies:
            errors.append("policies.knowledge_states es requerido para anti-alucinación")
        else:
            required_states = ['HECHO_VERIFICADO', 'FALTAN_DATOS']
            for state in required_states:
                if state not in policies['knowledge_states']:
                    errors.append(f"Knowledge state faltante: {state}")
        
        return len(errors) == 0, errors, warnings
    
    def _check_security(
        self, 
        bundle: Dict, 
        risk_score: int
    ) -> Tuple[bool, List[str], List[str]]:
        """Verifica políticas de seguridad según Risk Score"""
        errors = []
        warnings = []
        
        policies = bundle.get('policies', {})
        bundle_risk = bundle.get('bundle_meta', {}).get('risk_score', 0)
        
        # Usar risk_score del bundle si no se proporciona
        if risk_score == 0:
            risk_score = bundle_risk
        
        # HIGH Risk (>60) debe tener Model Armor
        if risk_score > 60:
            if not policies.get('model_armor_enabled', False):
                errors.append(
                    f"Risk Score {risk_score} (HIGH) requiere model_armor_enabled=true"
                )
            if not policies.get('hitl_required', False):
                warnings.append(
                    f"Risk Score {risk_score} (HIGH) recomienda hitl_required=true"
                )
        
        # MEDIUM Risk (30-60) recomienda Model Armor
        elif risk_score > 30:
            if not policies.get('model_armor_enabled', False):
                warnings.append(
                    f"Risk Score {risk_score} (MEDIUM) recomienda model_armor_enabled=true"
                )
        
        # Verificar coherencia de tools con risk
        tools = bundle.get('tools', {}).get('contracts', [])
        for tool in tools:
            if tool.get('side_effects', False) and risk_score > 60:
                if not tool.get('dry_run_default', False):
                    warnings.append(
                        f"Tool '{tool.get('name')}' tiene side_effects pero dry_run_default=false "
                        f"(recomendado para Risk {risk_score})"
                    )
        
        return len(errors) == 0, errors, warnings
    
    def _check_ghost_entities(self, bundle: Dict) -> Tuple[bool, List[str]]:
        """Detecta referencias a entidades no definidas (ghost entities)"""
        errors = []
        
        prompt_text = bundle.get('system_prompt', {}).get('text', '')
        tools = bundle.get('tools', {}).get('contracts', [])
        tool_names = {t.get('name', '').lower() for t in tools}
        
        # Patrones específicos que indican USO de una herramienta
        # (no solo mención casual)
        usage_patterns = [
            r'usa\s+(?:la\s+herramienta\s+)?(\w+[-\w]*)\s+para',  # "usa X para"
            r'utiliza\s+(\w+[-\w]*)\s+para',  # "utiliza X para"
            r'con\s+(?:la\s+herramienta\s+)?(\w+[-\w]*)[\s,]',  # "con X,"
            r'mediante\s+(\w+[-\w]*)',  # "mediante X"
            r'(\w+[-\w]*)\s+MCP',  # "X MCP"
            r'herramienta\s+(\w+[-\w]*)',  # "herramienta X"
        ]
        
        mentioned_tools = set()
        for pattern in usage_patterns:
            matches = re.findall(pattern, prompt_text.lower())
            mentioned_tools.update(matches)
        
        # Keywords genéricas que NO son ghost entities
        safe_keywords = {
            # Artículos y preposiciones
            'que', 'el', 'la', 'los', 'las', 'un', 'una', 'para', 'con', 'de', 'en',
            # Tipos de acciones
            'read', 'write', 'analyze', 'summarize', 'execute', 'transform', 'export',
            # Entidades genéricas
            'user', 'data', 'file', 'document', 'información', 'datos', 'archivo',
            'base', 'fuente', 'herramienta', 'herramientas', 'apropiados',
            'apropiadas', 'disponibles', 'verificar', 'confirmar',
            # Palabras comunes en prompts que causan falsos positivos
            'análisis', 'insights', 'sentimiento', 'resumen', 'documento',
            'contenido', 'resultado', 'formato', 'markdown', 'texto',
            'generar', 'crear', 'procesar', 'extraer', 'estructura',
            'estructurado', 'output', 'input', 'respuesta', 'solicitud',
            # Conceptos de dominio
            'proyecto', 'tarea', 'objetivo', 'contexto', 'fuentes'
        }
        
        # Solo reportar si hay patrones MUY específicos de uso de herramienta
        # que NO está en tool_contracts
        for tool in mentioned_tools:
            if tool not in safe_keywords and tool not in tool_names:
                # Verificar que parece un nombre de MCP real (con guiones o formato típico)
                if '-' in tool or len(tool) > 5:
                    errors.append(
                        f"Posible Ghost Entity: '{tool}' parece referenciarse como herramienta "
                        f"pero no está en tool_contracts"
                    )
        
        # Verificar que todas las herramientas en contracts existen (validación inversa)
        # Esto es solo informativo, no es error
        
        return len(errors) == 0, errors
    
    def add_verification_metadata(
        self, 
        bundle: Dict, 
        result: VerificationResult
    ) -> Dict:
        """
        Añade metadata de verificación al bundle.
        
        Args:
            bundle: Gem Bundle original
            result: Resultado de verificación
        
        Returns:
            Bundle con metadata de verificación
        """
        bundle_copy = bundle.copy()
        
        bundle_copy['verifier'] = {
            'verified': result.passed,
            'checks_passed': result.checks_passed,
            'warnings_count': len(result.warnings),
            'verified_at': None  # Se llenará con timestamp al guardar
        }
        
        return bundle_copy


# CLI para testing standalone
if __name__ == "__main__":
    import json
    
    # Test bundle
    test_bundle = {
        "bundle_meta": {
            "use_case_id": "test_case",
            "version": "1.0.0",
            "risk_score": 45
        },
        "model_routing": {
            "default_model": "gemini-3-pro"
        },
        "policies": {
            "knowledge_states": ["HECHO_VERIFICADO", "INFERENCIA", "ASUNCION", "FALTAN_DATOS"],
            "model_armor_enabled": True,
            "hitl_required": False
        },
        "system_prompt": {
            "text": "Eres un agente. Usa filesystem para leer archivos."
        },
        "tools": {
            "contracts": [
                {"name": "filesystem", "side_effects": False}
            ]
        }
    }
    
    verifier = VerifierGate()
    result = verifier.verify(test_bundle, risk_score=45)
    
    print("\n" + "="*60)
    print("  VERIFIER GATE TEST")
    print("="*60)
    
    print(f"\nVerification {'PASSED' if result.passed else 'FAILED'}")
    
    print(f"\nChecks passed: {result.checks_passed}")
    
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for error in result.errors:
            print(f"  ❌ {error}")
    
    if result.warnings:
        print(f"\nWarnings ({len(result.warnings)}):")
        for warning in result.warnings:
            print(f"  ⚠️ {warning}")
