# 06. Observabilidad

## 📊 Telemetry Contract: AGCCE-OBS-V1

AGCCE Ultra implementa un contrato de telemetría estándar para observabilidad completa.

---

## 📈 Métricas Disponibles

### Reliability (Fiabilidad)

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `plan_success_rate` | Porcentaje | Tasa de éxito de planes generados |
| `self_correction_attempts` | Entero | Total de auto-correcciones |
| `hallucinations_blocked` | Entero | Alucinaciones detectadas y bloqueadas |

### Performance (Rendimiento)

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `rag_indexing_ms` | Latencia | Tiempo de indexación RAG |
| `plan_generation_ms` | Latencia | Tiempo de generación de plan |
| `delta_index_efficiency` | Porcentaje | Eficiencia del indexado incremental |

### Security (Seguridad)

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `snyk_vulnerabilities_prevented` | Entero | Vulnerabilidades detectadas |
| `snyk_diff_blocks` | Entero | Bloqueos por Snyk-Diff |
| `unauthorized_path_attempts` | Entero | Intentos de paths no autorizados |

---

## 📁 Persistencia

### Archivos de Logs

| Archivo | Propósito | Formato |
|---------|-----------|---------|
| `logs/telemetry.jsonl` | Métricas generales | JSONL (append-only) |
| `logs/security_events.jsonl` | Eventos de seguridad | JSONL (append-only) |
| `logs/events.jsonl` | Log de eventos dispatcher | JSONL |
| `logs/queue.jsonl` | Cola local (resiliencia) | JSONL |

### Retención

- **Política**: 30 días
- **Limpieza**: `python scripts/metrics_collector.py cleanup`

---

## 🖥️ Dashboard

### Iniciar Dashboard

```powershell
# Puerto por defecto (8080)
python scripts/dashboard_server.py

# Puerto personalizado
python scripts/dashboard_server.py --port 8888
```

### URL de Acceso
```
http://localhost:8888/dashboard/index.html
```

### Secciones del Dashboard

1. **Header**
   - Logo AGCCE Ultra
   - Estado de conexión (verde = conectado)

2. **Reliability**
   - Plan Success Rate (%)
   - Self-Corrections (total)
   - Hallucinations Blocked (total)

3. **Performance**
   - Avg Plan Generation (ms)
   - Avg RAG Indexing (ms)
   - Delta Index Efficiency (%)

4. **Security**
   - Snyk Scans (total)
   - Commits Blocked (total)

5. **Activity Chart**
   - Gráfico de actividad semanal
   - Planes generados vs Bloqueos Snyk

6. **Security Timeline**
   - Eventos de seguridad recientes
   - Timestamps y severidad

### Auto-Refresh

El dashboard se actualiza automáticamente cada 30 segundos.

---

## 📊 API de Métricas

### Ver Resumen (CLI)

```powershell
# Últimos 7 días
python scripts/metrics_collector.py summary 7

# Últimos 30 días
python scripts/metrics_collector.py summary 30
```

**Ejemplo de output:**
```json
{
  "period_days": 7,
  "total_entries": 42,
  "reliability": {
    "plans_generated": 15,
    "plans_successful": 14,
    "success_rate_pct": 93.33,
    "total_self_corrections": 3,
    "hallucinations_blocked": 2
  },
  "performance": {
    "avg_plan_generation_ms": 1250,
    "avg_rag_indexing_ms": 850,
    "avg_delta_efficiency_pct": 75.5
  },
  "security": {
    "snyk_scans": 20,
    "vulnerabilities_found": 5,
    "commits_blocked": 2,
    "unauthorized_paths_blocked": 1
  }
}
```

### Ver Timeline de Seguridad (CLI)

```powershell
python scripts/metrics_collector.py timeline 7
```

**Ejemplo de output:**
```
2026-01-17T12:30:00 [CRITICAL] snyk_code_block
2026-01-16T15:45:00 [HIGH] snyk_diff_block
2026-01-15T09:20:00 [WARNING] unauthorized_path
```

---

## 📝 Uso Programático

### Registrar Métricas

```python
from metrics_collector import Telemetry

# Plan generado
Telemetry.record_plan_generated(
    success=True,
    attempts=1,
    hallucinations_blocked=0,
    latency_ms=1250,
    plan_id="PLAN-XXX"
)

# Indexación RAG
Telemetry.record_rag_indexing(
    files_indexed=150,
    incremental=True,
    delta_files=5,
    latency_ms=850
)

# Scan de Snyk
Telemetry.record_snyk_scan(
    scan_type="code",
    vulnerabilities_found=0,
    critical_count=0,
    high_count=0,
    blocked_commit=False
)

# Evento de seguridad
Telemetry.record_security_event(
    event_type="unauthorized_path",
    blocked=True,
    severity="warning",
    file_path="/fake/path.py"
)
```

### Leer Métricas

```python
from metrics_collector import TelemetryReader
from datetime import datetime, timedelta

# Leer todas las entradas
entries = TelemetryReader.read_entries()

# Leer desde hace 7 días
since = datetime.now() - timedelta(days=7)
entries = TelemetryReader.read_entries(since=since)

# Leer solo un tipo
entries = TelemetryReader.read_entries(
    entry_type="reliability.plan_generation"
)

# Obtener resumen
summary = TelemetryReader.get_summary(days=7)

# Obtener timeline de seguridad
timeline = TelemetryReader.get_security_timeline(days=7)
```

---

## 🔧 Dimensiones

Cada entrada de telemetría incluye:

```json
{
  "dimensions": {
    "branch_name": "master",
    "model_id": "gemini-2.5-pro",
    "hostname": "MI-PC"
  }
}
```

Esto permite filtrar y agrupar métricas por:
- Branch de Git
- Modelo de IA utilizado
- Máquina/hostname
