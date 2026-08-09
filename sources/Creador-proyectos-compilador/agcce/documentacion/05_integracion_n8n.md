# 05. Integración con n8n

## 🎯 Objetivo

La integración con n8n permite que AGCCE Ultra notifique eventos críticos a canales externos (Slack, Email, Jira, etc.) de forma automática.

---

## 📊 Arquitectura de Integración

```
AGCCE Ultra                           n8n
┌──────────────────┐                ┌──────────────────┐
│ event_dispatcher │ ──── HTTP ────► │ Webhook Trigger  │
│    (Python)      │    POST        │                  │
└──────────────────┘                └────────┬─────────┘
                                             ▼
                                    ┌──────────────────┐
                                    │ Process & Format │
                                    └────────┬─────────┘
                                             ▼
                                    ┌──────────────────┐
                                    │ Slack / Email /  │
                                    │ Jira / Custom    │
                                    └──────────────────┘
```

---

## 🔔 Eventos Soportados

| Evento | Descripción | Severidad |
|--------|-------------|-----------|
| `PLAN_VALIDATED` | Plan generado y validado exitosamente | Info |
| `EXECUTION_ERROR` | Error durante la ejecución | High |
| `EVIDENCE_READY` | Evidencia lista para envío | Info |
| `SECURITY_BREACH_ATTEMPT` | Intento de brecha de seguridad | Critical |
| `HIGH_LATENCY_THRESHOLD` | Umbral de latencia excedido | Warning |
| `HITL_TIMEOUT` | Timeout esperando aprobación humana | Warning |
| `HEARTBEAT` | Healthcheck ping | Info |

---

## 📦 Workflows n8n Incluidos

### 1. Evidence Report Sender
**Archivo:** `n8n/evidence_report_sender.json`

**Flujo:**
1. Recibe webhook EVIDENCE_READY
2. Formatea mensaje con resumen
3. Envía a Slack y/o Email
4. Responde con confirmación

**Ejemplo de mensaje:**
```
📋 AGCCE Evidence Report

Plan ID: PLAN-NK4X29GS
Objective: Implementar validación de inputs
Progress: 5/5 steps
Verification: ✅ Passed
Evidence Path: /evidence/PLAN-NK4X29GS.json
```

---

### 2. Execution Error Handler
**Archivo:** `n8n/execution_error_handler.json`

**Flujo:**
1. Recibe webhook EXECUTION_ERROR
2. Formatea alerta de error
3. Envía a canal de alertas Slack
4. Responde con confirmación

**Ejemplo de alerta:**
```
🚨 AGCCE Execution Error

Plan ID: PLAN-NK4X29GS
Step ID: S03
Severity: HIGH
Error: FileNotFoundError: /path/to/file.py

Requiere atención inmediata
```

---

### 3. Security Alert Handler
**Archivo:** `n8n/security_alert_handler.json`

**Flujo:**
1. Recibe webhook SECURITY_BREACH_ATTEMPT
2. Formatea alerta crítica
3. Envía a canal de seguridad
4. Responde con confirmación

**Ejemplo de alerta:**
```
🔴 SECURITY ALERT - AGCCE

Severity: CRITICAL
Alert Type: snyk_code_block
Plan ID: PLAN-NK4X29GS
Details: {
  "critical": 2,
  "high": 5
}

⚠️ Acción inmediata requerida
```

---

## ⚙️ Configuración

### Paso 1: Importar Workflows en n8n

1. Abrir tu instancia n8n
2. Ir a Workflows → Import
3. Seleccionar cada archivo JSON de `n8n/`
4. Guardar e importar

### Paso 2: Configurar Credenciales

Para cada workflow, configurar:

**Slack:**
- Crear app en Slack
- Obtener OAuth token
- Añadir credencial en n8n

**Email:**
- Configurar servidor SMTP
- Añadir credencial en n8n

### Paso 3: Activar Workflows

1. Abrir cada workflow
2. Click en "Active" toggle
3. Notar la URL del webhook

### Paso 4: Configurar AGCCE

Editar `config/n8n_webhooks.json`:

```json
{
  "PLAN_VALIDATED": "https://tu-n8n.com/webhook/xxx-plan-validated",
  "EXECUTION_ERROR": "https://tu-n8n.com/webhook/xxx-execution-error",
  "EVIDENCE_READY": "https://tu-n8n.com/webhook/xxx-evidence-ready",
  "SECURITY_BREACH_ATTEMPT": "https://tu-n8n.com/webhook/xxx-security-alert",
  "HEARTBEAT": "https://tu-n8n.com/webhook/xxx-heartbeat"
}
```

O usar el configurador interactivo:
```powershell
python scripts/event_dispatcher.py configure
```

### Paso 5: Verificar Conexión

```powershell
python scripts/event_dispatcher.py healthcheck
```

---

## 🔄 Retry y Resiliencia

### Retry con Backoff

Si el envío falla, el dispatcher reintenta automáticamente:

| Intento | Delay |
|---------|-------|
| 1 | 0s (inmediato) |
| 2 | 1s |
| 3 | 5s |
| 4 | 15s |

### Cola Local

Si todos los intentos fallan, el evento se guarda en:
```
logs/queue.jsonl
```

Para procesar la cola manualmente:
```powershell
python scripts/event_dispatcher.py process-queue
```

---

## 📝 System Context

Cada payload incluye automáticamente:

```json
{
  "system_context": {
    "bundle_id": "BNDL-AGCCE-ULTRA-V2-FINAL",
    "bundle_version": "2.0.0-ULTRA-FINAL",
    "model_id": "gemini-2.5-pro",
    "hostname": "MI-PC",
    "dispatcher_version": "2.0.0-FINAL"
  }
}
```

Esto permite generar analíticas por modelo/versión en n8n.

---

## 🔒 Idempotencia

Cada evento incluye un `idempotency_key` basado en:
- Tipo de evento
- Plan ID

Si intentas enviar el mismo evento dos veces, el segundo será ignorado.

Para forzar re-envío:
```python
EventDispatcher.emit("PLAN_VALIDATED", payload, force=True)
```
