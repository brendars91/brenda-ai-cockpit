# 11. Integración con Gem Builder Compiler

> **Sprint 1 Implementado** - AGCCE ahora puede consumir Gem Bundles

---

## 🎯 ¿Qué es Esta Integración?

AGCCE v4.0 ahora puede **cargar Gem Bundles** compilados por Gem Builder Compiler y usarlos para configurar sus agentes MAS dinámicamente.

### Flujo de Trabajo

```
1. Usuario → Gem Builder: "Quiero agente SAP FI analyzer"
2. Gem Builder → Compila: sap_fi_analyzer_v1.0.0.json
3. Usuario → Copia Gem a: Agente Copilot Engine/gems/
4. Usuario → AGCCE: "Ejecuta proyecto con gem sap_fi_analyzer_v1.0.0.json"
5. AGCCE → Carga Gem y configura sus 5 agentes MAS
6. AGCCE → Ejecuta proyecto
```

---

## 📦 Componentes del Sprint 1

### 1. `scripts/gem_loader.py`

Módulo que carga y valida Gem Bundles.

**Funciones principales**:
- `load_gem(gem_path)` - Carga y valida un Gem contra schema
- `convert_to_agent_profile(gem, role)` - Convierte Gem en Agent Profile de AGCCE
- `create_agent_profiles_from_gem(gem_path)` - Crea perfiles para los 5 agentes MAS
- `get_gem_info(gem_path)` - Obtiene metadata sin cargar completamente

**Ejemplo de uso**:
```powershell
python scripts/gem_loader.py gems/sap_cost_analyzer_v1.0.0.json

# Output:
📦 Gem: sap_cost_analyzer v1.0.0
   Model: gemini-3-pro
   Risk Score: 75
   Model Armor: ✓ Enabled
✓ Created 5 agent profiles
```

### 2. `schemas/AGCCE_GemPlan_v1.schema.json`

Schema JSON para GemPlans (híbrido de Plan AGCCE + Gem Bundle).

**Campos clave**:
- `gem_configuration.gem_bundle_path` - Path al Gem Bundle
- `gem_configuration.agent_overrides` - Qué configuración usar (Gem vs default)
- `tasks` - Tareas estilo AGCCE Plan normal

### 3. Directorios Nuevos

```
Agente Copilot Engine/
├── gems/                    # Gem Bundles importados
│   └── sap_cost_analyzer_v1.0.0.json
│
└── config/
    └── gem_profiles/        # Agent profiles generados desde Gems
        ├── sap_cost_analyzer_researcher.json
        ├── sap_cost_analyzer_architect.json
        └── ...
```

### 4. `scripts/orchestrator.py` (Modificado)

**Nuevas capacidades**:
- Detecta GemPlans (`is_gemplan()`)
- Carga Gem Bundles antes de ejecutar
- Configura agentes MAS con configuración del Gem

---

## 🚀 Uso

### Paso 1: Compilar Gem en Gem Builder

```powershell
cd "C:\Users\ASUS\.gemini\Mis carpetas\Gem Builder"

# Crear Use Case Spec
$spec = @"
{
  "use_case_id": "api_auditor",
  "goal": "Auditar APIs REST para OWASP Top 10",
  "data_sources": [{"type": "api"}],
  "actions": [{"type": "analyze"}]
}
"@ | Out-File specs/api_auditor.json -Encoding UTF8

# Compilar (cuando el compilador esté implementado)
python src/cli.py compile --spec specs/api_auditor.json

# Output: bundles/api_auditor_v1.0.0.json
```

### Paso 2: Importar Gem a AGCCE

```powershell
cd "C:\Users\ASUS\.gemini\Agente Copilot Engine"

# Copiar Gem Bundle
Copy-Item "../Mis carpetas/Gem Builder/bundles/api_auditor_v1.0.0.json" gems/
```

### Paso 3: Crear GemPlan

