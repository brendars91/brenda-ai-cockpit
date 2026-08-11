# Brenda AI Cockpit - Architecture

## Estado actual
Brenda AI Cockpit es un monorepo npm/TypeScript para un control plane personal de agentes. El estado actual es **production-candidate local** con CI remoto verde y una primera frontera de producción personal en progreso: autenticación bearer, CORS cerrado y host seguro por defecto.

## Capas implementadas

### 1. Control Plane API (`apps/control-plane-api`)
- **Tech stack real:** Node.js `node:http` + TypeScript.
- **Endpoints readonly:** health, telemetry reads, adapters, capabilities, agent status.
- **Endpoint de delegación:** `/api/v1/delegate` valida requests y queda protegido por scope `command`.
- **Seguridad actual:** `/api/health` superficial es público; el resto requiere bearer auth cuando el servidor se configura para producción personal.
- **Boundary de red:** el arranque por defecto usa loopback (`127.0.0.1`). Public bind requiere override explícito.

### 2. Cockpit UI (`apps/cockpit-ui`)
- **Tech stack real:** React + TypeScript + Vite.
- **Estado:** build productivo verificado; pendiente de integrar flujo auth/commands/audit de producción personal.

### 3. Agent Runtime Console (`apps/agent-runtime-console`)
- **Tech stack real:** TypeScript package.
- **Estado:** expone estado runtime determinista y autorización de comandos sobre policy. Todavía no es executor persistente.

### 4. Packages
- `@cockpit/contracts`: tipos y contratos base.
- `@cockpit/context-fabric`: event log/context primitives.
- `@cockpit/capability-registry`: registro y búsqueda determinista de capacidades.
- `@cockpit/policy`: motor fail-closed para roles, riesgos y approvals.
- `@cockpit/quota-governor`: cuotas y freezes.
- `@cockpit/telemetry`: spans, métricas y redacción.
- `@cockpit/telemetry-reader`: snapshots/lecturas operativas.
- `@cockpit/intelligence`: scoring, findings y skill marketplace.
- `@cockpit/adapters`: Hermes, Claude Code, Codex y Paperclip.

## Data flow actual

```text
Cockpit UI / curl
    -> Control Plane API
       -> auth/CORS boundary
       -> readonly Hermes SQLite readers
       -> adapters/capability registry/runtime status
```

## Data flow objetivo para producción personal

```text
Brenda
  -> Tailscale/loopback only
  -> Cockpit UI
  -> authenticated Control Plane API
  -> Policy Enforcement Point
  -> cockpit.db command queue + audit ledger
  -> allowed action executor
  -> Hermes/GitHub/local services
```

## Storage

### Actual
- Lee DBs de Hermes en modo readonly para dashboards.
- No debe escribir en DBs de Hermes.

### Objetivo producción personal
- Añadir `cockpit.db` propio con SQLite WAL para commands, approvals, audit, deployments y health snapshots.
- Mantener DBs de Hermes como fuentes readonly.

## Security model resumido
- Privado por defecto: loopback/Tailscale.
- Auth obligatoria para endpoints útiles.
- CORS cerrado por allowlist.
- Sin credenciales hardcodeadas.
- Secret scan en CI.
- Policy antes de acciones mutativas.
- No shell libre desde UI/API.

## Reliability actual
- `/api/health` superficial.
- CI remoto `deterministic-gates` ejecuta `npm ci` + `npm run verify`.

## Reliability objetivo
- systemd con restart.
- health deep autenticado.
- smoke post-deploy.
- backup/restore probado.
- rollback de release.
- alertas en fallo.
