---
description: Generar Plan JSON automaticamente con Self-Correction
---

# Auto-Plan Workflow

Genera planes JSON automaticamente con validacion integrada.

## Comando Basico
```powershell
python scripts/plan_generator.py --objective "Descripcion de la tarea"
```

## Con Archivos Afectados
```powershell
python scripts/plan_generator.py --objective "Implementar validacion" --files "src/auth.py,src/login.py"
```

## Self-Correction Loop

El generador incluye correccion automatica:

```
1. Genera plan inicial
2. Valida con validate_plan.py
3. Si falla -> Corrige automaticamente
4. Reintenta hasta 3 veces
5. Si sigue fallando -> Solicita ayuda humana
```

## Salida

Los planes se guardan en `plans/`:
- `PLAN-XXXXXXXX.json` - Plan valido
- `_FAILED_PLAN-XXXXXXXX.json` - Plan que requiere revision humana

## Flujo Completo

1. Indexar codebase: `/rag-index`
2. Generar plan: `/auto-plan`
3. Ejecutar: `python scripts/orchestrator.py plans/PLAN-XXX.json`
