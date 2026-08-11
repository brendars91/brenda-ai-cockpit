# Personal Production Architecture

## Tesis
Brenda AI Cockpit es un control plane privado de una sola operadora. Producción para este repo significa operar con privacidad, autenticación, trazabilidad, recuperación y rollback; no significa SaaS público ni multi-tenant.

## Invariantes
1. Cero superficie pública por defecto.
2. Acceso por loopback/Tailscale.
3. Auth obligatoria para cualquier endpoint útil.
4. DBs de Hermes readonly.
5. Estado propio en `cockpit.db`.
6. Toda acción mutativa pasa por policy.
7. Toda acción mutativa queda auditada.
8. No hay shell libre desde UI/API.
9. Backup y restore deben probarse.
10. CI remoto y smoke post-deploy son obligatorios antes de declarar producción.

## Arquitectura objetivo

```text
Brenda
  -> Tailnet privada
  -> Cockpit UI
  -> Control Plane API autenticada
  -> Policy Enforcement Point
  -> cockpit.db: queue + approvals + audit
  -> Allowed Action Executor
  -> Hermes / GitHub / Paperclip / servicios locales
```

## Alcance deliberadamente excluido
- Kubernetes.
- Multi-tenant RBAC.
- OAuth externo en primera versión.
- Puerto público OCI.
- Comandos shell arbitrarios.
- PostgreSQL obligatorio mientras el uso sea personal y de baja concurrencia.

## Camino a nivel 10
1. PR-0/1: auth, CORS cerrado, host seguro, docs reality check.
2. PR-2: `cockpit.db` SQLite WAL y migraciones.
3. PR-3: audit ledger append-only.
4. PR-4: command queue + approvals + policy real.
5. PR-5: allowed action executor.
6. PR-6: UI operator-grade.
7. PR-7: systemd/Tailscale deploy.
8. PR-8: backup + restore drill.
9. PR-9: health deep + alertas.
10. PR-10: threat model + adversarial suite.
11. PR-11: release `v0.2.0-personal-production`.
