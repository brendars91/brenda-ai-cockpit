# 📋 Catálogo Completo de Comandos - Ejecución Automática

Este documento lista **TODOS** los comandos disponibles en el ecosistema. Antigravity los ejecuta automáticamente según el contexto.

**TÚ NO NECESITAS RECORDAR NINGUNO** - Solo habla en lenguaje natural.

---

## 🎯 Cómo Funciona

Cuando trabajas en un proyecto, yo:
1. **Detecto el contexto** (qué estás haciendo)
2. **Identifico comandos relevantes** de esta lista
3. **Los ejecuto automáticamente** o te sugiero ejecutarlos
4. **Te muestro el resultado**

---

## 📦 COMANDOS DE GEM BUILDER

### 🔷 Compilación de Gems

```powershell
# Compilar un Use Case Spec en Gem Bundle
python src/cli.py compile --spec specs/mi_spec.json --output bundles/

# Compilar con opciones avanzadas
python src/cli.py compile \
  --spec specs/mi_spec.json \
  --risk-score 75 \
  --model gemini-3-pro \
  --output bundles/mi_gem_v1.0.0.json
```

**Cuándo lo ejecuto**:
- Cuando dices "compila un agente que..."
- Cuando creas un Use Case Spec
- Cuando quieres generar un Gem Bundle

---

### 🔷 Validación

```powershell
# Validar Use Case Spec
python src/validator.py specs/mi_spec.json --type use_case_spec

# Validar Gem Bundle compilado
python src/validator.py bundles/mi_gem.json --type gem_bundle

# Validar contra schema
python src/validator.py bundles/mi_gem.json --schema schemas/gem_bundle.v1.schema.json
```

**Cuándo lo ejecuto**:
- Después de compilar un Gem (automático)
- Cuando copias un Gem de otra fuente
- Cuando modificas manualmente un Gem

---

### 🔷 Gestión de Gems

```powershell
# Listar Gems compilados
Get-ChildItem bundles/ -Filter "*.json" | ForEach-Object {
    $content = Get-Content $_.FullName | ConvertFrom-Json
    Write-Host "$($_.Name) - v$($content.bundle_meta.version) - Risk: $($content.bundle_meta.risk_score)"
}

# Copiar Gem a AGCCE
Copy-Item "bundles/mi_gem_v1.0.0.json" "../Agente Copilot Engine/gems/"

# Ver detalles de un Gem
Get-Content "bundles/mi_gem_v1.0.0.json" | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

**Cuándo lo ejecuto**:
- Cuando preguntas "qué Gems tengo?"
- Después de compilar (te pregunto si copiar a AGCCE)
- Cuando quieres ver detalles de un Gem

---

## 🤖 COMANDOS DE AGCCE v4.0

### 🔷 Gestión de Gems

```powershell
# Listar Gems disponibles
python scripts/gem_registry.py list

# Ver estadísticas de uso
python scripts/gem_registry.py stats

# Ver info de un Gem específico
python scripts/gem_registry.py show <use_case_id>

# Verificar integridad de Gem
python scripts/gem_loader.py gems/mi_gem_v1.0.0.json
```

**Cuándo lo ejecuto**:
- Cuando preguntas "qué Gems tengo?"
- Cuando mencionas usar un Gem
- Periódicamente para mostrarte Gems populares

---

### 🔷 Generación de GemPlans

```powershell
# Modo interactivo (wizard)
python scripts/gem_plan_generator.py --interactive

# Modo directo
python scripts/gem_plan_generator.py \
  --gem gems/api_auditor_v1.0.0.json \
  --goal "Auditar API REST" \
  --output plans/api_audit_gemplan.json

# Con tareas personalizadas desde JSON
python scripts/gem_plan_generator.py \
  --gem gems/mi_gem.json \
  --goal "..." \
  --tasks-json custom_tasks.json
```

**Cuándo lo ejecuto**:
- Cuando dices "usa el gem X para..."
- Cuando quieres ejecutar con un Gem específico
- Ofrezco modo interactivo vs directo

---

### 🔷 Ejecución de Planes

```powershell
# Ejecutar GemPlan
python scripts/orchestrator.py plans/mi_gemplan.json

