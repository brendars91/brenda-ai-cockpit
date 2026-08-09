---
name: capability-router
description: Router determinista que analiza un Use Case Spec y decide qué capacidades de arquitectura activar en el Gem Bundle (Model Routing, RAG Strategy, Toolset).
---

# Capability Router (Gem Builder Edition)

## Propósito

Analizar un **Use Case Spec** validado y determinar la **Arquitectura del Gem** óptima, seleccionando las capacidades técnicas necesarias.

## Entradas

1. **Use Case Spec** (JSON validado)
   - `goal`: Objetivo del agente
   - `data_sources`: Fuentes y sensibilidad
   - `constraints`: Latencia, coste

2. **Matriz de Capacidades** (interna)
   - Modelos: Gemini 3 Pro vs Flash
   - Grounding: Google Search vs RAG vs URL Context
   - Tools: Code Execution vs MCP vs Read-Only

## Algoritmo de Decisión

### Paso A: Model Routing
- Si `reasoning_depth == high` O `coding_complexity > medium` → **Gemini 3 Pro**
- Si `latency < 2s` O `task == classification` → **Gemini 3 Flash**

### Paso B: Knowledge & Grounding
- Si `data_sources` incluye `drive/docs` → Activar **Drive RAG**
- Si `data_sources` es `url` → Activar **Fetch Context**
- Si `knowledge_cutoff` es crítico → Activar **Google Search**

### Paso C: Toolset Planning
- Si `actions` requieren `side_effects` → Activar **MCP con HITL**
- Si `actions` requieren cálculo → Activar **Code Sandbox**

## Salida (JSON Fragment)

```json
{
  "selected_capabilities": [
    "model:gemini-3-pro",
    "grounding:google-search",
    "security:model-armor"
  ],
  "reasoning": "Se elige Pro por complejidad de razonamiento. Search activado por datos volátiles.",
  "risk_assessment": "High (Financial Data) -> Model Armor required"
}
```
