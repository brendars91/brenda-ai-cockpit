# Brenda AI Cockpit - Migration Roadmap

## Estado actual: production-candidate local
El repo ya no es solo un corte de consolidación. Tiene workspace npm coherente, paquetes canónicos, API, UI, runtime console, gates deterministas y smoke local verificado.

## Completado
- [x] Source manifest con 4 fuentes saneadas.
- [x] 12 workspaces verificables bajo `apps/*` y `packages/*`.
- [x] `@cockpit/contracts` promovido desde fuente heredada + `api-spec.json` inicial.
- [x] `@cockpit/context-fabric` con event log, replay, projections, hash chain e idempotency.
- [x] `@cockpit/quota-governor` con ventanas rolling/weekly, freeze y decisiones de cuota.
- [x] `@cockpit/telemetry` con spans, metrics y redacción de atributos sensibles.
- [x] `@cockpit/telemetry-reader` con snapshots sanitizados y análisis operacional.
- [x] `@cockpit/intelligence` con scoring, findings, brief ejecutivo y skill marketplace testable.
- [x] `@cockpit/policy` fail-closed para roles, riesgos y aprobaciones.
- [x] `@cockpit/adapters` con registry Hermes, Claude Code, Codex y Paperclip.
- [x] `@cockpit/capability-registry` con registro/búsqueda determinista.
- [x] `apps/control-plane-api` con health, telemetry reads, adapters, capabilities, agent status y delegate validation.
- [x] `apps/cockpit-ui` con Vite production build.
- [x] `apps/agent-runtime-console` con estado runtime y autorización de comandos.
- [x] CI `deterministic-gates` configurado para `npm ci` + `npm run verify`.
- [x] Secret scan, validate repo, typecheck, tests, build y smoke local.

## Próximas fases para producción externa real

### Fase 1 — Auth y boundary de red
- [ ] Añadir autenticación JWT/signed internal token en `control-plane-api`.
- [ ] Separar endpoints readonly vs endpoints que ejecutan acciones.
- [ ] Añadir tests de rechazo para requests sin auth, token expirado y scope insuficiente.

### Fase 2 — Storage productivo
- [ ] Añadir adapter PostgreSQL para context fabric/telemetry operational state.
- [ ] Mantener SQLite como modo local/dev readonly.
- [ ] Añadir migraciones versionadas y tests de rollback.

### Fase 3 — Runtime execution real
- [ ] Convertir `agent-runtime-console` de proyección determinista a executor con queue persistente.
- [ ] Añadir receipts de aprobación para acciones R3+.
- [ ] Añadir audit log de cada comando con hash de entrada/salida.

### Fase 4 — CI remoto y release
- [ ] Verificar GitHub Actions remoto en PR.
- [ ] Publicar artefacto/release interno.
- [ ] Añadir deploy interno detrás de Tailscale o GitHub Pages solo para UI estática si el repo queda público.

### Fase 5 — Observabilidad de producción
- [ ] Healthchecks de dependencias reales.
- [ ] Alertas por fallos de cron/API/build.
- [ ] Dashboard de errores por fingerprint y coste por agente.

## Criterio de promoción
El repo puede considerarse **production-candidate local** cuando `npm run verify` y smoke local pasan. Puede considerarse **producción externa** solo cuando auth, storage productivo, ejecución real, CI remoto y deploy protegido estén verificados.