# Ejecutar Plan AGCCE normal
python scripts/orchestrator.py plans/mi_plan.json

# Dry-run (sin escribir archivos)
python scripts/orchestrator.py plans/mi_plan.json --dry-run
```

**Cuándo lo ejecuto**:
- Después de generar un GemPlan
- Cuando dices "ejecuta el plan..."
- Automáticamente si ya confirmaste todo

---

### 🔷 CLI Interactivo

```powershell
# Abrir CLI con menú
python scripts/agcce_cli.py

# Opciones directas sin menú
python scripts/agcce_cli.py --indexar
python scripts/agcce_cli.py --generar-plan
python scripts/agcce_cli.py --generar-gemplan
python scripts/agcce_cli.py --ejecutar-plan <plan.json>
python scripts/agcce_cli.py --metricas
```

**Cuándo lo ejecuto**:
- Si prefieres interfaz visual
- Para explorar opciones disponibles
- Raramente (prefiero ejecutar directamente)

---

### 🔷 RAG & Indexación

```powershell
# Indexar codebase completo
python scripts/rag_indexer.py

# Indexación incremental (solo cambios)
python scripts/rag_indexer.py --incremental

# Indexar directorio específico
python scripts/rag_indexer.py --path src/

# Búsqueda semántica
python scripts/rag_search.py "cómo se autentica el usuario"
```

**Cuándo lo ejecuto**:
- Al inicio de un proyecto nuevo
- Después de cambios grandes
- Cuando necesito contexto del codebase
- Para búsquedas semánticas

---

### 🔷 Security & Auditoría

```powershell
# Security Guardian (Red Team)
python scripts/security_guardian.py analyze <path>

# Escaneo Snyk Code
snyk code test

# Escaneo de secretos
python scripts/secrets_detector.py .
python scripts/secrets_detector.py --scan-staged

# Audit Trail
python scripts/audit_trail.py verify
python scripts/audit_trail.py show 7
python scripts/audit_trail.py export audit_export.json
```

**Cuándo lo ejecuto**:
- Antes de cada commit (automático con pre-commit hook)
- Cuando implementas código sensible
- Cuando pides "escanea seguridad"
- Periódicamente para prevención

---

### 🔷 Dashboard & Métricas

```powershell
# Iniciar dashboard web
python scripts/dashboard_server.py --port 8888

# Ver métricas en consola (7 días)
python scripts/metrics_collector.py summary 7

# Ver métricas (30 días)
python scripts/metrics_collector.py summary 30

# Timeline de seguridad
python scripts/metrics_collector.py timeline 7

# Generar reporte
python scripts/metrics_collector.py report --output reports/metrics_$(Get-Date -Format 'yyyyMMdd').html
```

**Cuándo lo ejecuto**:
- Cuando pides "muestra métricas"
- Cuando quieres ver Gems activos
- Para revisiones semanales/mensuales
- Cuando hay eventos de seguridad

---

### 🔷 Testing

```powershell
# Ejecutar todos los tests
pytest

# Tests con coverage
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/test_gem_loader.py
pytest -k "test_load_gem"

# Tests end-to-end
pytest tests/e2e/

# Tests en modo watch
pytest-watch
```

**Cuándo lo ejecuto**:
- Después de implementar código
- Antes de commit (automático)
- Cuando pides "crea tests"
- Para validar cambios

---

### 🔷 Git & Version Control

```powershell
# Pre-flight check
python scripts/pre_flight_check.py

# Pre-commit hook (automático)
python scripts/pre_commit_hook.py

# Ver cambios pendientes
git status --porcelain

# Commit con validación
git add .
python scripts/pre_commit_hook.py && git commit -m "mensaje"

# Ver historial de cambios
git log --oneline --graph --all
```

**Cuándo lo ejecuto**:
- Antes de hacer commit
- Cuando pides "commitea los cambios"
- Para validar estado del repo
- Automático en workflow

---

### 🔷 Deployment & CI/CD

```powershell
# Build para producción
npm run build  # Frontend
python -m build  # Python package

# Docker build
docker build -t mi-proyecto:latest .
docker-compose up -d

# Despliegue
python scripts/deploy.py --env staging
python scripts/deploy.py --env production

# Rollback
python scripts/deploy.py --rollback --env production
``

