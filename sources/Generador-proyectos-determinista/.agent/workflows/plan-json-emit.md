---
description: Emitir un Plan JSON estructurado antes de cualquier acción
---

# Plan JSON Emit Workflow

Workflow para generar un Plan JSON válido según el schema AGCCE_Plan_v1.

## Prerequisitos
- Objetivo claro definido
- Archivos objetivo identificados
- Pre-flight check ejecutado

## Proceso de Emisión

### 1. Verificar estado Git (obligatorio según directiva v1.1.0 §3)
// turbo
```powershell
git status --porcelain
```

Si hay cambios:
- Notificar al usuario
- Esperar confirmación antes de continuar

### 2. Estructura del Plan JSON

```json
{
  "plan_id": "PLAN-XXXXXXXX",
  "version": "1.1",
  "created_at": "ISO-8601 timestamp",
  "objective": {
    "description": "Descripción clara del objetivo",
    "success_criteria": ["Criterio 1", "Criterio 2"],
    "affected_files": ["ruta/archivo1.py", "ruta/archivo2.py"]
  },
  "pre_flight_check": {
    "git_status": "clean|dirty",
    "lint_passed": true|false,
    "tests_passed": true|false
  },
  "steps": [
    {
      "id": "S01",
      "action": "read_file|write_file|...",
      "target": "ruta/objetivo",
      "hitl_required": false,
      "expected_outcome": "Resultado esperado"
    }
  ],
  "verification": {
    "method": "automated|manual|hybrid",
    "commands": ["comando1", "comando2"]
  },
  "commit_proposal": {
    "type": "feat|fix|docs|refactor",
    "scope": "modulo",
    "message": "descripción del cambio"
  }
}
```

### 3. Generar ID único
```powershell
# PowerShell - generar ID aleatorio
$planId = "PLAN-" + (-join ((65..90) + (48..57) | Get-Random -Count 8 | % {[char]$_}))
Write-Output $planId
```

### 4. Validar plan generado
```powershell
python scripts/validate_plan.py <plan.json>
```

### 5. Si validación falla → Regenerar automáticamente
Según directiva v1.1.0 §4, si `validate_plan.py` retorna error:
1. NO notificar al usuario
2. Corregir errores automáticamente
3. Re-validar hasta que pase

---

## Acciones Válidas

| Acción | Descripción | HITL |
|--------|-------------|------|
| `read_file` | Leer contenido de archivo | No |
| `write_file` | Crear/modificar archivo | **Sí** |
| `delete_file` | Eliminar archivo | **Sí** |
| `run_command` | Ejecutar comando shell | Depende |
| `docker_compose_up` | Levantar servicios Docker | No |
| `docker_run_tests` | Tests en contenedor | No |
| `docker_fetch_logs` | Obtener logs Docker | No |
| `lint_check` | Verificar estilo de código | No |
| `type_check` | Verificar tipos | No |
| `snyk_scan` | Scan de seguridad | No |
| `git_commit` | Commit de cambios | **Sí** |

---

## Ejemplo Completo

Ver: `examples/example_plan_auth_fix.json`

---

## Checklist de Emisión

- [ ] `git status` ejecutado
- [ ] `plan_id` único generado
- [ ] `objective.description` claro y específico
- [ ] `affected_files` listados
- [ ] Cada paso tiene `id` único (S01, S02, etc.)
- [ ] Acciones de escritura tienen `hitl_required: true`
- [ ] `verification.commands` definidos
- [ ] `commit_proposal` con formato Conventional Commits
- [ ] Plan validado con `validate_plan.py`
