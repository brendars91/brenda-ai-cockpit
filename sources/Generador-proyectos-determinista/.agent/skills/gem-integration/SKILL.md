---
name: gem-integration
description: Skill especializado en integración de Gem Bundles compilados por Gem Builder Compiler en AGCCE v4.0. Permite configurar agentes MAS dinámicamente desde Gems versionados.
---

# GemIntegration Skill

## Propósito

Facilitar la integración entre **Gem Builder Compiler** (generador de Gem Bundles) y **AGCCE v4.0** (ejecutor multi-agente).

## ¿Qué es un Gem Bundle?

Un **Gem Bundle** es un artefacto JSON versionado compilado por Gem Builder que contiene:
- System Prompt con hash SHA-256
- Model Routing (Pro vs Flash)
- Políticas anti-alucinación y seguridad
- Tool Contracts (MCPs permitidos)
- Knowledge Plan (grounding strategies)
- Verifier Checks
- Eval Suite

## Flujo de Integración

```
1. Usuario → Gem Builder
   "Quiero agente SAP FI analyzer"

2. Gem Builder → Compila
   bundles/sap_fi_analyzer_v1.0.0.json

3. Usuario → Copia Gem
   Agente Copilot Engine/gems/sap_fi_analyzer_v1.0.0.json

4. Usuario → Genera GemPlan
   python scripts/gem_plan_generator.py --interactive

5. AGCCE → Ejecuta
   python scripts/orchestrator.py plans/gemplan.json
```

## Componentes

### 1. `scripts/gem_loader.py`

Carga y valida Gem Bundles, convirtiéndolos en Agent Profiles de AGCCE.

**Uso**:
```powershell
python scripts/gem_loader.py gems/mi_gem_v1.0.0.json
```

### 2. `scripts/gem_plan_generator.py`

Genera GemPlans (híbrido de Plan AGCCE + Gem Bundle).

**Uso Interactivo**:
```powershell
python scripts/gem_plan_generator.py --interactive
```

**Uso Directo**:
```powershell
python scripts/gem_plan_generator.py \
  --gem gems/api_auditor_v1.0.0.json \
  --goal "Auditar API REST" \
  --output plans/api_audit.json
```

### 3. `agcce_cli.py` (Extendido)

CLI con opción de GemPlan:
```
[3] Generar GemPlan  - Crea plan desde Gem Bundle 🔷
```

### 4. `orchestrator.py` (Modificado)

Detecta GemPlans automáticamente y carga Gems antes de ejecutar.

## Agent Profiles desde Gems

Cuando AGCCE carga un Gem, genera automáticamente perfiles para los 5 agentes MAS:

```json
// config/gem_profiles/api_auditor_researcher.json
{
  "agent_id": "api_auditor_researcher",
  "system_prompt": "...",  // Del Gem
  "model": "gemini-3-pro", // Del Gem
  "policies": {...},       // Del Gem
  "allowed_mcps": [...],   // Del Gem (tools sin side-effects)
  "risk_score": 60
}
```

## Schemas

### AGCCE_GemPlan_v1

```json
{
  "plan_id": "gemplan_...",
  "goal": "Objetivo del usuario",
  "tasks": [...],  // Tareas AGCCE
  "gem_configuration": {
    "gem_bundle_path": "gems/mi_gem_v1.0.0.json",
    "gem_version": "1.0.0",
    "agent_overrides": {
      "system_prompt_source": "gem",  // vs "default"
      "model_source": "gem",
      "policies_source": "strictest"
    }
  },
  "schema_version": "AGCCE_GemPlan_v1"
}
```

## Ventajas

| Beneficio | Descripción |
|-----------|-------------|
| **Versionado** | Gems versionados (SemVer) con trazabilidad |
| **Estandarización** | System prompts consistentes en equipo |
| **A/B Testing** | Probar diferentes configs de agentes |
| **Marketplace** | Importar Gems de terceros |
| **Auditabilidad** | Cada Gem tiene hash verificable |
| **Risk Engine** | Políticas automáticas según Risk Score |

## Troubleshooting

### Error: "gem_loader.py not found"
```powershell
# Verificar
Get-ChildItem "scripts/gem_loader.py"
```

### Error: "Gem Bundle not found"
```powershell
# Listar Gems
Get-ChildItem gems/

# Copiar Gem desde Gem Builder
Copy-Item "../Mis carpetas/Gem Builder/bundles/mi_gem.json" gems/
```

### Error: "Schema validation failed"
```powershell
# Instalar jsonschema
pip install jsonschema
```

## Referencias

- [Gem Bundle Schema](../../Mis%20carpetas/Gem%20Builder/schemas/gem_bundle.v1.schema.json)
- [Integration Plan](../../antigravity/brain/.../integration_plan_agcce_gem.md)
- [Documentación](../documentacion/11_gem_integration.md)

---

**Estado**: ✅ Sprint 2 Completado  
**Versión AGCCE**: 1.2.0-GEM-ENABLED
