---
name: schema-fixer
description: Diagnosticador y reparador automático de Gem Bundles inválidos. Valida contra gem_bundle.v1.schema.json y propone correcciones específicas.
---

# Schema Fixer (Gem Builder Edition)

## Propósito

Validar Gem Bundles contra el schema oficial y **reparar automáticamente** errores comunes de schema validation.

## Inputs

1. **Gem Bundle (JSON)** - Bundle potencialmente inválido
2. **Schema** - `schemas/gem_bundle.v1.schema.json`

## Proceso de Diagnóstico

### 1. Schema Validation

```python
import jsonschema
import json

def validate_bundle(bundle_path: str, schema_path: str):
    with open(bundle_path) as f:
        bundle = json.load(f)
    with open(schema_path) as f:
        schema = json.load(f)
    
    try:
        jsonschema.validate(instance=bundle, schema=schema)
        return {"valid": True, "errors": []}
    except jsonschema.ValidationError as e:
        return {
            "valid": False,
            "errors": [{
                "path": list(e.path),
                "message": e.message,
                "validator": e.validator
            }]
        }
```

### 2. Auto-Fixes Comunes

| Error | Fix Automático |
|-------|----------------|
| `version` no cumple pattern | Corregir a SemVer válido (ej: `1.0.0`) |
| `compiled_at` no es ISO-8601 | Regenerar con `datetime.utcnow().isoformat()` |
| Falta `compiler_version` | Inyectar desde metadata del compilador |
| `risk_score` fuera de rango | Clampar a [0, 100] |
| `tool_contracts` vacío | Advertir (no auto-fix, requiere decisión manual) |

### 3. Reportar No-Fixables

Errores que REQUIEREN intervención manual:
- Falta `system_prompt.text` (no se puede inferir)
- `knowledge_plan.grounding_strategy` == `rag` pero sin `allowed_sources`
- `policies.security.model_armor_enabled` debe ser `true` pero está `false` con `risk_score > 60`

## Output

```json
{
  "validation_result": {
    "valid": false,
    "auto_fixed": [
      {
        "path": "bundle_meta.version",
        "original": "1.0",
        "fixed": "1.0.0",
        "reason": "SemVer compliance"
      }
    ],
    "manual_fixes_required": [
      {
        "path": "system_prompt.text",
        "error": "Required field missing",
        "action": "Proporcionar system prompt válido"
      }
    ]
  },
  "fixed_bundle": { /* bundle corregido */ }
}
```

## Uso en Pipeline

El Schema Fixer se invoca automáticamente después del Verifier Gate si hay errores de schema.
