# Production Readiness Checklist

## Estado objetivo: producción personal nivel 10

### Acceso y red
- [x] Host seguro por defecto: loopback.
- [x] Public bind requiere override explícito.
- [x] `/api/health` superficial público.
- [x] Endpoints útiles requieren auth.
- [x] CORS por allowlist.
- [x] Acceso Tailscale verificado en host de producción: `tailscale serve status` muestra `https://gemini-arm-node-01.tail22d85a.ts.net:8787 (tailnet only)` y browser QA confirmó `/api/health` OK + `/api/v1/commands` cerrado sin bearer.

### Seguridad API
- [x] Bearer auth con scopes.
- [x] Missing/invalid token cubierto por tests.
- [x] Token readonly bloqueado en endpoint mutativo.
- [x] Payload grande bloqueado.
- [x] Action/risk inválidos fallan cerrado antes de policy.
- [x] Rotación/revocación por token file verificada en host: drill cambió token, reinició API, token viejo devolvió 401 y token nuevo 200. Multi-token persistente queda fuera de scope por diseño single-operator.

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
- [x] Instalación systemd real en host aprobada y ejecutada: API active/enabled, health timer active/enabled, proceso `User=ubuntu`, listener solo `127.0.0.1:8787`.
- [x] Tailscale Serve verificado privado: `:8787 (tailnet only)`; Funnel no activado.
- [x] Alertas Discord ante fallo: watchdog Python verde silencioso, `--test` entregó mensaje Discord `1536659525229215754`.

### Recuperación
- [x] Backup físico de SQLite.
- [x] Manifest con sha256/tamaño.
- [x] Restore drill probado por test automatizado.
- [x] Rollback systemd probado en host real: unidades copiadas a `backups/systemd-rollback-drill-20260811/`, restauradas con `install`, `daemon-reload`, restart API y smoke post-rollback `succeeded`.

### Release
- [x] CI remoto verde: GitHub Actions `deterministic-gates` success en release commit `13ec38d37932b6fd96b250696e8625ad944e47b9` (`31476037064`).
- [x] Smoke local API/UI contra build real: auth, command execution, health deep, backup y restore-test.
- [x] Smoke post-deploy systemd/Tailscale verde: API systemd activa, health deep por timer OK, Tailscale HTTPS `/api/health` OK, endpoint útil cerrado sin bearer, submit+execute post-deploy `succeeded`.
- [x] Browser QA UI.
- [x] Threat model actualizado al código.
- [x] Tag `v0.2.0-personal-production` creado sobre el release final verificado.

## Regla de honestidad
Todos los checks de host real, CI remoto, smoke local/post-deploy, browser QA, recovery, alertas y release tag deben estar verdes antes de declarar producción personal nivel 10.
