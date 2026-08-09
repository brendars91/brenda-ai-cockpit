# 📚 Catálogo de Skills - Skills Proyectos

> **Biblioteca Central de Skills Reutilizables para Antigravity**  
> **Ubicación**: `C:\Users\ASUS\.gemini\Skills proyectos`  
> **Última actualización**: 2026-01-19

---

## 🏗️ Estructura de la Biblioteca

```
Skills proyectos/
├── .agent/skills/
│   ├── _core/                    # Skills fundamentales (siempre activas)
│   ├── automation/               # Automatización y workflows
│   ├── by-domain/                # Organizadas por dominio
│   │   ├── _inbox/               # Sin clasificar
│   │   ├── automation/           # Automatización
│   │   ├── code-quality/         # Calidad de código
│   │   ├── communication/        # Documentación y comunicación
│   │   ├── design/               # UI/UX y diseño
│   │   ├── development/          # Desarrollo y herramientas
│   │   ├── documents/            # Manejo de documentos Office
│   │   ├── sap/                  # SAP (FI/CO, ABAP, BTP)
│   │   ├── security/             # Seguridad (NEW!)
│   │   └── web/                  # Desarrollo web
│   └── projects/                 # Skills específicas de proyectos
├── docs/                         # Documentación
│   └── ANTIGRAVITY_SKILLS_BEST_PRACTICES.md
└── tools/                        # Herramientas auxiliares
```

---

## ⭐ Skills Core (Siempre Activas)

| Skill | Descripción | Estado |
|-------|-------------|--------|
| **skill-router** | Super-skill que selecciona el conjunto óptimo de skills basándose en el Project Brief | ✅ Completa |
| **project-standards** | Estándares de calidad, naming conventions y Definition of Done | ✅ Completa |

---

## 🤖 Skills de Automatización

| Skill | Descripción | Estado | Ubicación |
|-------|-------------|--------|-----------|
| **n8n-workflows** | Creación y validación de workflows n8n profesionales | ✅ Completa | `automation/` y `by-domain/automation/` |

---

## 🔐 Skills de Seguridad

| Skill | Descripción | Estado | Ubicación |
|-------|-------------|--------|-----------|
| **security-red-team** | Generación de hipótesis de ataque, detección de vulnerabilidades lógicas, protocolo Red-to-Green | ✅ Completa | `by-domain/security/` |

---

## 🛠️ Skills de Desarrollo

| Skill | Descripción | Estado | Ubicación |
|-------|-------------|--------|-----------|
| **mcp-builder** | Creación de servidores MCP profesionales (9KB SKILL.md) | ✅ Completa | `by-domain/development/` |
| **skill-creator** | Creación de skills siguiendo mejores prácticas (18KB SKILL.md) | ✅ Completa | `by-domain/development/` |

---

## 🔍 Skills de Code Quality

| Skill | Descripción | Estado | Ubicación |
|-------|-------------|--------|-----------|
| **code-fixer** | Debugging sistemático, integración Snyk/Semgrep y patrones de fix | ✅ Completa | `by-domain/code-quality/` |

---

## 📊 Skills SAP

| Skill | Descripción | Estado | Ubicación |
|-------|-------------|--------|-----------|
| **abap** | Desarrollo ABAP | 📁 Carpeta creada | `by-domain/sap/abap/` |
| **btp** | SAP Business Technology Platform | 📁 Carpeta creada | `by-domain/sap/btp/` |
| **fi-co** | Módulos Financieros y Controlling | 📁 Carpeta creada | `by-domain/sap/fi-co/` |

---

## 📖 Cómo Usar Este Catálogo

### Para Nuevos Proyectos

1. **Ejecutar `skill-router`** con tu Project Brief
2. **Revisar** las skills recomendadas
3. **Copiar** las skills necesarias a tu proyecto:
   ```powershell
   Copy-Item -Recurse "C:\Users\ASUS\.gemini\Skills proyectos\.agent\skills\by-domain\<domain>\<skill>" `
              -Destination "C:\mi-proyecto\.agent\skills\<skill>"
   ```
4. **Personalizar** si es necesario

### Criterios de Selección

| Tipo de Proyecto | Skills Recomendadas |
|------------------|---------------------|
| **Web App** | n8n-workflows, security-red-team |
| **Automatización** | n8n-workflows, mcp-builder |
| **Desarrollo IA/Agentes** | skill-creator, mcp-builder, security-red-team |
| **SAP** | fi-co, abap, btp (según módulo) |
| **Seguridad** | security-red-team, code-fixer |

---

## 📋 Estado de Skills

- ✅ **Completa**: Skill lista para producción con documentación completa
- ⏳ **Placeholder**: Estructura creada, pendiente desarrollo
- 📁 **Carpeta creada**: Solo estructura de carpetas

---

## 🔄 Mantenimiento

### Añadir Nueva Skill

1. Crear carpeta en el dominio correspondiente
2. Crear `SKILL.md` con frontmatter válido
3. Actualizar este catálogo
4. Probar en un proyecto piloto

### Promover Skill

```
projects/<id>/ → by-domain/<domain>/ → _core/
   (específica)      (genérica)        (fundamental)
```

---

> **Documentación relacionada**: [ANTIGRAVITY_SKILLS_BEST_PRACTICES.md](./ANTIGRAVITY_SKILLS_BEST_PRACTICES.md)
