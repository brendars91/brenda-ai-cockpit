# Directivas de Refinamiento AGCCE v1.1.0

> **Prioridad**: CRÍTICA  
> **Fase**: Configuración Inicial  
> **Estado**: ACTIVO

## 1. Acoplamiento Determinista Docker-Plan

Antes de ejecutar cualquier script en `./scripts/*.ps1` relacionado con Docker:

```
VALIDACIÓN OBLIGATORIA:
├── Verificar que el `id` del paso (S01, S02...) exista en AGCCE_Plan_v1
├── El mapeo debe ser explícito en el JSON de planificación
└── PROHIBIDO: Ejecuciones de infraestructura sin mapeo
```

### Ejemplo de Mapeo Válido:
```json
{
  "step_id": "S01",
  "action": "docker_compose_up",
  "script": "scripts/docker_compose_up.ps1",
  "expected_outcome": "Services running"
}
```

---

## 2. Gestión de Recursos Snyk (Efficiency)

Las herramientas del MCP de Snyk quedan **restringidas exclusivamente** a:

| Fase | Permitido | Descripción |
|------|-----------|-------------|
| Pre-flight Check | ✅ | Antes de proponer un patch |
| Verification Report | ✅ | Después de una implementación |
| Thinking | ❌ | PROHIBIDO |
| Drafting | ❌ | PROHIBIDO |

**Razón**: Optimizar uso de tokens y reducir latencia.

---

## 3. Protocolo de Versionado Local (Git)

Ante la ausencia de MCP de GitHub, AGCCE asume control total de `git` via comandos de terminal.

### Pre-Requisito (Antes de emitir plan-json):
```bash
git status
```
- Si hay cambios no trackeados que interfieran con la tarea → Notificar usuario
- Proponer solución antes de continuar

### Post-Requisito (Al completar tarea exitosa):
```bash
git add <archivos_modificados>
git commit -m "<tipo>: <descripción>"
```

**Formato de Commits**: [Conventional Commits](https://www.conventionalcommits.org/)
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Documentación
- `refactor:` - Refactorización sin cambio funcional
- `test:` - Añadir/modificar tests
- `chore:` - Mantenimiento

---

## 4. Validación Automática de Evidencias

El script `scripts/validate_plan.py` actúa como **gate automático**:

```
FLUJO DE VALIDACIÓN:
├── 1. Generar Plan JSON
├── 2. Ejecutar validate_plan.py
├── 3. Si PASS → Continuar ejecución
└── 4. Si FAIL → Regenerar Plan JSON (sin intervención del usuario)
```

### Criterios de Validación:
1. Schema JSON válido según `AGCCE_Plan_v1.schema.json`
2. Todos los IDs de pasos son únicos
3. Cada acción tiene un script o comando asociado
4. No hay dependencias circulares

---

## Activación

Esta directiva está **ACTIVA** desde: 2026-01-16

Para verificar estado operativo:
```
Estado: AGCCE v1.1.0-OPTIMIZED ✅
```
