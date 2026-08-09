---
description: Bootstrap automático de proyecto - Configura MCPs y Skills según contexto
---

# /project-bootstrap Workflow

Configura automáticamente un nuevo proyecto con Skills y MCPs apropiados.

## Pasos

1. **Analizar contexto del proyecto**
   - Detectar stack tecnológico
   - Identificar dominio (SAP, DevOps, Marketing, Custom)
   - Evaluar complejidad

2. **Seleccionar Skills del catálogo**
   Basado en `resources/skills/CATALOG.md`:
   
   | Stack | Skills Auto-seleccionados |
   |-------|--------------------------|
   | Python API | `api-design`, `code-fixer`, `security-red-team` |
   | React/Next.js | `ui-design`, `performance`, `testing` |
   | SAP | `sap-fico`, `abap-standards` |
   | Full-Stack | Combinación de ambos |

3. **Copiar Skills a `.agent/skills/`**
   // turbo
   ```bash
   cp -r resources/skills/<skill-id> .agent/skills/
   ```

4. **Adaptar Skills al contexto**
   - Reemplazar ejemplos genéricos
   - Ajustar nomenclatura al proyecto
   - Actualizar referencias a archivos

5. **Configurar MCPs necesarios**
   Revisar `local-watcher/mcp_config_local.json` y activar:
   - `filesystem` (siempre)
   - `github` (si hay repo)
   - `context7` (documentación)
   - `snyk` (seguridad)

6. **Copiar Rules base**
   // turbo
   ```bash
   cp .agent/rules/global-security.md .agent/rules/
   cp .agent/rules/coding-standards.md .agent/rules/
   ```

7. **Generar reporte de bootstrap**

```
✅ Project Bootstrap Complete

Skills instalados: 4
  • api-design
  • code-fixer
  • security-red-team
  • testing

MCPs activos: 3
  • filesystem
  • github
  • snyk

Rules copiadas: 2
  • global-security.md (Priority 9999)
  • coding-standards.md

Proyecto listo para desarrollo.
```

// turbo-all
