# Brenda AI Cockpit

Control plane avanzado para agentes IA, context fabric, policy, adapters, telemetry y ejecución determinista.

## Qué es ahora

Brenda AI Cockpit es un monorepo npm/TypeScript production-candidate local: consolida fuentes heredadas en paquetes canónicos, expone una API de control plane, sirve una UI operacional y ejecuta gates deterministas reales.

No es solo documentación: `npm run verify` ejecuta escaneo de secretos, validación estructural, typecheck, tests y build de todos los workspaces.

## Fuentes integradas

- `interfaz-herramientas-IA`
- `Gem-Trinity-Genesis`
- `Creador-proyectos-compilador`
- `Generador-proyectos-determinista`

## Apps

- `apps/cockpit-ui` — dashboard React/Vite.
- `apps/control-plane-api` — API Node HTTP readonly/control plane.
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

```bash
node apps/control-plane-api/dist/server.js 8789
curl -fsS http://127.0.0.1:8789/api/health
curl -fsS http://127.0.0.1:8789/api/v1/capabilities
curl -fsS http://127.0.0.1:8789/api/v1/agents/status
```

Para la UI:

```bash
cd apps/cockpit-ui
npx vite preview --host 127.0.0.1 --port 5190
```

## Estado honesto

Verificado como production-candidate local. Para producción externa faltan auth/JWT, storage productivo, ejecución real persistente, CI remoto verde y despliegue protegido.
