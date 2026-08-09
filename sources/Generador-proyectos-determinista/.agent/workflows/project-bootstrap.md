---
description: Bootstrap automático de proyecto - Configura MCPs y Skills según contexto
---

# Project Bootstrap Workflow

## 🎯 Propósito

Este workflow se ejecuta **automáticamente** cuando Antigravity detecta un proyecto nuevo o sin configurar. Analiza el contexto y configura:

1. ✅ **MCPs necesarios** (te dice cuáles activar)
2. ✅ **Skills apropiados** (los copia y adapta al proyecto)

---

## 🔄 Cuándo se Activa

- Cuando creas un nuevo proyecto
- Cuando abres un proyecto sin `.agent/skills/`
- Cuando explícitamente pides "configura este proyecto"

---

## 📋 Proceso Automático

### Paso 1: Análisis de Contexto

Antigravity analiza:
- **Archivos del proyecto** (package.json, requirements.txt, pom.xml, etc.)
- **README o documentación** existente
- **Descripción verbal** que le des del proyecto

Ejemplos de contexto detectado:
- "Proyecto Python con FastAPI y PostgreSQL" → API, Base de Datos
- "Dashboard React con Chart.js" → Frontend, Visualización
- "Agente con n8n para automatización" → Automation, Workflows
- "Sistema SAP ABAP FICO" → ERP, SAP

---

### Paso 2: Sugerencia de MCPs

Basado en el contexto, Antigravity sugiere MCPs:

```
🔷 MCPs Recomendados para este proyecto:

CRÍTICOS (activar obligatoriamente):
  ✓ filesystem - Lectura/escritura de archivos
  ✓ snyk - Escaneo de seguridad

ALTAMENTE RECOMENDADOS:
  ✓ context7 - Búsqueda semántica en codebase
  ✓ sequential-thinking - Razonamiento complejo

OPCIONALES (según necesidad):
  ○ opa - Políticas y validación (si hay compliance)
  ○ fetch - Acceso a URLs externas
  ○ github - Integración Git (si hay CI/CD)
  ○ docker - Contenedores (si hay deployment)

¿Quieres que active estos MCPs en settings.json? (s/n)
```

---

### Paso 3: Selección de Skills

Antigravity busca en `C:\Users\ASUS\.gemini\Skills proyectos\` y selecciona:

**Mapeo Contexto → Skills**:

| Contexto del Proyecto | Skills Seleccionados |
|----------------------|---------------------|
| **API REST** | `api-design`, `code-fixer`, `security-red-team` |
| **Frontend (React/Vue)** | `ui-design`, `accessibility`, `performance` |
| **Base de Datos** | `database-optimizer`, `migration-planner` |
| **Automation (n8n)** | `n8n-workflows`, `integration-patterns` |
| **SAP ABAP/FICO** | `sap-fico`, `sap-btp`, `abap-standards` |
| **Python Data** | `data-pipeline`, `ml-ops`, `testing` |
| **DevOps/CI/CD** | `docker-builder`, `ci-cd-hooks` |
| **Security** | `security-red-team`, `secrets-detection` |

```
🎯 Skills Recomendados para tu proyecto:

De "Skills proyectos":
  ✓ api-design (para diseño de endpoints REST)
  ✓ code-fixer (para reparación automática de bugs)
  ✓ security-red-team (para detección de vulnerabilidades)
  ✓ database-optimizer (para queries eficientes)

¿Los copio a .agent/skills/ y adapto al proyecto? (s/n)
```

---

### Paso 4: Adaptación de Skills

Si confirmas, Antigravity:

1. **Copia** los skills de `Skills proyectos/` a `.agent/skills/` del proyecto
2. **Adapta** cada `SKILL.md` al contexto específico:
   - Reemplaza ejemplos genéricos con ejemplos del proyecto
   - Ajusta nomenclatura y convenciones
   - Añade secciones específicas del dominio

Ejemplo de adaptación:

**Antes** (genérico):
```markdown
# API Design Skill
Diseña APIs REST siguiendo mejores prácticas.
Ejemplo: GET /api/users/{id}
```

**Después** (adaptado a "Sistema de Costos SAP"):
```markdown
# API Design Skill - SAP Cost Analyzer
Diseña APIs REST para exposición de datos SAP FI.
Ejemplo: GET /api/sap/costs/{project_id}?period=Q4
Considera: Autenticación SAP, Rate limiting, Cache de tablas BKPF/BSEG
```

---

## 🚀 Ejemplo Completo de Bootstrap

### Escenario: Nuevo Proyecto de API Python

```
Usuario: "Voy a crear una API con FastAPI para gestionar inventarios"

