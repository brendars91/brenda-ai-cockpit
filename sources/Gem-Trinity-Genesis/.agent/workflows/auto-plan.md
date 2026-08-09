---
description: Generar Plan JSON estructurado antes de ejecutar cualquier modificación
---

# /auto-plan Workflow

Este workflow genera un plan JSON estructurado con corrección automática antes de hacer cambios.

## Pasos

1. **Analizar el prompt del usuario**
   - Extraer objetivos principales
   - Identificar archivos afectados
   - Estimar complejidad

2. **Generar plan JSON**
   ```json
   {
     "plan_id": "uuid",
     "objectives": ["..."],
     "files_to_modify": ["..."],
     "steps": [
       {"step": 1, "action": "...", "file": "...", "risk": "low|medium|high"}
     ],
     "estimated_time": "Xm",
     "requires_approval": true|false
   }
   ```

3. **Validar plan**
   - Verificar archivos existen
   - Comprobar no hay conflictos
   - Calcular score de riesgo

4. **Corregir si hay errores**
   - Re-generar secciones con errores
   - Ajustar estimaciones

5. **Presentar al usuario para aprobación** (si `requires_approval: true`)

## Ejemplo

```
Usuario: "Añade autenticación JWT al API"

auto-plan output:
{
  "plan_id": "abc123",
  "objectives": ["Implementar JWT auth", "Proteger endpoints", "Añadir middleware"],
  "files_to_modify": ["api_server.py", "auth_middleware.py"],
  "steps": [
    {"step": 1, "action": "Crear auth_middleware.py", "file": "NEW", "risk": "low"},
    {"step": 2, "action": "Modificar api_server.py", "file": "api_server.py", "risk": "medium"}
  ],
  "estimated_time": "15m",
  "requires_approval": true
}
```

// turbo-all
