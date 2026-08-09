# Skills Library Documentation

## Overview

Esta es una **librería curada de skills** profesional diseñada para acelerar proyectos técnicos y de hobby. Las skills extienden las capacidades del agente proporcionando conocimiento especializado, workflows y herramientas.

## Structure

```
.agent/skills/
├── _core/                    # Skills fundamentales (siempre activas)
│   ├── skill-router/         # Selección automática de skills
│   └── project-standards/    # Estándares de calidad
├── by-domain/                # Skills genéricas por dominio
│   ├── documents/            # Word, Excel, PDF, PowerPoint
│   ├── design/               # UI/UX, diseño visual
│   ├── web/                  # Web apps, testing
│   ├── development/          # MCP, herramientas dev
│   ├── communication/        # Documentación, comms
│   ├── automation/           # n8n, workflows
│   ├── code-quality/         # Debugging, code review
│   ├── sap/                  # SAP (fi-co, abap, btp)
│   └── _inbox/               # Skills sin clasificar
└── projects/                 # Skills específicas por proyecto
```

## Workflow Recomendado

### 1. Escribir Project Brief
Describe tu proyecto con:
- Objetivo principal
- Entregables esperados
- Stack/tecnologías
- Restricciones

### 2. Ejecutar Skill Router
El `skill-router` analiza tu brief y recomienda skills.

### 3. Trabajar con Selected Skills
Usa las skills recomendadas según su documentación.

### 4. Adaptar cuando sea necesario
```powershell
.\tools\skill-scaffolder\skill-scaffolder.ps1 adapt `
    -SourcePath ".agent\skills\by-domain\documents\xlsx" `
    -NewName "sap-xlsx" `
    -ProjectId "mi-proyecto" `
    -Reason "Formato custom para SAP"
```

### 5. Promover skills maduras
- `projects/` → `by-domain/` cuando sea útil para más proyectos
- `by-domain/` → `_core/` cuando sea fundamental

## Commands

### Crear nueva skill
```powershell
.\tools\skill-scaffolder\skill-scaffolder.ps1 create `
    -Name "mi-skill" `
    -Description "Descripción de mi skill" `
    -Domain "web"
```

### Validar todas las skills
```powershell
.\tools\skill-scaffolder\validate-skills.ps1
```

### Reconstruir catálogo
```powershell
.\tools\skill-scaffolder\build-catalog.ps1
```

## Key Files

| File | Purpose |
|------|---------|
| `CATALOG.md` | Catálogo completo de skills (auto-generado) |
| `UPSTREAM.md` | Info del repositorio upstream |
| `UPSTREAM_CATALOG.md` | Skills disponibles en upstream |
| `VALIDATION_REPORT.md` | Último reporte de validación |
| `ADAPTATIONS.md` | Log de adaptaciones de skills |

## Maintenance

1. **Actualizar upstream**: `git pull` en `vendor/anthropics-skills`
2. **Re-validar**: `.\validate-skills.ps1`
3. **Reconstruir catálogo**: `.\build-catalog.ps1`
4. **Revisar duplicados**: Comparar skills similares
5. **Promover maduras**: Mover skills estables a niveles superiores
