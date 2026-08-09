# 03. Guía de Uso

## 🔄 Flujo de Trabajo Típico

### Paso 1: Indexar el Codebase

Antes de comenzar cualquier tarea, asegúrate de que el índice RAG esté actualizado:

```powershell
# Primera vez (indexación completa)
python scripts/rag_indexer.py

# Actualizaciones posteriores (incremental)
python scripts/rag_indexer.py --incremental
```

**¿Qué hace?**
- Escanea todos los archivos del proyecto
- Genera metadatos para búsqueda semántica
- En modo incremental, solo re-indexa archivos modificados

---

### Paso 2: Generar un Plan

Cuando tengas una tarea clara:

```powershell
python scripts/plan_generator.py --objective "Implementar validación de inputs en el módulo auth"
```

**Opciones adicionales:**
```powershell
# Especificar archivos objetivo
python scripts/plan_generator.py --objective "Refactorizar" --files "scripts/common.py,scripts/utils.py"

# Con contexto adicional
python scripts/plan_generator.py --objective "Optimizar consultas" --context "La base de datos es PostgreSQL"
```

**¿Qué hace?**
1. Genera un plan JSON estructurado
2. Valida que los paths referenciados existan (anti-alucinación)
3. Si falla la validación, reintenta hasta 3 veces
4. Guarda el plan en `plans/PLAN-XXXXXXXX.json`

---

### Paso 3: Revisar el Plan

Abre el plan generado y revisa:

```powershell
# Ver el plan
Get-Content plans/PLAN-XXXXXXXX.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

O validar formalmente:

```powershell
python scripts/validate_plan.py plans/PLAN-XXXXXXXX.json
```

---

### Paso 4: Ejecutar el Plan (Opcional)

Si deseas ejecutar el plan completo con el orquestador:

```powershell
python scripts/orchestrator.py plans/PLAN-XXXXXXXX.json
```

**El orquestador:**
1. Ejecuta Pre-flight Check (git status, lint, types)
2. Solicita aprobación humana (HITL Gate)
3. Ejecuta cada paso del plan
4. Recolecta evidencia

---

### Paso 5: Commit de Cambios

Al hacer commit, el hook de pre-commit verificará automáticamente:

```powershell
git add -A
git commit -m "feat: implement input validation"
```

**Si hay vulnerabilidades:**
- El commit será bloqueado
- Verás el detalle de las vulnerabilidades
- Debes corregir antes de poder hacer commit

---

## 📊 Monitoreo

### Ver Métricas

```powershell
# Resumen de 7 días
python scripts/metrics_collector.py summary 7

# Timeline de seguridad
python scripts/metrics_collector.py timeline 7
```

### Dashboard Visual

```powershell
python scripts/dashboard_server.py --port 8888
# Abrir: http://localhost:8888
```

---

## 🔔 Notificaciones

### Verificar n8n

```powershell
python scripts/event_dispatcher.py healthcheck
```

### Procesar Cola Local

Si hubo fallos de conexión, los eventos se guardan localmente:

```powershell
python scripts/event_dispatcher.py process-queue
```

---

## 🛠️ Workflows Disponibles

Puedes usar comandos de workflow desde el chat del agente:

| Comando | Descripción |
|---------|-------------|
| `/auto-plan` | Genera plan JSON automáticamente |
| `/rag-index` | Indexa el codebase |
| `/ci-cd-hooks` | Configura hooks de CI/CD |
| `/pre-flight-check` | Verifica estado antes de cambios |
| `/git-protocol` | Protocolo de versionado Git |
| `/docker-executor` | Ejecutar comandos Docker |
| `/plan-json-emit` | Emitir plan JSON estructurado |

---

## 📝 Ejemplos Prácticos

### Ejemplo 1: Añadir Nuevo Endpoint API

```powershell
# 1. Indexar
python scripts/rag_indexer.py --incremental

# 2. Generar plan
python scripts/plan_generator.py --objective "Añadir endpoint GET /api/users/{id}" --files "api/routes.py,api/controllers.py"

# 3. Revisar plan
python scripts/validate_plan.py plans/PLAN-XXX.json

# 4. Implementar cambios manualmente siguiendo el plan

# 5. Commit
git add -A
git commit -m "feat(api): add GET /api/users/:id endpoint"
```

### Ejemplo 2: Corregir Bug

```powershell
# 1. Generar plan de debugging
python scripts/plan_generator.py --objective "Corregir error 500 en login" --context "El error ocurre cuando el email tiene caracteres especiales"

# 2. Ver el plan generado
type plans\PLAN-XXX.json

# 3. Seguir los pasos del plan para debuggear
```

### Ejemplo 3: Refactorización

```powershell
# 1. Indexar para tener contexto completo
python scripts/rag_indexer.py

# 2. Generar plan de refactorización
python scripts/plan_generator.py --objective "Refactorizar scripts/common.py para separar logging de utilidades"

# 3. Ejecutar con orquestador (opcional)
python scripts/orchestrator.py plans/PLAN-XXX.json
```

---

## ⚠️ Consideraciones Importantes

### 1. No Saltear Snyk
```
PROHIBIDO: git commit --no-verify
```
El bypass de Snyk está prohibido por las directivas de AGCCE.

### 2. Siempre Indexar Antes de Planificar
El plan generator depende del índice RAG para validar paths.

### 3. Revisar Plans Antes de Ejecutar
Aunque hay self-correction, siempre revisa los planes generados.

### 4. Mantener Dashboard Activo
El dashboard te da visibilidad del estado del sistema.
