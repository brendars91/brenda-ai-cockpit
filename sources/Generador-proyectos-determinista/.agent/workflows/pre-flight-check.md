---
description: Verificación previa antes de proponer cambios de código
---

# Pre-Flight Check Workflow

Validaciones obligatorias antes de proponer cualquier cambio.

## Secuencia de Checks

### 1. Estado del Repositorio
// turbo
```powershell
git status --porcelain
```

### 2. Lint Check (Python)
```powershell
python scripts/lint_check.py <archivo_o_directorio>
```

### 3. Type Check (Python)
```powershell
python scripts/type_check.py <archivo_o_directorio>
```

### 4. Validar Plan JSON (si aplica)
```powershell
python scripts/validate_plan.py <plan.json>
```

### 5. Tests Unitarios
```powershell
pytest tests/ -v --tb=short
```

---

## Matriz de Decisión

| Git Status | Lint | Types | Tests | Acción |
|------------|------|-------|-------|--------|
| ✅ clean | ✅ | ✅ | ✅ | Continuar |
| ⚠️ dirty | ✅ | ✅ | ✅ | Notificar, esperar |
| ✅ clean | ❌ | * | * | Corregir lint primero |
| ✅ clean | ✅ | ❌ | * | Corregir types |
| ✅ clean | ✅ | ✅ | ❌ | Investigar tests |

---

## Criterios de Bloqueo

El pre-flight check **BLOQUEA** la emisión de plan si:

1. **Errores de sintaxis** en archivos a modificar
2. **Imports faltantes** detectados
3. **Tests fallando** en módulos afectados
4. **Cambios no commiteados** en archivos objetivo

---

## Integración con Snyk

> ⚠️ **IMPORTANTE**: Según directivas v1.1.0, Snyk solo se ejecuta en:
> - Pre-flight Check (AQUÍ) ✅
> - Verification Report ✅

### Scan de Seguridad (opcional)
```powershell
# Solo si hay cambios en dependencias
snyk test --severity-threshold=high
```
