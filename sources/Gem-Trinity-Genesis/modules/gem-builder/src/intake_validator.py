"""
Intake Validator - Fase 1 del Pipeline Gem Builder

Valida Use Case Spec contra schema JSON y reglas de negocio.
Normaliza el input para garantizar consistencia.
"""
import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class IntakeValidator:
    """Validador de Use Case Specs"""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Args:
            schema_path: Path al schema JSON. Si None, usa el schema por defecto.
        """
        if schema_path is None:
            # Path relativo desde src/
            schema_path = "../schemas/use_case_spec.v1.schema.json"
        
        self.schema_path = Path(__file__).parent / schema_path
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict:
        """Carga el JSON Schema de Use Case Spec"""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate(self, spec_path: str) -> Tuple[bool, Optional[Dict], List[str]]:
        """
        Valida un Use Case Spec contra el schema.
        
        Args:
            spec_path: Path al archivo JSON del Use Case Spec
        
        Returns:
            Tuple de (es_valido, spec_normalizado, errores)
        """
        errors = []
        
        # Cargar spec
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                spec = json.load(f)
        except FileNotFoundError:
            errors.append(f"Archivo no encontrado: {spec_path}")
            return False, None, errors
        except json.JSONDecodeError as e:
            errors.append(f"JSON inválido: {e}")
            return False, None, errors
        
        # Validar contra schema
        try:
            jsonschema.validate(instance=spec, schema=self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
            return False, spec, errors
        
        # Validaciones de negocio adicionales
        business_errors = self._validate_business_rules(spec)
        if business_errors:
            errors.extend(business_errors)
            return False, spec, errors
        
        # Normalizar spec (añadir defaults, limpiar)
        normalized_spec = self._normalize_spec(spec)
        
        return True, normalized_spec, []
    
    def _validate_business_rules(self, spec: Dict) -> List[str]:
        """
        Validaciones de reglas de negocio más allá del schema.
        
        Returns:
            Lista de errores (vacía si todo OK)
        """
        errors = []
        
        # Regla 1: Si tiene acciones con side_effects, debe tener HITL o permitirse explícitamente
        has_side_effects = any(
            action.get('side_effects', False) 
            for action in spec.get('actions', [])
        )
        
        if has_side_effects:
            hitl = spec.get('security', {}).get('hitl_required', 'auto')
            if hitl == 'never':
                errors.append(
                    "Acciones con side_effects requieren HITL (hitl_required != 'never')"
                )
        
        # Regla 2: Financial data requiere sensitivity=financial
        for ds in spec.get('data_sources', []):
            if 'financial' in ds.get('description', '').lower():
                if ds.get('sensitivity') != 'financial':
                    errors.append(
                        f"Data source '{ds.get('type')}' menciona 'financial' "
                        "pero sensitivity no es 'financial'"
                    )
        
        # Regla 3: Write access requiere justificación explícita
        for ds in spec.get('data_sources', []):
            if ds.get('access') in ['write', 'read_write']:
                if not ds.get('description'):
                    errors.append(
                        f"Data source con write access '{ds.get('type')}' "
                        "requiere 'description' justificando el write"
                    )
        
        # Regla 4: Execute actions son consideradas high-risk
        has_execute = any(
            action.get('type') == 'execute'
            for action in spec.get('actions', [])
        )
        
        if has_execute:
            # Advertencia, no error
            # (el Risk Engine lo manejará con Risk Score alto)
            pass
        
        return errors
    
    def _normalize_spec(self, spec: Dict) -> Dict:
        """
        Normaliza el spec añadiendo defaults y limpiando.
        
        Returns:
            Spec normalizado
        """
        normalized = spec.copy()
        
        # Añadir defaults
        if 'users' not in normalized:
            normalized['users'] = ['end_user']
        
        if 'output' not in normalized:
            normalized['output'] = {'type': 'text'}
        
        if 'constraints' not in normalized:
            normalized['constraints'] = {
                'latency_ms': 5000,
                'cost_tier': 'medium'
            }
        
        if 'security' not in normalized:
            normalized['security'] = {'hitl_required': 'auto'}
        
        # Normalizar data_sources
        for ds in normalized.get('data_sources', []):
            if 'access' not in ds:
                ds['access'] = 'read'
            if 'sensitivity' not in ds:
                ds['sensitivity'] = 'internal'
        
        # Normalizar actions
        for action in normalized.get('actions', []):
            if 'side_effects' not in action:
                action['side_effects'] = False
        
        return normalized
    
    def get_missing_data_questions(self, spec: Dict) -> List[str]:
        """
        Genera preguntas para campos faltantes (FALTAN_DATOS).
        
        Args:
            spec: Spec parcial o incompleto
        
        Returns:
            Lista de preguntas para el usuario
        """
        questions = []
        
        if 'use_case_id' not in spec:
            questions.append("¿Cuál es el identificador del caso de uso? (ej: sap_cost_analyzer)")
        
        if 'goal' not in spec or len(spec.get('goal', '')) < 10:
            questions.append("¿Cuál es el objetivo del agente? (descripción detallada)")
        
        if 'data_sources' not in spec or not spec.get('data_sources'):
            questions.append(
                "¿Qué fuentes de datos necesita el agente? "
                "(ej: database, API, archivos, Google Drive)"
            )
        
        if 'actions' not in spec or not spec.get('actions'):
            questions.append(
                "¿Qué acciones debe realizar el agente? "
                "(ej: analizar, resumir, transformar, ejecutar)"
            )
        
        # Preguntas contextuales según lo que ya existe
        if spec.get('data_sources'):
            for i, ds in enumerate(spec['data_sources']):
                if 'sensitivity' not in ds:
                    questions.append(
                        f"Para la fuente de datos '{ds.get('type', 'desconocida')}', "
                        "¿cuál es el nivel de sensibilidad? (public/internal/confidential/financial)"
                    )
        
        return questions


# CLI para testing standalone
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python intake_validator.py <path_to_spec.json>")
        sys.exit(1)
    
    validator = IntakeValidator()
    spec_path = sys.argv[1]
    
    print(f"\nValidando Use Case Spec: {spec_path}")
    print("=" * 60)
    
    is_valid, normalized_spec, errors = validator.validate(spec_path)
    
    if is_valid:
        print("✓ Spec válido")
        print("\nSpec normalizado:")
        print(json.dumps(normalized_spec, indent=2, ensure_ascii=False))
    else:
        print("✗ Spec inválido")
        print("\nErrores encontrados:")
        for error in errors:
            print(f"  - {error}")
        
        # Mostrar preguntas FALTAN_DATOS si aplica
        if normalized_spec:
            questions = validator.get_missing_data_questions(normalized_spec)
            if questions:
                print("\nFALTAN_DATOS - Preguntas para completar:")
                for q in questions:
                    print(f"  ? {q}")
