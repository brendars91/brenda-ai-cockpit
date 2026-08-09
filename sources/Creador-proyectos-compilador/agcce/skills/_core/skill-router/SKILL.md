---
name: skill-router
description: Super-skill que selecciona el conjunto óptimo de skills basándose en el Project Brief, contexto del repo y catálogo disponible. Usar siempre al inicio de un proyecto para determinar qué skills activar.
---

# Skill Router

## Propósito

Dado un **Project Brief** y el **estado del repositorio**, seleccionar el conjunto mínimo y eficaz de skills de `docs/skills/CATALOG.md`.

## Entradas

1. **Project Brief** (texto del usuario con objetivo, entregables, restricciones)
2. **Señales del repo**:
   - Stack detectado (package.json, requirements.txt, etc.)
   - Presencia de carpetas clave (docs/, src/, tests/)
   - Archivos de configuración existentes
3. **Catálogo**: `docs/skills/CATALOG.md`

## Algoritmo de Selección

### Paso A: Extraer Intenciones
Del Project Brief, identificar:
- **Objetivo principal** (¿qué se quiere lograr?)
- **Entregables** (¿qué artefactos se producirán?)
- **Restricciones** (¿qué NO hacer?)
- **Riesgos** (¿qué podría fallar?)

### Paso B: Mapear Intenciones → Skills
Comparar intenciones contra el catálogo:
1. Buscar coincidencias en `description`
2. Filtrar por `domain` relevante al stack detectado
3. Verificar `tags/metadata` si existen

### Paso C: Resolver Conflictos
- Preferir skills más específicas del stack detectado
- No seleccionar dos skills que hagan lo mismo
- Si hay duplicado funcional, elegir la más actualizada y justificar

### Paso D: Componer Conjunto Final
- **Core (siempre activas)**:
  - `project-standards` - Estándares de calidad
- **Recomendadas**: 3-8 skills máximo según Project Brief
- **Excluidas**: Skills que choquen con restricciones

## Salida Obligatoria

```markdown
## Selected Skills
- [skill-name]: razón de inclusión

## Rationale
Explicación breve de la selección

## Risks/Assumptions
- Supuestos sobre el proyecto
- Riesgos identificados

## Next Actions
1. Paso inmediato a ejecutar
2. Siguiente paso
```

## Dominios Disponibles

| Dominio | Descripción |
|---------|-------------|
| `documents` | Word, Excel, PDF, PowerPoint |
| `design` | UI/UX, diseño visual, temas |
| `web` | Web apps, testing web |
| `development` | MCP, skills, herramientas dev |
| `communication` | Documentación, comunicaciones |
| `automation` | n8n, workflows, automatización |
| `code-quality` | Debugging, code review, fixes |
| `sap` | FI/CO, ABAP, BTP |
| `_inbox` | Skills sin clasificar |

## Ejemplo de Uso

**Input**: "Crear dashboard de costos SAP FI con exportación a Excel"

**Output**:
```markdown
## Selected Skills
- xlsx: Exportación a Excel con fórmulas
- frontend-design: Dashboard UI de alta calidad
- sap/fi-co: Conocimiento de módulo FI

## Rationale
Proyecto combina SAP FI (extracción datos), visualización (dashboard) y exportación (Excel).

## Risks/Assumptions
- Asume acceso a datos SAP vía RFC/BAPI
- Dashboard web, no SAP Fiori nativo

## Next Actions
1. Definir KPIs de costos a mostrar
2. Diseñar estructura del dashboard
3. Implementar extracción de datos SAP
```
