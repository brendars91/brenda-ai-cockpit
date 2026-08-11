# Brenda AI Cockpit

Control plane privado para agentes IA, context fabric, policy, adapters, telemetry y ejecución determinista de operaciones personales.

## Qué es ahora

Brenda AI Cockpit es un monorepo npm/TypeScript **production-candidate local** que está siendo promovido a **producción personal privada** para uso exclusivo de Brenda.

No es solo documentación: `npm run verify` ejecuta escaneo de secretos, validación estructural, typecheck, tests y build de todos los workspaces.

## Estado de producción personal

Implementado y verificado en esta línea de hardening:

- API Node HTTP con health superficial público.
- Bearer auth con scopes `read`, `command` y `admin` para endpoints útiles.
- CORS cerrado por allowlist.
- Host seguro por defecto (`127.0.0.1`).
- Public bind bloqueado salvo override explícito.
- Tests adversariales para missing auth, token inválido, scope insuficiente, CORS, payload grande y public bind.

Pendiente para declarar **nivel 10 completo**:

- `cockpit.db` propio con SQLite WAL y migraciones.
- Audit ledger append-only.
- Command queue persistente.
- Policy enforcement sobre acciones reales.
- Allowed action executor sin shell libre.
- UI operator-grade con auth/commands/audit.
- Deploy systemd/Tailscale.
- Backup y restore drill.
- Health deep, alertas, threat model y release tag.

## Fuentes integradas

- `interfaz-herramientas-IA`
- `Gem-Trinity-Genesis`
- `Creador-proyectos-compilador`
- `Generador-proyectos-determinista`

## Apps

- `apps/cockpit-ui` — dashboard React/Vite.
- `apps/control-plane-api` — API Node HTTP para control plane personal.
- `apps/agent-runtime-console` — runtime status y autorización de comandos.

## Paquetes

- `packages/contracts`
- `packages/policy`
- `packages/context-fabric`
- `packages/capability-registry`
- `packages/quota-governor`
- `packages/telemetry`
- `packages/telemetry-reader`
- `packages/intelligence`
- `packages/adapters`

## Verificación

```bash
npm install --workspaces --include-workspace-root --no-audit --no-fund
npm run verify
```

Gate esperado:

- `secret_scan: PASS`
- `validate_repo: PASS (4 source imports, 12 workspaces)`
- TypeScript typecheck verde
- Vitest verde
- Build completo verde, incluida UI Vite

## Smoke local

Health superficial sin auth:

```bash
node apps/control-plane-api/dist/server.js 8789
curl -fsS http://127.0.0.1:8789/api/health
```

Endpoints útiles requieren bearer token configurado. En producción personal, cargar el token desde archivo local protegido y acceder por loopback/Tailscale.

## Documentos de producción

- `docs/PERSONAL_PRODUCTION_ARCHITECTURE.md`
- `docs/SECURITY_MODEL.md`
- `docs/PRODUCTION_READINESS_CHECKLIST.md`
- `docs/ARCHITECTURE.md`
- `docs/MIGRATION_ROADMAP.md`
