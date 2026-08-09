---
name: n8n-workflows
description: Guía profesional para desarrollo de workflows n8n, nodos personalizados e integraciones. Úsala cuando construyas automatizaciones, integraciones con APIs, workflows con AI/LLMs, o necesites crear nodos custom en TypeScript.
license: MIT
---

# n8n Workflow Development Guide

## Overview

Crea workflows de automatización profesionales con n8n que integren cualquier servicio con cualquier otro. La calidad de un workflow se mide por su fiabilidad, mantenibilidad y capacidad de manejar errores graciosamente.

---

# Process

## 🚀 High-Level Workflow

Crear un workflow n8n de alta calidad involucra cinco fases principales:

### Phase 1: Análisis de Requisitos

#### 1.1 Entender el Caso de Uso

**Preguntas clave:**
- ¿Qué evento dispara el workflow? (webhook, schedule, manual, otro workflow)
- ¿Qué datos entran y qué formato tienen?
- ¿Qué transformaciones son necesarias?
- ¿Qué servicios externos se integran?
- ¿Qué debe pasar si hay errores?

**Tipos de Workflows:**
| Tipo | Trigger | Casos de Uso |
|------|---------|--------------|
| **Event-driven** | Webhook | APIs, integraciones real-time |
| **Scheduled** | Cron | ETL, reportes, sincronización |
| **Manual** | Botón | Procesos bajo demanda |
| **Sub-workflow** | Execute Workflow | Módulos reutilizables |

#### 1.2 Mapear Dependencias

- Credenciales necesarias (API keys, OAuth, etc.)
- Rate limits de cada servicio
- Volumen de datos esperado
- Requisitos de latencia

---

### Phase 2: Diseño del Workflow

#### 2.1 Patrones de Arquitectura

**Patrón ETL (Extract-Transform-Load):**
```
Trigger → Fetch Data → Transform → Filter → Output
```

**Patrón Event Handler:**
```
Webhook → Validate → Process → Respond → Notify (async)
```

**Patrón AI Agent:**
```
Trigger → Context Prep → LLM → Parse Response → Action
```

**Patrón Error Handling:**
```
Try Node → [Success] → Continue
          → [Error] → Log → Notify → Retry/Fallback
```

#### 2.2 Consideraciones de Diseño

- **Idempotencia**: El mismo input debe producir el mismo resultado
- **Atomicidad**: Operaciones completas o ninguna
- **Observabilidad**: Logs en puntos críticos
- **Modularidad**: Sub-workflows para lógica reutilizable

---

### Phase 3: Implementación

#### 3.1 Configuración Base

**Variables de Entorno** (Settings → Variables):
```javascript
// Acceso en expresiones
{{ $vars.API_BASE_URL }}
{{ $vars.ENVIRONMENT }}
```

**Credenciales**:
- Usa el sistema de credenciales de n8n, nunca hardcodees secrets
- Configura credenciales de test y producción separadas

#### 3.2 Nodos Esenciales

**HTTP Request** - Llamadas a APIs:
```javascript
// Expresión para headers dinámicos
{{ { "Authorization": "Bearer " + $credentials.apiKey } }}

// Body dinámico
{{ JSON.stringify($json) }}
```

**Code Node** - Transformaciones complejas:
```javascript
// Transformar items
return items.map(item => ({
  json: {
    id: item.json.id,
    processedAt: new Date().toISOString(),
    data: transformData(item.json.data)
  }
}));

function transformData(data) {
  // Lógica de transformación
  return data;
}
```

**IF Node** - Condiciones:
```javascript
// Expresión booleana
{{ $json.status === "active" && $json.amount > 100 }}
```

**Split In Batches** - Procesamiento en lotes:
- Usa para respetar rate limits
- Combina con Wait node para delays

#### 3.3 Expresiones Comunes

```javascript
// Acceso a datos del item actual
{{ $json.fieldName }}
{{ $json["field-with-dashes"] }}
{{ $json.nested?.optional?.field }}

// Datos de nodos anteriores
{{ $('Node Name').item.json.field }}
{{ $('Node Name').all() }}  // Todos los items
{{ $('Node Name').first() }} // Primer item

// Variables especiales
{{ $workflow.id }}
{{ $execution.id }}
{{ $now }}  // Luxon DateTime
{{ $today }} // Fecha de hoy

// Manipulación de fechas (Luxon)
{{ $now.minus({days: 7}).toISO() }}
{{ $now.toFormat('yyyy-MM-dd') }}

// Strings
{{ $json.name.toLowerCase().trim() }}
{{ $json.email.split('@')[1] }}

// Arrays
{{ $json.items.filter(i => i.active).length }}
{{ $json.tags.join(', ') }}
```

**📚 Load [n8n Expressions Reference](./reference/n8n_expressions.md) for complete expression guide.**

---

### Phase 4: Testing y Debugging