**Opción Manual**:
```json
// plans/api_audit_gemplan.json
{
  "plan_id": "gemplan_api_audit_001",
  "goal": "Auditar API de autenticación",
  "tasks": [
    {
      "agent": "researcher",
      "action": "search_api_endpoints",
      "context": "Encontrar todos los endpoints de /api/auth/"
    },
    {
      "agent": "auditor",
      "action": "security_review",
      "focus": ["owasp_top_10", "auth_bypass"]
    },
    {
      "agent": "constructor",
      "action": "implement_fixes",
      "output_path": "api/auth_fixed.py"
    }
  ],
  "gem_configuration": {
    "gem_bundle_path": "gems/api_auditor_v1.0.0.json",
    "gem_version": "1.0.0",
    "gem_use_case_id": "api_auditor",
    "agent_overrides": {
      "system_prompt_source": "gem",
      "model_source": "gem",
      "policies_source": "strictest"
    }
  },
  "schema_version": "AGCCE_GemPlan_v1",
  "created_at": "2026-01-19T11:00:00Z"
}
```

### Paso 4: Ejecutar con AGCCE

```powershell
python scripts/orchestrator.py plans/api_audit_gemplan.json

# Log output:
🔷 GemPlan detected!
Loading Gem Bundle configuration...

📦 Gem: api_auditor v1.0.0
   Compiled: 2026-01-19T10:30:00Z
   Model: gemini-3-pro
   Risk Score: 60
   Model Armor: ✓ Enabled
   Grounding: google_search

✓ Created 5 agent profiles in config/gem_profiles/
✓ Gem loaded and agents configured

=== FASE 1: PRE-FLIGHT CHECK ===
...
✓ PIPELINE COMPLETED SUCCESSFULLY
```

---

## 📋 Agent Profiles Generados desde Gems

Cuando AGCCE carga un Gem, genera automáticamente perfiles para los 5 agentes:

```json
// config/gem_profiles/api_auditor_researcher.json
{
  "agent_id": "api_auditor_researcher",
  "role": "researcher",
  "version": "1.0.0",
  
  "system_prompt": "Eres un experto en...",  // Del Gem
  "system_prompt_hash": "a3f2b8c9...",
  
  "model": "gemini-3-pro",  // Del Gem
  
  "policies": {
    "model_armor": true,  // Del Gem
    "hitl_required": true,
    "read_only_tools": false
  },
  
  "allowed_mcps": ["database", "fetch"],  // Del Gem (tools sin side-effects)
  "forbidden_mcps": ["filesystem"],
  
  "grounding": "google_search",  // Del Gem
  
  "gem_source": "api_auditor",
  "risk_score": 60
}
```

---

## 🧪 Testing

```powershell
# Test 1: Cargar Gem manualmente
python scripts/gem_loader.py gems/test_gem_v1.0.0.json

# Test 2: Validar GemPlan contra schema
# (requiere implementar validate_gemplan.py)

# Test 3: Dry-run de GemPlan
python scripts/orchestrator.py plans/test_gemplan.json
```

---

## 🚧 Pendiente (Sprints 2 y 3)

### Sprint 2: Generación y CLI
- [ ] `scripts/gem_plan_generator.py` - Generador interactivo de GemPlans
- [ ] `agcce_cli.py gemplan create` - Comando CLI
- [ ] `.agent/skills/gem-integration/SKILL.md` - Skill documentado

### Sprint 3: Features Avanzados
- [ ] Versionado de Gems (verificar compatibilidad)
- [ ] Cache de Agent Profiles
- [ ] Dashboard: mostrar Gems activos
- [ ] Gem Registry integration

---

## 🔧 Troubleshooting

### Error: "gem_loader.py not found"
```powershell
# Verificar que existe
Get-ChildItem "scripts/gem_loader.py"

# Si no existe, reinstalar desde repositorio
```

### Error: "Gem Bundle not found"
```powershell
# Verificar path en GemPlan
Get-Content plans/mi_gemplan.json | Select-String "gem_bundle_path"

# Verificar que el Gem existe
Get-ChildItem gems/
```

### Error: "Schema validation failed"
```powershell
# Instalar jsonschema
pip install jsonschema

# Validar Gem manualmente
python -c "import json, jsonschema; ..."
```

---

## 📚 Referencias

- [Master Spec Gem Builder](../Mis%20carpetas/Gem%20Builder/Gem%20Builder.txt)
- [Gem Bundle Schema](../Mis%20carpetas/Gem%20Builder/schemas/gem_bundle.v1.schema.json)
- [Integration Plan](../../antigravity/brain/.../integration_plan_agcce_gem.md)

---

**Estado**: ✅ Sprint 1 Completado  
**Versión AGCCE**: 1.2.0-GEM-ENABLED  
**Fecha**: 2026-01-19
