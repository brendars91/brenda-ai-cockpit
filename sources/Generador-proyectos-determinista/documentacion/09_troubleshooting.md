# 09. Troubleshooting

## 🔧 Problemas Comunes y Soluciones

---

## Encoding / Caracteres

### Problema: Caracteres extraños en la terminal

**Síntomas:**
```
[OK] Operaci├│n exitosa
════════════
```

**Causa:** La terminal no soporta UTF-8 correctamente.

**Solución:**
```powershell
# Configurar PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
```

O agregar a tu perfil de PowerShell (`$PROFILE`):
```powershell
chcp 65001
```

---

## Git

### Problema: Hook de pre-commit no ejecuta

**Causa:** Hook no tiene permisos o no está instalado.

**Solución:**
```powershell
# Reinstalar hook
python scripts/pre_commit_hook.py --install

# Verificar que existe
Get-Content .git/hooks/pre-commit
```

### Problema: Commit bloqueado por Snyk

**Mensaje:**
```
[X] SNYK CHECK FAILED
Vulnerabilities found: 3 Critical, 5 High
```

**Solución:**
1. Ver detalles:
   ```powershell
   snyk code test
   ```
2. Corregir las vulnerabilidades en el código
3. Reintentar commit

**NOTA:** NO usar `--no-verify`, está PROHIBIDO.

---

## RAG Indexer

### Problema: Indexación muy lenta

**Causa:** Indexación completa en proyecto grande.

**Solución:**
```powershell
# Usar modo incremental
python scripts/rag_indexer.py --incremental
```

### Problema: Archivos no aparecen en índice

**Causa:** Archivos ignorados por .gitignore.

**Solución:** El indexador respeta .gitignore. Si necesitas incluir archivos ignorados, modifica las exclusiones.

---

## Plan Generator

### Problema: Plan rechazado por paths inexistentes

**Mensaje:**
```
[X] Semantic Verification Failed
Path 'src/fake.py' no existe
```

**Causa:** El path referenciado no existe en el filesystem ni en el índice RAG.

**Solución:**
1. Verificar que el path es correcto
2. Re-indexar el codebase:
   ```powershell
   python scripts/rag_indexer.py
   ```
3. Regenerar el plan

### Problema: Máximo de reintentos alcanzado

**Mensaje:**
```
[X] Max retries reached (3/3)
Requiere intervencion humana
```

**Solución:**
1. Revisar el objetivo del plan
2. Hacer el objetivo más específico
3. Especificar archivos manualmente:
   ```powershell
   python scripts/plan_generator.py --objective "Mi tarea" --files "file1.py,file2.py"
   ```

---

## n8n / Event Dispatcher

### Problema: Healthcheck falla

**Mensaje:**
```
[!] ADVERTENCIA: n8n no disponible
```

**Posibles causas:**
1. n8n no está corriendo
2. URL de webhook incorrecta
3. Firewall bloqueando conexión

**Solución:**
1. Verificar que n8n está activo
2. Verificar URLs en `config/n8n_webhooks.json`
3. Probar conexión manualmente:
   ```powershell
   Invoke-WebRequest -Uri "https://tu-n8n.com/webhook/test" -Method POST
   ```

### Problema: Eventos no llegan a n8n

**Posibles causas:**
1. Webhook no configurado
2. Evento duplicado (idempotencia)
3. Error de conexión (guardado en cola)

**Solución:**
1. Verificar configuración:
   ```powershell
   python scripts/event_dispatcher.py status
   ```
2. Procesar cola:
   ```powershell
   python scripts/event_dispatcher.py process-queue
   ```
3. Forzar envío:
   ```powershell
   python scripts/event_dispatcher.py test PLAN_VALIDATED
   ```

---

## Dashboard

### Problema: Dashboard no carga

**Causa:** Puerto ocupado.

**Solución:**
```powershell
# Usar otro puerto
python scripts/dashboard_server.py --port 9000
```

### Problema: Métricas vacías

**Causa:** No hay datos en telemetry.jsonl.

**Solución:**
1. Ejecutar algunas operaciones:
   ```powershell
   python scripts/plan_generator.py --objective "Test"
   ```
2. Regenerar datos del dashboard:
   ```powershell
   python scripts/dashboard_server.py --generate-only
   ```

---

## Snyk

### Problema: Snyk no encontrado

**Mensaje:**
```
[X] Snyk CLI not found
```

**Solución:**
1. Instalar Snyk:
   ```powershell
   npm install -g snyk
   ```
2. Autenticar:
   ```powershell
   snyk auth
   ```

### Problema: Snyk timeout

**Causa:** Proyecto muy grande o conexión lenta.

**Solución:**
1. Escanear solo archivos staged:
   ```powershell
   snyk code test --file=archivo.py
   ```
2. Verificar conexión a internet

---

## Orquestador

### Problema: Pre-flight check falla

**Mensaje:**
```
[X] PRE-FLIGHT CHECK FAILED
Git working directory not clean
```

**Solución:**
1. Ver cambios pendientes:
   ```powershell
   git status
   ```
2. Commit o stash los cambios:
   ```powershell
   git stash
   # o
   git add -A && git commit -m "WIP"
   ```

### Problema: HITL timeout

**Mensaje:**
```
[!] HITL timeout after 5 minutes
```

**Solución:** El sistema espera aprobación humana. Responde con 'a' para aprobar o 'r' para rechazar.

---

## Logs

### Problema: Logs muy grandes

**Solución:**
```powershell
# Limpiar logs antiguos (> 30 días)
python scripts/metrics_collector.py cleanup
```

### Problema: Log corrupto

**Síntoma:** Error al leer JSONL

**Solución:**
1. Backup del log:
   ```powershell
   Copy-Item logs/telemetry.jsonl logs/telemetry.backup.jsonl
   ```
2. Limpiar líneas corruptas manualmente o eliminar el archivo

---

## Contacto y Soporte

Para problemas no documentados:
1. Revisar logs en `logs/`
2. Activar modo verbose (si disponible)
3. Crear issue con:
   - Descripción del problema
   - Mensaje de error completo
   - Pasos para reproducir
   - Versión del bundle (`config/bundle.json`)