#### 4.1 Estrategias de Test

1. **Test con datos mock**: Usa nodos manuales para simular inputs
2. **Ejecución paso a paso**: Ejecuta nodos individuales
3. **Pin data**: Fija outputs para tests consistentes
4. **Production test**: Usa workflows de test que llaman al principal

#### 4.2 Debugging

**Logs en Code Node:**
```javascript
console.log('Processing item:', JSON.stringify($json, null, 2));
// Los logs aparecen en el panel de ejecución
```

**Error Handling Pattern:**
```javascript
// En Code Node
try {
  const result = riskyOperation($json);
  return [{ json: { success: true, result } }];
} catch (error) {
  return [{ json: { 
    success: false, 
    error: error.message,
    originalData: $json 
  }}];
}
```

#### 4.3 Error Workflow

Configura un workflow de errores global (Settings → Error Workflow):
```
Error Trigger → Extract Info → Notify (Slack/Email) → Log to DB
```

---

### Phase 5: Deploy y Monitoreo

#### 5.1 Activación

- Activa el workflow solo cuando esté completamente testeado
- Usa tags para organizar (e.g., "production", "development")
- Documenta en la descripción del workflow

#### 5.2 Monitoreo

**Métricas clave:**
- Ejecuciones exitosas vs fallidas
- Tiempo de ejecución promedio
- Errores por tipo/nodo

**Notificaciones:**
- Configura alertas para fallos consecutivos
- Monitorea credenciales próximas a expirar

---

# Quick Reference

## Nodos por Categoría

| Categoría | Nodos Clave |
|-----------|-------------|
| **Triggers** | Webhook, Schedule, Manual, Execute Workflow Trigger |
| **Data** | HTTP Request, Code, Set, Merge, Split |
| **Control** | IF, Switch, Loop, Wait, Stop and Error |
| **Transform** | Aggregate, Filter, Sort, Limit, Summarize |
| **AI** | OpenAI, Anthropic, LangChain, AI Agent |
| **Communication** | Email, Slack, Discord, Telegram |
| **Database** | PostgreSQL, MySQL, MongoDB, Redis |
| **Files** | Read Binary, Write Binary, Spreadsheet |

## Shortcuts de Expresiones

```javascript
// Input data
$json                    // Current item JSON
$binary                  // Current item binary data
$input.first()          // First input item
$input.last()           // Last input item
$input.all()            // All input items

// Cross-node
$('NodeName').item      // Item at same index from node
$('NodeName').first()   // First item from node
$('NodeName').all()     // All items from node

// Execution context
$execution.id           // Current execution ID
$execution.mode         // 'test' or 'production'
$workflow.id            // Workflow ID
$workflow.name          // Workflow name

// Variables & credentials
$vars.VARIABLE_NAME     // Environment variable
$credentials.name       // Credential field (in expressions)

// Date/Time (Luxon)
$now                    // Current DateTime
$today                  // Today at midnight
```

---

# Reference Files

## 📚 Documentation Library

Load these resources as needed during development:

### Core n8n Documentation
- [📊 n8n Expressions Guide](./reference/n8n_expressions.md) - Complete expression syntax and examples
- [🏗️ Custom Nodes Development](./reference/n8n_custom_nodes.md) - Building TypeScript nodes
- [✅ Best Practices](./reference/n8n_best_practices.md) - Patterns and anti-patterns
- [🤖 AI Integration Guide](./reference/n8n_ai_integration.md) - LLM and agent workflows
- [🔌 API Reference](./reference/n8n_api_reference.md) - REST API and webhooks

### Helper Scripts
- **scripts/workflow_validator.py** - Validate workflow JSON structure
- **scripts/node_scaffolder.py** - Generate custom node boilerplate

### Example Workflows
- **examples/** - Ready-to-import workflow templates

---

# Decision Tree

```
Task → What type of automation?
    │
    ├─ Data sync/ETL → Schedule Trigger + HTTP/DB nodes
    │
    ├─ API endpoint → Webhook Trigger + Processing + Respond to Webhook
    │
    ├─ AI/LLM task → Trigger + Context Prep + AI Node + Action
    │
    └─ Event reaction → Webhook/Trigger → Process → Notify/Action
        │
        └─ Needs sub-logic? → Use Execute Workflow for modularity
```

---

# Common Pitfalls

❌ **Don't** hardcode API keys or secrets in nodes
✅ **Do** use n8n's credential system

❌ **Don't** process thousands of items in a single batch
✅ **Do** use Split In Batches with appropriate batch size

❌ **Don't** ignore error handling
✅ **Do** configure Error Workflow and use try-catch in Code nodes

❌ **Don't** use fixed dates in scheduled workflows
✅ **Do** use relative dates (`$now.minus({days: 1})`)

❌ **Don't** duplicate logic across workflows
✅ **Do** create sub-workflows for reusable components
