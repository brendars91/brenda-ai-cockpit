---
name: spec-linter
description: Capacidad para validar sintáctica y semánticamente el Use Case Spec JSON generado.
---

# Skill: Spec Linter

## Propósito
Asegurar que el JSON generado por el Gem Architect cumpla estrictamente con el esquema `use_case_spec.v1.schema.json` antes de ser entregado al usuario o guardado.

## Instrucciones
Cuando hayas generado un bloque JSON candidato para el `use_case_spec`:

1.  **Leer el Esquema:**
    Usa la herramienta `filesystem` (o equivalente) para leer el archivo de esquema en:
    `../schemas/use_case_spec.v1.schema.json`

2.  **Validación Campo a Campo:**
    Verifica que tu JSON tenga:
    - [ ] `use_case_id`: Formato kebab-case (ej. `my-agent-v1`).
    - [ ] `goal`: Texto claro en lenguaje natural.
    - [ ] `data_sources`: Array no vacío. Cada fuente debe tener `type` y `access`.
    - [ ] `actions`: Array no vacío. Cada acción debe tener `type`.
    - [ ] `security`: Debe tener `hitl_required` (auto/always/never).

3.  **Auto-Corrección:**
    Si encuentras una discrepancia (ej. falta un campo obligatorio o el tipo es incorrecto), **corrígelo silenciosamente** antes de presentar el bloque final.

4.  **Reporte Final:**
    Si la validación es exitosa, presenta el JSON. Si hay dudas sobre un campo opcional, pregunta al usuario.