Antigravity:
  1. [ANÁLISIS] Detectado: API REST + Python + Base de Datos
  
  2. [MCPs]
     🔷 MCPs Recomendados:
     CRÍTICOS:
       ✓ filesystem
       ✓ snyk
     RECOMENDADOS:
       ✓ context7 (búsqueda semántica)
       ✓ fetch (docs externas FastAPI)
     
     ¿Activo estos MCPs? → Usuario: "sí"
     ✓ Añadidos a settings.json
  
  3. [SKILLS]
     🎯 Skills Seleccionados:
       ✓ api-design
       ✓ code-fixer
       ✓ database-optimizer
       ✓ security-red-team
     
     ¿Los copio y adapto? → Usuario: "sí"
     
  4. [ADAPTACIÓN]
     ✓ Copiando api-design...
     ✓ Adaptando a FastAPI + Inventarios...
     ✓ Añadiendo ejemplos de endpoints:
       - GET /inventory/items
       - POST /inventory/items
       - PUT /inventory/items/{id}/stock
     
     ✓ Copiando code-fixer...
     ✓ Adaptando para errores comunes de FastAPI...
     
     ✓ Copiando database-optimizer...
     ✓ Adaptando para queries de inventario (products, stock, movements)...
     
     ✓ Copiando security-red-team...
     ✓ Añadiendo tests de inventario (IDOR, stock manipulation)...
  
  5. [RESUMEN]
     ✅ Proyecto configurado!
     
     MCPs activos: 4
     Skills instalados: 4 (100% adaptados)
     
     Ahora puedes decirme:
     - "Diseña la API de inventarios"
     - "Implementa el endpoint de productos"
     - "Escanea vulnerabilidades en la API"
```

---

## 📂 Estructura Resultante

Después del bootstrap:

```
Mi Proyecto API/
├── .agent/
│   └── skills/              ← Skills copiados y adaptados
│       ├── api-design/
│       ├── code-fixer/
│       ├── database-optimizer/
│       └── security-red-team/
│
├── PROJECT_CONFIG.json      ← Configuración del bootstrap
└── README.md                ← Actualizado con skills disponibles
```

`PROJECT_CONFIG.json`:
```json
{
  "project_context": {
    "type": "api_rest",
    "stack": ["python", "fastapi", "postgresql"],
    "domain": "inventory_management"
  },
  "bootstrap": {
    "mcps_enabled": ["filesystem", "snyk", "context7", "fetch"],
    "skills_installed": ["api-design", "code-fixer", "database-optimizer", "security-red-team"],
    "bootstrapped_at": "2026-01-19T12:25:00Z"
  }
}
```

---

## 🎯 Para Proyectos Futuros

**Automático**:
1. Abres nuevo proyecto en VS Code
2. Le dices a Antigravity qué es el proyecto
3. Antigravity ejecuta este workflow automáticamente
4. Confirmas MCPs y Skills
5. ¡Listo para trabajar!

**No necesitas repetir nada**, Antigravity lo maneja.

---

## 💡 Comandos que NO Necesitas Recordar

```powershell
# Listar skills disponibles
Get-ChildItem "C:\Users\ASUS\.gemini\Skills proyectos"

# Copiar skill manualmente
Copy-Item -Recurse "Skills proyectos/api-design" ".agent/skills/"

# Activar MCPs en settings.json
code "C:\Users\ASUS\.gemini\settings.json"
```

**Antigravity hace todo esto automáticamente** 🚀

---

**Versión**: 1.0  
**Última actualización**: 2026-01-19
