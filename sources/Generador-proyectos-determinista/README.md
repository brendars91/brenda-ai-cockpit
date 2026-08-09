# AGCCE v4.0 GEM-ENABLED

**Antigravity Core Copilot Engine - Sistema Multi-Agente con Soporte Gem Bundles**

---

## 🎯 ¿Qué es este proyecto?

Un **ejecutor multi-agente** (MAS) que implementa proyectos de forma determinista. Ahora integrado con **Gem Builder** para cargar agentes especializados desde Gem Bundles.

---

## 💬 Cómo Hablar Conmigo (Antigravity)

### ✅ Ejemplos de lo que puedes decir:

1. **"Usa el gem api_auditor para auditar la API de autenticación"**
   → Genero GemPlan y ejecuto AGCCE con ese Gem

2. **"Qué Gems tengo disponibles?"**
   → Listo Gems en `gems/` y muestro estadísticas

3. **"Ejecuta el proyecto de análisis SAP con el gem sap_cost_analyzer"**
   → Cargo el Gem, configuro agentes MAS y ejecuto

4. **"Muéstrame el dashboard con los Gems activos"**
   → Abro el dashboard con la sección de Gems

5. **"Genera un plan para implementar autenticación OAuth2"**
   → Creo un Plan AGCCE normal (sin Gem)

---

## 🚀 Funcionalidades que Puedo Recordarte

Si olvidas mencionar estas cosas, yo te las recuerdo:

### 🔷 Al usar un Gem:
- ✅ **Verificar Gem existe**: Busco en `gems/` automáticamente
- ✅ **Generar GemPlan**: Te pregunto objetivo y tareas
- ✅ **Modo interactivo**: Te ofrezco wizard paso a paso
- ✅ **Cache de profiles**: Si el Gem ya se usó, cargo 10x más rápido
- ✅ **Registry automático**: Registro uso y versión

### 🔷 Al ejecutar:
- ✅ **Pre-flight check**: Valido Git status, schemas, etc.
- ✅ **HITL Gates**: Te pregunto antes de acciones de escritura
- ✅ **Security Guardian**: Escaneo con Snyk + Red Team
- ✅ **Evidence Report**: Genero reporte de lo ejecutado
- ✅ **Telemetría**: Guardo logs en `logs/telemetry.jsonl`

### 🔷 Funcionalidades útiles:
- ✅ **Ver estadísticas de Gems**: Cuáles usas más, risk scores
- ✅ **Dashboard visual**: Métricas y Gems activos
- ✅ **CLI interactivo**: Menú con todas las opciones
- ✅ **Indexar codebase**: Para búsqueda semántica (RAG)

---

## 📋 Comandos que Ejecuto Por Ti

**NO necesitas recordar estos comandos**, yo los ejecuto automáticamente:

```powershell
# Ver Gems disponibles
python scripts/gem_registry.py list

# Generar GemPlan (modo interactivo)
python scripts/gem_plan_generator.py --interactive

# Ejecutar GemPlan
python scripts/orchestrator.py plans/mi_gemplan.json

# Ver estadísticas
python scripts/gem_registry.py stats

# CLI principal
python scripts/agcce_cli.py

# Indexar codebase
python scripts/rag_indexer.py

# Dashboard
python scripts/dashboard_server.py --port 8888
```

---

## 📂 Estructura del Proyecto

```
Agente Copilot Engine/
├── gems/                → Gem Bundles importados (desde Gem Builder)
├── config/
│   └── gem_profiles/    → Agent profiles generados desde Gems
├── plans/               → Plans AGCCE y GemPlans
├── scripts/             → Scripts Python (orchestrator, gem_loader, etc.)
├── logs/                → Telemetría y evidencia
├── documentacion/       → Guías (11_gem_integration.md, etc.)
└── WORKFLOW.md          → Guía conversacional
```

---

## 🎯 Workflows Típicos

### Workflow 1: Ejecutar con Gem

1. **TÚ**: "Usa el gem api_auditor para auditar /api/auth/"
2. **YO**: 
   - Verifico Gem en `gems/`
   - Genero GemPlan (te pregunto detalles)
   - Cargo Gem y configuro 5 agentes MAS
   - Ejecuto Orchestrator
   - Te muestro resultado

### Workflow 2: Plan normal (sin Gem)

1. **TÚ**: "Implementa autenticación OAuth2"
2. **YO**:
   - Genero Plan AGCCE normal
   - Ejecuto con agentes por defecto
   - Te muestro resultado

### Workflow 3: Ver estado

1. **TÚ**: "Qué Gems he usado últimamente?"
2. **YO**:
   - Leo registry
   - Te muestro top Gems por uso
   - Sugiero optimizaciones si hay Gems obsoletos

---

## 🤖 Los 5 Agentes MAS

Cuando ejecutas con un Gem, estos agentes usan la configuración del Gem:

1. **Researcher** → Busca contexto (codebase, docs, APIs)
2. **Architect** → Diseña la solución
3. **Constructor** → Escribe código
4. **Auditor** → Escanea seguridad (Snyk + Security Guardian)
5. **Tester** → Crea tests automatizados

---

## ⚙️ Estado Actual

- ✅ **Integración Gem Builder completa** (Sprints 1-3)
- ✅ AGCCE v4.0 MAS funcionando
- ✅ Security Guardian (Red Team)
- ✅ Dashboard con métricas
- ✅ CLI interactivo
- ✅ RAG indexing
- ✅ n8n webhooks

---

## 💡 Tips

- Habla en **lenguaje natural**, yo ejecuto los comandos
- Si olvidas copiar un Gem, **te lo recuerdo**
- Si hay vulnerabilidades, **te alerto proactivamente**
- Si el Gem tiene Risk > 60, **activo Model Armor automáticamente**
- Uso **cache de profiles** para acelerar (10x más rápido)

---

## 🔗 Proyectos Relacionados

- **Gem Builder**: `C:\Users\ASUS\.gemini\Mis carpetas\Gem Builder\`
  → Para compilar Gem Bundles

---

**Versión**: 1.2.0-GEM-ENABLED  
**Última actualización**: 2026-01-19
