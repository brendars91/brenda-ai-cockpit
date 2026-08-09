---
name: tool-contract-builder
description: Generador de contratos MCP para tools. Crea definiciones JSON Schema para tool_contracts compatible con el Master Spec, sin implementar el servidor MCP.
---

# Tool Contract Builder (Gem Builder Edition)

## Propósito

Generar **definiciones de tool_contracts** válidas para Gem Bundles, especificando:
- Input/Output schemas
- Side-effects
- Timeouts y retry policies
- Idempotency requirements

## Inputs

1. **Tool Name** - Nombre de la herramienta MCP
2. **Capabilities** - Qué hace la tool (lectura/escritura/ejecución)
3. **Risk Assessment** - Del Risk Engine

## Template de Contrato

```json
{
  "name": "database_query",
  "protocol": "mcp",
  "description": "Ejecuta queries SQL de solo lectura",
  "side_effects": false,
  "dry_run": false,
  "timeout_ms": 5000,
  "idempotency_key_required": false,
  "schema_ref": "schemas/tools/database_query.schema.json",
  "error_catalog": [
    {
      "code": "TIMEOUT",
      "retryable": true,
      "max_retries": 3,
      "backoff_ms": 1000
    },
    {
      "code": "INVALID_QUERY",
      "retryable": false,
      "fallback": "return_empty_result"
    }
  ]
}
```

## Reglas de Generación

### Side-Effects Detection

- **Lectura** (`side_effects: false`):
  - `filesystem.read_file`
  - `database.select`
  - `api.get`

- **Escritura** (`side_effects: true`):
  - `filesystem.write_file`
  - `database.insert/update/delete`
  - `api.post/put/delete`

### Políticas por Risk Score

| Risk Score | Políticas Automáticas |
|------------|-----------------------|
| 0-30 (Low) | `dry_run: false`, `timeout_ms: 10000` |
| 31-60 (Medium) | `dry_run: true`, `timeout_ms: 5000`, HITL sugerido |
| 61-100 (High) | `dry_run: true`, `timeout_ms: 3000`, HITL OBLIGATORIO, read-only |

## Output

Array de tool_contracts para inyectar en el Gem Bundle.
