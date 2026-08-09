# 04. Referencia de Scripts

## 📂 Ubicación: `scripts/`

---

## common.py

**Propósito**: Módulo de utilidades compartidas y configuración de encoding.

**Exporta:**
- `Colors`: Códigos ANSI para colores en terminal
- `Symbols`: Caracteres ASCII-safe para compatibilidad Windows
- `log_pass()`, `log_fail()`, `log_warn()`, `log_info()`: Funciones de logging
- `make_header()`: Genera headers formateados
- `safe_print()`: Print con manejo de encoding

**Uso:**
```python
from common import Colors, Symbols, log_pass, log_fail

log_pass("Operación exitosa")
log_fail("Error en el proceso")
```

---

## rag_indexer.py (v2.0)

**Propósito**: Indexador de codebase para búsqueda semántica.

**Características:**
- Indexación incremental via git diff + hashes
- Detección automática de lenguajes
- Cache de estado en `.rag_index_state.json`

**Uso:**
```powershell
# Indexación completa
python scripts/rag_indexer.py

# Indexación incremental (solo cambios)
python scripts/rag_indexer.py --incremental

# Ver estado del índice
python scripts/rag_indexer.py --status
```

**Archivos generados:**
- `.rag_index_state.json`: Estado del índice
- `.rag_file_hashes.json`: Hashes MD5 de archivos

---

## plan_generator.py (v2.1)

**Propósito**: Genera planes JSON con Self-Correction Loop.

**Características:**
- Self-Correction: 3 reintentos automáticos
- Semantic Verification: Valida que paths existan
- Anti-alucinación: Rechaza paths inexistentes

**Uso:**
```powershell
# Básico
python scripts/plan_generator.py --objective "Mi tarea"

# Con archivos específicos
python scripts/plan_generator.py --objective "Refactorizar" --files "file1.py,file2.py"

# Con contexto adicional
python scripts/plan_generator.py --objective "Debuggear" --context "Error en línea 42"
```

**Output:**
- Plan JSON en `plans/PLAN-XXXXXXXX.json`

---

## validate_plan.py

**Propósito**: Valida planes JSON contra schema AGCCE_Plan_v1.

**Uso:**
```powershell
python scripts/validate_plan.py plans/PLAN-XXX.json
```

**Validaciones:**
- Schema JSON válido
- Campos requeridos presentes
- Tipos de datos correctos
- IDs de pasos únicos

---

## orchestrator.py

**Propósito**: Orquesta la ejecución completa de un plan.

**Fases:**
1. Pre-flight Check (git, lint, types)
2. HITL Gate (aprobación humana)
3. Ejecución de pasos
4. Evidence Collection

**Uso:**
```powershell
python scripts/orchestrator.py plans/PLAN-XXX.json
```

---

## hitl_gate.py

**Propósito**: Human-in-the-Loop Gate para aprobaciones.

**Uso:**
```powershell
python scripts/hitl_gate.py plans/PLAN-XXX.json
```

**Opciones:**
- `a`: Aprobar todo el plan
- `s`: Aprobar paso por paso
- `r`: Rechazar plan
- `v`: Ver detalles del paso

---

## collect_evidence.py

**Propósito**: Recolecta evidencia de ejecución.

**Uso:**
```powershell
python scripts/collect_evidence.py plans/PLAN-XXX.json
```

**Output:**
- Evidence JSON con logs, timestamps y resultados

---

## pre_commit_hook.py (v2.1)

**Propósito**: Hook de pre-commit con validaciones de seguridad.

**Checks:**
1. Lint Check (archivos Python staged)
2. Snyk Code Scan
3. Snyk-Diff Policy (dependencias)

**Instalación:**
```powershell
python scripts/pre_commit_hook.py --install
```

**Desinstalación:**
```powershell
python scripts/pre_commit_hook.py --uninstall
```

**Comportamiento:**
- Bloquea commits con vulnerabilidades Critical/High
- Analiza delta en requirements.txt/package.json

---

## metrics_collector.py (AGCCE-OBS-V1)

**Propósito**: Colector de métricas para observabilidad.

**Telemetry Contract:** AGCCE-OBS-V1

**Uso CLI:**
```powershell
# Resumen de 7 días
python scripts/metrics_collector.py summary 7

# Timeline de seguridad
python scripts/metrics_collector.py timeline 7

# Limpiar logs antiguos
python scripts/metrics_collector.py cleanup
```

**Uso Programático:**
```python
from metrics_collector import Telemetry

Telemetry.record_plan_generated(success=True, attempts=1, latency_ms=150)
Telemetry.record_snyk_scan(scan_type="code", vulnerabilities_found=0)
```

**Archivos:**
- `logs/telemetry.jsonl`: Métricas generales
- `logs/security_events.jsonl`: Eventos de seguridad

---

## dashboard_server.py

**Propósito**: Servidor HTTP para el dashboard de métricas.

**Uso:**
```powershell
# Puerto por defecto (8080)
python scripts/dashboard_server.py

# Puerto personalizado
python scripts/dashboard_server.py --port 8888

# Solo generar datos (sin servidor)
python scripts/dashboard_server.py --generate-only
```

**URL:** `http://localhost:<puerto>/dashboard/index.html`

---

## event_dispatcher.py (v2.0 FINAL)

**Propósito**: Dispatcher de eventos para n8n con Webhook-First pattern.

**Características:**
- Healthcheck Handshake
- Retry con Backoff (1s, 5s, 15s)
- System Context en payloads
- Cola local para resiliencia

**Uso CLI:**
```powershell
# Ver estado de webhooks
python scripts/event_dispatcher.py status

# Verificar n8n disponible
python scripts/event_dispatcher.py healthcheck

# Configurar webhooks
python scripts/event_dispatcher.py configure

# Enviar evento de prueba
python scripts/event_dispatcher.py test PLAN_VALIDATED

# Procesar cola local
python scripts/event_dispatcher.py process-queue
```

**Uso Programático:**
```python
from event_dispatcher import EventDispatcher

EventDispatcher.healthcheck()
EventDispatcher.emit_plan_validated("PLAN-XXX", plan_data)
EventDispatcher.emit_evidence_ready("PLAN-XXX", "/path/to/evidence", summary)
```

**Eventos Soportados:**
- `PLAN_VALIDATED`
- `EXECUTION_ERROR`
- `EVIDENCE_READY`
- `SECURITY_BREACH_ATTEMPT`
- `HIGH_LATENCY_THRESHOLD`
- `HITL_TIMEOUT`
- `HEARTBEAT`

---

## doc_fetcher.py

**Propósito**: Obtiene documentación de librerías via MCP context7.

**Uso:**
```powershell
python scripts/doc_fetcher.py --library "fastapi" --query "authentication"
```

**Cache:** `.doc_cache.json`

---

## lint_check.py

**Propósito**: Ejecuta linting en archivos Python.

**Uso:**
```powershell
python scripts/lint_check.py file1.py file2.py
```

---

## type_check.py

**Propósito**: Ejecuta verificación de tipos.

**Uso:**
```powershell
python scripts/type_check.py file1.py file2.py
```
