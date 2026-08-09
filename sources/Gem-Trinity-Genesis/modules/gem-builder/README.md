# Gem Builder Compiler

**Sistema determinista de compilación de agentes especializados**

---

## 🎯 ¿Qué es este proyecto?

Un **compilador** que transforma especificaciones de casos de uso en **Gem Bundles** (agentes versionados en JSON) listos para ejecutar en AGCCE.

---

## 💬 Cómo Hablar Conmigo (Antigravity)

### ✅ Ejemplos de lo que puedes decir:

1. **"Compila un agente para analizar costos SAP FI con datos sensibles"**
   → Yo creo el Use Case Spec y compilo el Gem Bundle

2. **"Qué Gem Bundles tengo compilados?"**
   → Listo los Gems en `bundles/`

3. **"Valida el Gem Bundle api_auditor_v1.0.0.json"**
   → Ejecuto validación contra schema

4. **"Muéstrame la configuración de MCPs autorizados"**
   → Abro y explico `config/mcp_whitelist.json`

---

## 🚀 Funcionalidades que Puedo Recordarte

Si olvidas mencionar estas cosas, yo te las recuerdo:

### 🔷 Al compilar un Gem:
- ✅ **Risk Score**: Te pregunto el nivel de sensibilidad de datos
- ✅ **Model Routing**: Sugiero Gemini Pro (razonamiento) o Flash (rapidez)
- ✅ **Políticas de Seguridad**: Activo Model Armor si Risk > 60
- ✅ **Grounding Strategy**: Te pregunto si necesita buscar contexto externo
- ✅ **Verifier Checks**: Añado validaciones según el tipo de agente

### 🔷 Después de compilar:
- ✅ Te recuerdo copiar el Gem a `Agente Copilot Engine\gems\`
- ✅ Te sugiero versionado SemVer (v1.0.0, v1.1.0, etc.)
- ✅ Te muestro el hash SHA-256 del system prompt

---

## 📋 Comandos que Ejecuto Por Ti

**NO necesitas recordar estos comandos**, yo los ejecuto automáticamente:

```powershell
# Validar Use Case Spec
python src/validator.py specs/mi_spec.json

# Compilar Gem Bundle
python src/cli.py compile --spec specs/mi_spec.json

# Ver Gems compilados
Get-ChildItem bundles/

# Validar Gem compilado
python src/validator.py bundles/mi_gem_v1.0.0.json --type gem_bundle
```

---

## 📂 Estructura del Proyecto

```
Gem Builder/
├── specs/           → INPUT: Use Case Specs (tú o yo los creamos)
├── bundles/         → OUTPUT: Gem Bundles compilados
├── schemas/         → Schemas de validación
├── config/          → Configuración (MCPs, políticas)
├── .agent/skills/   → Skills del compilador
└── WORKFLOW.md      → Esta guía
```

---

## 🎯 Workflow Típico

1. **TÚ**: "Compila un agente que [descripción del caso de uso]"
2. **YO**: 
   - Creo el Use Case Spec en `specs/`
   - Te pregunto detalles (risk score, MCPs necesarios, etc.)
   - Compilo el Gem Bundle
   - Guardo en `bundles/`
   - Te muestro el resultado

3. **TÚ**: Copias el Gem a `Agente Copilot Engine\gems\`
4. **TÚ**: Vas a AGCCE y me dices qué hacer con ese Gem

---

## ⚙️ Estado Actual

- ✅ Schemas definidos (`gem_bundle.v1.schema.json`)
- ✅ MCPs configurados (whitelist)
- ✅ Skills adaptados (5 skills 100% específicos)
- ⏳ **Compilador Python**: Pendiente de implementación

---

## 💡 Tips

- Habla en **lenguaje natural**, yo traduzco a comandos
- Si olvidas algo, **yo te lo recuerdo**
- Si necesito info adicional, **te pregunto**
- Usa **versionado SemVer** (v1.0.0 → v1.1.0 → v2.0.0)

---

**Versión**: 1.0  
**Última actualización**: 2026-01-19
