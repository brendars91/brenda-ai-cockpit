# 📚 Catálogo de Skills Disponibles

Esta carpeta contiene **skills reutilizables** organizados por dominio. Antigravity los usa para **configurar proyectos automáticamente**.

---

## 🎯 Cómo Funciona

Cuando inicias un proyecto nuevo:

1. **Le dices a Antigravity** el contexto del proyecto
2. **Antigravity analiza** y sugiere skills apropiados
3. **Confirmas** y Antigravity los copia a `.agent/skills/` del proyecto
4. **Antigravity adapta** cada skill 100% al contexto específico

---

## 📂 Skills Disponibles por Dominio

### 🌐 **Web & APIs**
- `api-design` - Diseño de APIs REST/GraphQL
- `ui-design` - Interfaces de usuario modernas
- `accessibility` - Accesibilidad WCAG
- `performance` - Optimización web

### 🔧 **Code Quality**
- `code-fixer` - Reparación automática de bugs
- `testing` - Estrategias de testing (unit, integration, e2e)
- `refactoring` - Mejora de código legacy
- `lint-standards` - Linting y code style

### 🔒 **Security**
- `security-red-team` - Detección proactiva de vulnerabilidades
- `secrets-detection` - Detección de secretos en código
- `dependency-audit` - Auditoría de dependencias

### 🗄️ **Data & Databases**
- `database-optimizer` - Optimización de queries
- `migration-planner` - Planificación de migraciones
- `data-pipeline` - Pipelines de datos ETL
- `ml-ops` - MLOps y model deployment

### 🤖 **Automation**
- `n8n-workflows` - Workflows de automatización
- `ci-cd-hooks` - Integración CI/CD
- `docker-builder` - Contenedores y deployment
- `integration-patterns` - Patrones de integración

### 💼 **SAP & ERP**
- `sap-fico` - SAP Finance & Controlling
- `sap-btp` - SAP Business Technology Platform
- `abap-standards` - Estándares ABAP

### 🏗️ **Core (Siempre Activos)**
- `skill-router` - Selección inteligente de skills
- `project-standards` - Estándares del proyecto

---

## 🔄 Mapeo Contexto → Skills

| Tipo de Proyecto | Skills Auto-Seleccionados |
|------------------|---------------------------|
| **API REST (Python/Node/Java)** | `api-design`, `code-fixer`, `database-optimizer`, `security-red-team` |
| **Frontend (React/Vue/Angular)** | `ui-design`, `accessibility`, `performance`, `testing` |
| **Backend + DB** | `database-optimizer`, `migration-planner`, `api-design`, `security-red-team` |
| **Data Science/ML** | `data-pipeline`, `ml-ops`, `testing` |
| **Automation** | `n8n-workflows`, `integration-patterns`, `ci-cd-hooks` |
| **SAP Projects** | `sap-fico`, `abap-standards`, `sap-btp` |
| **DevOps/Infra** | `docker-builder`, `ci-cd-hooks`, `security-red-team` |
| **Full-Stack** | `api-design`, `ui-design`, `database-optimizer`, `testing`, `security-red-team` |

---

## 💡 Ejemplo de Uso

```
Usuario: "Nuevo proyecto: Dashboard React con API Node.js"

Antigravity:
  🔷 Contexto detectado: Full-Stack (React + Node.js)
  
  🎯 Skills recomendados:
    ✓ ui-design (para componentes React)
    ✓ api-design (para endpoints Node.js)
    ✓ performance (optimización frontend)
    ✓ testing (Jest + React Testing Library)
    ✓ security-red-team (XSS, CSRF, etc.)
  
  ¿Los copio a .agent/skills/ y adapto? (s/n)
  
Usuario: "sí"

Antigravity:
  ✓ Copiando 5 skills...
  ✓ Adaptando ui-design para componentes de Dashboard...
  ✓ Adaptando api-design para endpoints de datos...
  ✓ Listo! Skills instalados y 100% adaptados al proyecto.
```

---

## 📋 Estructura de un Skill

Cada skill tiene:

```
skill-name/
├── SKILL.md              ← Documentación principal
├── examples/             ← Ejemplos de uso
├── scripts/              ← Scripts helper
└── resources/            ← Templates, configs
```

---

## ✅ Reglas de Adaptación

Cuando Antigravity adapta un skill:

1. **Reemplaza ejemplos genéricos** con ejemplos del proyecto
2. **Ajusta nomenclatura** (nombres de variables, clases, APIs)
3. **Añade secciones específicas** del dominio
4. **Actualiza referencias** a archivos del proyecto
5. **Configura tooling** específico (linters, formatters)

---

## 🚀 Añadir Nuevos Skills

Si creas un skill nuevo:

1. Añádelo a esta carpeta `Skills proyectos/<domain>/<skill-name>/`
2. Crea `SKILL.md` con la estructura estándar
3. Actualiza este `CATALOG.md` con descripción
4. Antigravity lo detectará automáticamente en futuros proyectos

---

**Ubicación**: `C:\Users\ASUS\.gemini\Skills proyectos\`  
**Última actualización**: 2026-01-19
