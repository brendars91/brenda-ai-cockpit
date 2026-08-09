---
name: project-standards
description: Estándares de calidad, naming conventions y Definition of Done para skills y proyectos. Se aplica siempre como base de cualquier trabajo.
---

# Project Standards

## Naming Conventions

### Skills
- **Nombre**: `kebab-case` (ej: `sap-fi-reports`)
- **Nombre = carpeta**: El nombre en frontmatter debe coincidir con el directorio
- **Single responsibility**: Una skill = una capacidad bien definida

### Archivos
- Scripts: `kebab-case.ps1`, `snake_case.py`
- Documentación: `UPPER_CASE.md` para docs principales, `kebab-case.md` para referencias

## Calidad Mínima de una Skill

Toda skill debe incluir:

### 1. Frontmatter YAML (obligatorio)
```yaml
---
name: skill-name
description: Descripción clara de qué hace y cuándo usarla
---
```

### 2. Objetivo claro
- ¿Qué problema resuelve?
- ¿Cuándo se debe usar?

### 3. Inputs/Outputs
- ¿Qué necesita para funcionar?
- ¿Qué produce?

### 4. Instrucciones paso a paso
- Procedimiento claro y reproducible
- Comandos o código cuando aplique

### 5. Ejemplos mínimos
- Al menos un ejemplo de uso
- Caso típico documentado

### 6. Referencias (opcional)
- Links a documentación externa
- Recursos adicionales

## Política de Promoción

Las skills maduran a través de niveles:

```
projects/<project-id>/  →  by-domain/<domain>/  →  _core/
   (específica)              (genérica)           (fundamental)
```

### Criterios de promoción:
- **projects → by-domain**: Útil para más de un proyecto, sin dependencias específicas
- **by-domain → _core**: Fundamental, siempre necesaria, muy estable

## Seguridad

### Reglas NO negociables:
1. **NO borrar** archivos sin confirmación explícita
2. **NO sobrescribir** archivos existentes sin confirmación
3. **NO tocar** producción sin validación en staging
4. **NO exfiltrar** datos sensibles
5. **NO almacenar** secretos (tokens, API keys) en el repo

### Manejo de secretos:
- Usar variables de entorno
- Documentar qué secretos se necesitan (sin valores)
- Referenciar secret stores externos

## Definition of Done

Una tarea está completa cuando:

- [ ] Código/skill funciona según especificación
- [ ] Tests pasan (si aplica)
- [ ] Documentación actualizada
- [ ] Sin errores de seguridad (Snyk clean)
- [ ] Revisión de pares (si aplica)
- [ ] Trazabilidad registrada

## Trazabilidad

### Al importar skills:
```markdown
- upstream_source: vendor/anthropics-skills/skills/<name>
- imported_at: YYYY-MM-DD
```

### Al adaptar skills:
```markdown
- adapted_from: .agent/skills/by-domain/<domain>/<name>
- adapted_at: YYYY-MM-DD
- project_id: <project-id>
- reason: <motivo de adaptación>
```
