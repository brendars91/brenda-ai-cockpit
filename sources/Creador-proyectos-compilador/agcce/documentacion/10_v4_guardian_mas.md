# 10. AGCCE v4.0 - Security Guardian y Multi-Agent System

> Documentación de las nuevas características de AGCCE v4.0 GUARDIAN MAS

---

## 🛡️ Security Guardian (Red Team)

### ¿Qué es?

Un sistema de seguridad **proactivo** que detecta vulnerabilidades lógicas que las herramientas estáticas (como Snyk) no pueden ver.

### Vulnerabilidades Detectadas

| Tipo | Descripción |
|------|-------------|
| **IDOR** | Acceso a recursos de otros usuarios cambiando IDs |
| **Race Condition** | Condiciones de carrera en operaciones concurrentes |
| **Auth Bypass** | Bypass de autenticación/autorización |
| **Logic Flaw** | Fallos en lógica de negocio |
| **Data Exposure** | Filtración de datos sensibles en logs/respuestas |
| **SSRF** | Server-Side Request Forgery |

### Uso

```powershell
# Analizar un archivo
python scripts/security_guardian.py analyze path/to/file.py

# Analizar directorio completo
python scripts/security_guardian.py analyze scripts/

# Ver estadísticas
python scripts/security_guardian.py stats
```

### Protocolo Red-to-Green

1. **Hipótesis de Ataque**: "¿Cómo podría un atacante explotar esto?"
2. **PoC Test**: Escribir test que demuestre la vulnerabilidad
3. **Fix**: Implementar la corrección
4. **Verify**: Ejecutar test para confirmar que ya no es explotable

### Integración con Plan JSON

```json
{
  "security_analysis": {
    "assumptions": ["Usuario autenticado antes de llegar aquí"],
    "attack_vectors": [{"type": "IDOR", "likelihood": "high"}],
    "mitigations": ["Verificar ownership en cada endpoint"],
    "validation_tests": ["tests/security/test_idor.py"]
  }
}
```

---

## 🤖 Multi-Agent System (MAS)

### Arquitectura

```
Researcher → Architect → Constructor → Auditor → Tester
```

### Agentes Disponibles

| Agente | Rol | MCPs Permitidos |
|--------|-----|-----------------|
| **Researcher** | Buscar contexto en codebase | smart-coding-mcp, context7, fetch |
| **Architect** | Diseñar solución, crear plan | sequential-thinking, context7 |
| **Constructor** | Escribir código | filesystem, smart-coding-mcp |
| **Auditor** | Revisar seguridad | snyk, filesystem |
| **Tester** | Verificar calidad | filesystem |

### Perfiles de Agente

Los perfiles están en `config/agent_profiles/`:
- `architect.json`
- `constructor.json`
- `auditor.json`
- `tester.json`
- `researcher.json`

Cada perfil define:
- System prompt específico del rol
- MCPs permitidos y prohibidos
- Responsabilidades
- Checks de calidad
- A quién entrega el trabajo (handoff)

### Uso

```powershell
# Ver todos los perfiles
python scripts/agent_switcher.py list

# Ver flujo de trabajo
python scripts/agent_switcher.py workflow

# Ver detalles de un agente
python scripts/agent_switcher.py show architect

# Activar un agente
python scripts/agent_switcher.py activate constructor
```

---

## 📋 Blackboard (Estado Compartido)

### ¿Qué es?

Un sistema de estado compartido que permite a los agentes:
- Leer el estado global del proyecto
- Escribir resultados de su fase
- Mantener historial de cambios

### Archivo de Estado

`logs/current_state.json`

### Uso

```powershell
# Ver estado actual
python scripts/blackboard.py status

# Obtener un valor
python scripts/blackboard.py get current_phase

# Establecer un valor
python scripts/blackboard.py set current_phase implementation

# Ver historial de cambios
python scripts/blackboard.py history 20

# Limpiar estado
python scripts/blackboard.py clear
```

### Campos del Estado

| Campo | Descripción |
|-------|-------------|
| `current_phase` | Fase actual (planning, implementation, etc.) |
| `current_agent` | Agente activo |
| `current_plan_id` | ID del plan en ejecución |
| `current_step` | Paso actual del plan |
| `context` | Contexto compartido |
| `results` | Resultados de cada fase |
| `errors` | Errores registrados |

---

## 🧪 Tests Automatizados

### Estructura

```
tests/
├── __init__.py
├── conftest.py          # Fixtures compartidos
├── test_skill_loader.py
├── test_task_queue.py
├── test_smart_search.py
└── test_security_guardian.py
```

### Ejecutar Tests

```powershell
# Instalar pytest
pip install pytest

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar un archivo específico
pytest tests/test_security_guardian.py -v

# Ver cobertura (requiere pytest-cov)
pip install pytest-cov
pytest tests/ --cov=scripts --cov-report=html
```

### Tests Incluidos

| Archivo | Tests | Cobertura |
|---------|-------|-----------|
| `test_skill_loader.py` | 9 | SkillLoader, fases, MCPs |
| `test_task_queue.py` | 10 | Cola de tareas, prioridades |
| `test_smart_search.py` | 6 | Búsqueda semántica, refinamiento |
| `test_security_guardian.py` | 10 | Detección de vulnerabilidades |

---

## 📊 Nuevas Métricas (Dashboard)

La v4.0 añade la métrica de **Vulnerabilidades Lógicas Detectadas**:
- Diferencia entre lo que Snyk encuentra y lo que Security Guardian detecta
- Permite medir la efectividad del razonamiento de seguridad

---

## 🔄 Resumen de Cambios v4.0

| Feature | Archivos Añadidos |
|---------|-------------------|
| Security Guardian | `scripts/security_guardian.py`, `.agent/skills/security-red-team/SKILL.md` |
| Tests Automatizados | `tests/*` (6 archivos) |
| Multi-Agent System | `config/agent_profiles/*` (5 archivos), `scripts/agent_switcher.py` |
| Blackboard | `scripts/blackboard.py` |
