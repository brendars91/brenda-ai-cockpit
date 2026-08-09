---
name: gem-standards
description: Estándares de calidad, nomenclatura y Definition of Done exclusivos para Gem Bundles compilados.
---

# Gem Standards

## Naming Conventions

### Bundles
- ID: `[use-case-id]_v[major].[minor].[patch]` (ej: `sap-fi-audit_v1.0.2`)
- Archivo: `bundles/[id].json`

### Systems Prompts
- Variables: `{{SCREAMING_SNAKE_CASE}}` (ej: `{{USER_ROLE}}`, `{{KNOWLEDGE_CUTOFF}}`)
- Hash: SHA-256 del contenido raw

## Definition of Done (Gem Bundle)

Un Gem Bundle es válido SOLO si cumple:

1. **Schema Compliance**:
   - [ ] Valida contra `schemas/gem_bundle.v1.schema.json` sin errores.

2. **Grounding check**:
   - [ ] No menciona fuentes de datos no declaradas en `knowledge_plan`.
   - [ ] Datos volátiles tienen estrategia de grounding asignada.

3. **Security Audit**:
   - [ ] Risk Score calculado (0-100).
   - [ ] Si Score > 60, Policies incluyen `model_armor_enabled: true`.
   - [ ] System Prompt escaneado contra Injection (Snyk Clean).

4. **Trazabilidad**:
   - [ ] `compiled_at` es UTC ISO-8601.
   - [ ] `compiler_version` coincide con el runtime actual.

## Manejo de MCPs
- **Lista Blanca estricta**: Solo tools permitidas en `config/mcp_whitelist.json`.
- **Timeouts**: Timeouts explícitos en milisegundos para cada tool.
- **Idempotencia**: Tools de escritura requieren `idempotency_key`.
