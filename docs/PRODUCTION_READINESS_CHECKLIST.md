# Production Readiness Checklist

## Estado objetivo: producción personal nivel 10

### Acceso y red
- [x] Host seguro por defecto: loopback.
- [x] Public bind requiere override explícito.
- [x] `/api/health` superficial público.
- [x] Endpoints útiles requieren auth.
- [x] CORS por allowlist.
- [ ] Acceso Tailscale verificado en host de producción.

### Seguridad API
- [x] Bearer auth con scopes.
- [x] Missing/invalid token cubierto por tests.
- [x] Token readonly bloqueado en endpoint mutativo.
- [x] Payload grande bloqueado.
- [x] Action/risk inválidos fallan cerrado antes de policy.
- [ ] Rotación/revocación persistente multi-token en `cockpit.db`.

### Datos
- [x] Hermes DBs leídas readonly.
- [x] Tests CI-safe con fixtures, no DBs locales reales.
- [x] `cockpit.db` propio.
- [x] Migraciones versionadas.
- [x] WAL/busy timeout.

### Commands/runtime
- [x] Command queue persistente.
- [x] Policy enforcement en submit.
- [x] Approval receipts R3+.
- [x] Allowed action executor.
- [x] Sin shell libre.
- [x] Execution transitions auditadas: running/succeeded/failed.

### UI operador
- [x] Token bearer en memoria del navegador.
- [x] Catálogo cerrado de acciones.
- [x] Queue/approve/execute desde UI.
- [x] Audit chain visible.
- [x] Browser QA visual contra API real: UI cargó, token habilitó controles, refresh leyó commands/audit, queue+execute desde UI terminó `succeeded`, consola sin JS errors.

### Operación
- [x] Plantillas systemd API + health timer.
- [x] Healthcheck superficial y profundo autenticado.
- [x] Backup CLI.
- [x] Restore-test CLI.
- [ ] Instalación systemd real en host aprobada y ejecutada.
- [ ] Tailscale Serve/Funnel verificado privado.
- [ ] Alertas Discord ante fallo.

### Recuperación
- [x] Backup físico de SQLite.
- [x] Manifest con sha256/tamaño.
- [x] Restore drill probado por test automatizado.
- [ ] Rollback systemd probado en host real.

### Release
- [x] CI remoto verde: GitHub Actions `deterministic-gates` success en PR #4.
- [x] Smoke local API/UI contra build real: auth, command execution, health deep, backup y restore-test.
- [ ] Smoke post-deploy systemd/Tailscale verde.
- [x] Browser QA UI.
- [x] Threat model actualizado al código.
- [ ] Tag `v0.2.0-personal-production`.

## Regla de honestidad
Mientras haya checks pendientes de host real/CI remoto/browser QA, el repo puede estar endurecido y validado localmente, pero no se declara producción personal nivel 10.
