# 07. Seguridad

## 🛡️ Principios de Seguridad

AGCCE Ultra implementa **Security by Design** con múltiples capas de protección.

---

## 🔒 Controles de Seguridad

### 1. Gate Snyk (Code Scan)

**Script:** `pre_commit_hook.py`

**Funcionamiento:**
- Escanea código fuente antes de cada commit
- Detecta vulnerabilidades en el código
- Bloquea commits con severidad Critical o High

**Comando Snyk:**
```powershell
snyk code test --severity-threshold=high
```

### 2. Snyk-Diff Policy (Dependencias)

**Script:** `pre_commit_hook.py`

**Funcionamiento:**
- Detecta cambios en `requirements.txt`, `package.json`
- Analiza solo el delta (nuevas dependencias)
- Bloquea si las nuevas dependencias tienen vulnerabilidades

**Archivos monitoreados:**
- `requirements.txt`
- `package.json`
- `package-lock.json`
- `Pipfile`
- `Pipfile.lock`

### 3. Semantic Verification (Anti-Alucinación)

**Script:** `plan_generator.py`

**Funcionamiento:**
- Valida que todos los paths en el plan existan
- Verifica contra filesystem y/o índice RAG
- Si un path no existe, marca como "alucinación" y reintenta

**Ejemplo de rechazo:**
```
[X] Semantic Verification Failed: 
    Path 'src/fake_module.py' no existe en filesystem ni indice RAG
    Clasificado como: ALUCINACION_DE_ENTIDAD
    Reintentando generacion...
```

### 4. HITL Gate (Human-in-the-Loop)

**Script:** `hitl_gate.py`

**Funcionamiento:**
- Requiere aprobación humana para operaciones de escritura
- Muestra diff/patch antes de aplicar
- No permite bypass

### 5. Idempotencia

**Script:** `event_dispatcher.py`

**Funcionamiento:**
- Cada evento tiene un `idempotency_key`
- Basado en `event_type` + `plan_id`
- Previene ejecuciones duplicadas

---

## ⛔ Prohibiciones Absolutas

### 1. Bypass de Snyk
```
PROHIBIDO: git commit --no-verify
```

El bypass de Snyk está **absolutamente prohibido** por las directivas de AGCCE.

### 2. Referenciar Paths Sin Verificar

Todo path mencionado en un plan debe ser verificado antes de ser incluido.

### 3. Aplicar Cambios Sin HITL

No se pueden aplicar cambios de escritura/eliminación sin aprobación humana.

---

## 📊 Métricas de Seguridad

### Disponibles en Dashboard

| Métrica | Descripción |
|---------|-------------|
| Snyk Scans | Total de scans ejecutados |
| Commits Blocked | Commits bloqueados por vulnerabilidades |
| Vulnerabilities Found | Total de vulnerabilidades detectadas |
| Unauthorized Paths Blocked | Alucinaciones detectadas |

### Timeline de Seguridad

Eventos recientes visibles en:
- Dashboard → Security Timeline
- CLI: `python scripts/metrics_collector.py timeline 7`

---

## 🔐 Governance

Definido en `config/bundle.json`:

```json
{
  "governance": {
    "hitl": "mandatory_on_write",
    "security_gate": "Snyk_Hard_Block",
    "idempotency": "plan_id_enforced"
  }
}
```

| Política | Valor | Significado |
|----------|-------|-------------|
| `hitl` | mandatory_on_write | HITL requerido para escrituras |
| `security_gate` | Snyk_Hard_Block | Bloqueo duro en vulnerabilidades |
| `idempotency` | plan_id_enforced | Idempotencia obligatoria |

---

## 📝 Reglas AGCCE Ultra

Definidas en `.agent/rules/agcce_ultra_rules.md`:

### RAG Management
- Priorizar `smart-coding-mcp` para búsqueda semántica
- Verificar estado del índice antes de planificar
- Ejecutar indexación incremental regularmente

### Self-Correction
- Usar tracebacks para corrección
- Validar existencia de paths
- Máximo 3 reintentos

### Security Enforcement
- Snyk bypass PROHIBIDO
- Snyk-Diff en cada cambio de dependencias
- Alertas de seguridad a n8n

---

## 🚨 Alertas de Seguridad

### Eventos que disparan alertas:

| Evento | Severidad | Acción |
|--------|-----------|--------|
| `SECURITY_BREACH_ATTEMPT` | Critical | Notificación inmediata a n8n |
| Snyk Critical Finding | Critical | Bloqueo de commit |
| Snyk High Finding | High | Bloqueo de commit |
| Unauthorized Path | Warning | Reintento de generación |

### Configurar canal de alertas:

Editar `config/n8n_webhooks.json`:
```json
{
  "SECURITY_BREACH_ATTEMPT": "https://tu-n8n.com/webhook/security-alerts"
}
```

---

## 🔍 Auditoría

### Logs de Auditoría

Todos los eventos de seguridad se registran en:
```
logs/security_events.jsonl
```

Formato:
```json
{
  "timestamp": "2026-01-17T12:30:00",
  "type": "security.event",
  "metrics": {
    "event_type": "snyk_code_block",
    "blocked": true,
    "severity": "critical",
    "details": { ... }
  }
}
```

### Retención
- 30 días por defecto
- Configurable vía `cleanup`

---

## 🛠️ Respuesta a Incidentes

### 1. Vulnerabilidad Detectada en Código

```powershell
# Ver detalles
snyk code test

# Corregir el código
# ...

# Reintentar commit
git add -A
git commit -m "fix: resolve security vulnerability"
```

### 2. Vulnerabilidad en Dependencia

```powershell
# Ver vulnerabilidades
snyk test

# Actualizar dependencia
pip install package==safe_version

# Actualizar requirements.txt
pip freeze > requirements.txt

# Commit
git add -A
git commit -m "fix: upgrade vulnerable dependency"
```

### 3. Alucinación Detectada

El sistema automáticamente:
1. Rechaza el plan
2. Registra en telemetría
3. Reintenta con contexto adicional
4. Si falla 3 veces, solicita intervención humana
