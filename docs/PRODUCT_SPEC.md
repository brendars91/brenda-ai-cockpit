# Brenda AI Cockpit - Product Specification

## Estado verificado
Brenda AI Cockpit es ahora un workspace npm/TypeScript verificable que consolida fuentes heredadas en un control plane operativo para observabilidad, registro de capacidades, política de autorización, cuotas, telemetry, runtime status y UI estática.

El estado actual probado es **producto local production-candidate**, no despliegue remoto en producción: compila, testea, sirve API/UI en local y tiene CI configurado para ejecutar el mismo gate.

## Superficie implementada

### 1. Control Plane API (`apps/control-plane-api`)
Endpoints GET verificados:
- `/api/health` — healthcheck live-sqlite.
- `/api/summary`, `/api/sessions`, `/api/costs`, `/api/tools`, `/api/cron`, `/api/evidence`, `/api/memory` — lecturas readonly sobre SQLite real de Hermes cuando existe.
- `/api/v1/adapters` — catálogo canónico de adapters.
- `/api/v1/capabilities` — capacidades derivadas de adapters y registradas en `CapabilityRegistry`.
- `/api/v1/agents/status` — estado runtime determinista de agentes.

Endpoint POST verificado:
- `/api/v1/delegate` — valida forma de solicitud de delegación y rechaza payload inválido.

### 2. Paquetes canónicos (`packages/*`)
- `@cockpit/contracts`: contratos TypeScript/Zod heredados y OpenAPI inicial en `api-spec.json`.
- `@cockpit/context-fabric`: event log, replay determinista, hash chain, projections e idempotency store.
- `@cockpit/capability-registry`: registro tipado de capacidades con búsqueda determinista.
- `@cockpit/policy`: motor fail-closed para acciones por rol/riesgo/aprobaciones.
- `@cockpit/quota-governor`: ventanas rolling/weekly, freeze y decisiones allow/defer/deny/degrade.
- `@cockpit/telemetry`: spans, counters/histograms y redacción de atributos sensibles.
- `@cockpit/telemetry-reader`: snapshots sanitizados y funciones de análisis operacional.
- `@cockpit/intelligence`: scoring, findings y brief ejecutivo sobre telemetry real/sanitizada.
- `@cockpit/adapters`: registry canónico Hermes, Claude Code, Codex y Paperclip.

### 3. Apps (`apps/*`)
- `@cockpit/cockpit-web`: dashboard React/Vite compilable con dashboards de coste, evidencia, sesiones, cron, tools y memoria.
- `@cockpit/control-plane-api`: API Node HTTP compilable y testeada.
- `@cockpit/agent-runtime-console`: proyección de estado runtime y autorización de comandos por política.

### 4. Gates deterministas
`npm run verify` ejecuta:
1. `python3 tools/secret_scan.py .`
2. `python3 tools/validate_repo.py`
3. build previo de dependencias internas + `tsc --noEmit` por workspace
4. tests Vitest por workspace
5. build completo, incluido Vite production build

## Seguridad
- `secret_scan.py` detecta patrones GitHub, provider `sk-*`, Google API keys, private keys y token Neptune-like.
- Directorios generados (`node_modules`, `dist`, coverage, caches) quedan excluidos del escaneo para evitar ruido.
- `@cockpit/policy` niega acceso a credenciales por diseño y exige aprobación para acciones destructivas o R3+.

## Evidencia local actual
- `secret_scan: PASS`
- `validate_repo: PASS (4 source imports, 12 workspaces)`
- `npm run typecheck`: PASS
- `npm run test`: PASS, 198 tests efectivos tras eliminar duplicación de `dist`
- `npm run build`: PASS, Vite production bundle generado
- Smoke API: `/api/health`, `/api/v1/delegate`, `/api/v1/capabilities`, `/api/v1/agents/status`
- Smoke UI: HTML servido desde `apps/cockpit-ui/dist`

## Límites explícitos
- No se ha desplegado a un dominio público ni se ha validado CI remoto todavía.
- No hay autenticación/JWT productiva en API; el control plane está diseñado para red interna/local hasta añadir auth.
- La API lee SQLite local de Hermes; para multiusuario/producción externa falta adapter PostgreSQL y gestión de secretos/identidad.
- No se afirma cobertura 100%; se afirma suite verde con tests unitarios/integración existentes.
