---
name: code-fixer
description: Skill especializada para diagnosticar y reparar errores en el motor AGCCE v4.0. Integra análisis de telemetría (logs/telemetry.jsonl), estado del Blackboard, y recuperación de agentes (Graceful Recovery).
---

# 🔧 AGCCE Code Fixer Skill

> **Especialización**: Diagnóstico y reparación del Antigravity Core Copilot Engine (MAS Architecture).

---

## 🔍 Protocolo de Diagnóstico AGCCE

### 1. Análisis de Estado (Blackboard)

Antes de tocar código, verifica si el error es de estado o de lógica.

```powershell
# Ver estado actual de los agentes
python scripts/blackboard.py status

# Ver últimos errores registrados en memoria compartida
python scripts/blackboard.py get errors
```

> **Checklist Blackboard:**
> - [ ] ¿Están los agentes bloqueados en un estado?
> - [ ] ¿Hay inconsistencia en `plan_status`?
> - [ ] ¿El `execution_context` está corrupto?

### 2. Análisis de Telemetría y Logs

Los errores en este sistema distribuido a menudo son silenciosos en la consola pero ruidosos en los logs.

- **Telemetría General**: `logs/telemetry.jsonl`
  - Busca `event_type: "error"` o `severity: "critical"`
- **Recuperación de Agentes**: `logs/recovery_events.jsonl`
  - Revisa si el `GracefulRecovery` intentó revivir un agente y falló.

### 3. Ejecución de Tests Específicos

El proyecto usa `pytest`. No ejecutes toda la suite si solo falló un módulo.

```powershell
# Test de Orquestación (Core)
pytest tests/test_orchestrator.py -v

# Test de Seguridad (Guardian)
pytest tests/test_security_guardian.py -v

# Test de Infraestructura (Queue/Blackboard)
pytest tests/test_task_queue.py -v
```

---

## 🛠️ Patrones de Reparación Comunes

### A. Error de Validación de Plan (Schema Validation)
**Síntoma**: El Orchestrator rechaza un plan generado.
**Solución**:
1. Revisar `schemas/plan_schema.json`.
2. Validar que el `Architect` está generando JSON válido.
3. **Fix**: Ajustar el prompt del `Architect` en `config/agent_profiles/architect.json` o relajar el esquema si es demasiado estricto.

### B. Timeout de Agentes (Context Deadline)
**Síntoma**: `context deadline exceeded` en logs.
**Solución**:
1. Verificar si el agente está entrando en bucle infinito.
2. **Fix**: Aumentar `max_steps` en la configuración del agente o simplificar la tarea en `task_queue.py`.

### C. Fallo de Seguridad (Security Guardian Block)
**Síntoma**: Commit rechazado o alerta del Auditor.
**Solución**:
1. Ejecutar análisis manual: `python scripts/security_guardian.py analyze <archivo>`
2. Aplicar corrección sugerida (Sanitización, Auth check).
3. **Verificar**: Re-ejecutar script de seguridad.

---

## 🚨 Flujo de Emergencia (Emergency Reset)

Si el sistema está completamente roto o inconsistente:

1. **Limpiar Blackboard**:
   ```powershell
   python scripts/blackboard.py clear
   ```
2. **Purgar Cola de Tareas**:
   ```powershell
   python -c "from scripts.task_queue import TaskQueue; TaskQueue().clear()"
   ```
3. **Reiniciar Dashboard**:
   Matar proceso en puerto 8888 y reiniciar `dashboard_server.py`.

---

## ✅ Definition of Done para Fixes

1. **Reproducción**: El error se reprodujo con un test o script.
2. **Corrección**: El código se modificó siguiendo PEP 8.
3. **Validación**:
   - `pytest` pasa en el módulo afectado.
   - `snyk_code_scan` no reporta nuevas vulnerabilidades.
4. **Telemetría**: El fix registra correctamente el evento en los logs.