**Cuándo lo ejecuto**:
- Cuando pides "despliega a..."
- Después de tests exitosos
- Cuando hay tag de versión
- Nunca a producción sin confirmación

---

### 🔷 Utilities & Helpers

```powershell
# Linting
python scripts/lint_check.py <path>
ruff check .  # Python
eslint src/  # JavaScript

# Formatting
black .  # Python
prettier --write src/  # JavaScript

# Cleanup
python scripts/cleanup.py --remove-temp
python scripts/cleanup.py --remove-cache

# Backup
python scripts/backup.py --target plans/
```

**Cuándo lo ejecuto**:
- Antes de commit (linting automático)
- Cuando código tiene warnings
- Para mantener proyecto limpio
- Periódicamente para backups

---

## 🔄 Workflows Automatizados

### Workflow 1: Compilar y Usar Gem

```powershell
# 1. En Gem Builder
python src/cli.py compile --spec specs/mi_spec.json

# 2. Copiar a AGCCE
Copy-Item "bundles/mi_gem_v1.0.0.json" "../Agente Copilot Engine/gems/"

# 3. En AGCCE
cd "../Agente Copilot Engine"
python scripts/gem_plan_generator.py --interactive

# 4. Ejecutar
python scripts/orchestrator.py plans/mi_gemplan.json
```

**Cuándo lo ejecuto**: Cuando dices "compila un agente y úsalo"

---

### Workflow 2: Desarrollo Completo con Validación

```powershell
# 1. Indexar codebase
python scripts/rag_indexer.py

# 2. Generar plan
python scripts/plan_generator.py --objective "..."

# 3. Ejecutar con validaciones
python scripts/orchestrator.py plans/mi_plan.json

# 4. Tests automáticos
pytest --cov

# 5. Security scan
python scripts/security_guardian.py analyze .
snyk code test

# 6. Commit
git add .
python scripts/pre_commit_hook.py
git commit -m "feat: ..."
```

**Cuándo lo ejecuto**: Cuando implementas un feature completo

---

### Workflow 3: Revisión de Proyecto

```powershell
# 1. Métricas generales
python scripts/metrics_collector.py summary 30

# 2. Estado de Gems
python scripts/gem_registry.py stats

# 3. Security timeline
python scripts/metrics_collector.py timeline 7

# 4. Audit trail
python scripts/audit_trail.py verify

# 5. Dashboard visual
python scripts/dashboard_server.py --port 8888
```

**Cuándo lo ejecuto**: Cuando pides "muestra el estado del proyecto"

---

## 💡 Comandos que NUNCA Necesitas Recordar

Yo los ejecuto automáticamente según contexto:

| Contexto | Comando Ejecutado | Sin que lo pidas |
|----------|-------------------|------------------|
| "Compila un agente..." | `python src/cli.py compile` | ✅ Automático |
| "Usa el gem X..." | `gem_plan_generator.py --interactive` | ✅ Automático |
| Implementas código | `security_guardian.py`, `pytest` | ✅ Automático |
| Haces commit | `pre_commit_hook.py`, `snyk code test` | ✅ Automático |
| "Qué Gems tengo?" | `gem_registry.py list` | ✅ Automático |
| "Muestra métricas" | `metrics_collector.py summary` | ✅ Automático |
| Código complejo sin docs | Genero docstrings | ✅ Sugerido |
| UI sin accessibility | `accessibility` skill | ✅ Sugerido |

---

## 🎯 Categorías de Ejecución

### **Ejecución Silenciosa** (sin preguntar):
- Validaciones de schema
- Lint checks
- Git status
- Registry stats
- RAG search

### **Ejecución con Confirmación** (te pregunto):
- Compilar Gems
- Ejecutar planes
- Security scans (si encuentran issues)
- Commits
- Deployments

### **Sugerencia Proactiva** (te ofrezco):
- Tests cuando falta coverage
- Accessibility cuando creas UI
- Performance optimization
- Documentation
- Skills relevantes

---

**Versión**: 1.0  
**Comandos totales**: 50+  
**Última actualización**: 2026-01-19

**Tu trabajo**: Hablar en lenguaje natural  
**Mi trabajo**: Ejecutar el comando correcto en el momento correcto 🚀
