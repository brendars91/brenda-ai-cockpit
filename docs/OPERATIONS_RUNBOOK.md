# Operations Runbook: Brenda AI Cockpit Personal Production

## Scope
Producción aquí significa control plane privado de una sola operadora, no SaaS público. El servicio debe escuchar en loopback o Tailnet, requerir bearer auth para endpoints útiles, registrar acciones en `cockpit.db` y poder recuperarse desde backup probado.

## Runtime files
Crear a partir de la plantilla:

```bash
cp deploy/runtime/cockpit-api.conf.example deploy/runtime/cockpit-api.conf
python3 - <<'PY'
import secrets, pathlib
path = pathlib.Path('deploy/runtime/cockpit-token.txt')
path.write_text(secrets.token_urlsafe(48))
path.chmod(0o600)
PY
mkdir -p state backups
```

No commitear `deploy/runtime/cockpit-api.conf` ni `deploy/runtime/cockpit-token.txt`.

## Local smoke
```bash
npm run verify
COCKPIT_TOKEN_FILE=$PWD/deploy/runtime/cockpit-token.txt COCKPIT_TOKEN_SCOPES=admin COCKPIT_DB_PATH=$PWD/state/cockpit.db node apps/control-plane-api/dist/server.js 8787
node apps/control-plane-api/dist/healthcheck.js http://127.0.0.1:8787
node apps/control-plane-api/dist/backup.js backup state/cockpit.db backups
node apps/control-plane-api/dist/backup.js restore-test backups/<backup>.db
```

## systemd install
Esto modifica configuración del host. Ejecutar solo tras aprobación explícita de Brenda.

```bash
sudo cp deploy/systemd/brenda-ai-cockpit-api.service /etc/systemd/system/
sudo cp deploy/systemd/brenda-ai-cockpit-health.service /etc/systemd/system/
sudo cp deploy/systemd/brenda-ai-cockpit-health.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now brenda-ai-cockpit-api.service
sudo systemctl enable --now brenda-ai-cockpit-health.timer
systemctl status brenda-ai-cockpit-api.service --no-pager
systemctl list-timers brenda-ai-cockpit-health.timer --no-pager
```

## Tailscale boundary
Mantener API en `127.0.0.1`. Exponer solo mediante Tailscale Serve o SSH tunnel dentro de la tailnet. No usar `COCKPIT_ALLOW_PUBLIC_BIND=1` salvo diagnóstico temporal y documentado.

## Recovery drill
1. Ejecutar backup.
2. Ejecutar restore-test sobre el backup recién creado.
3. Guardar sha256 del manifest en evidencia de release.
4. No borrar backups hasta haber validado restore.

## Release gate
No declarar nivel 10 hasta que estén verdes:
- `npm run verify` local.
- CI remoto deterministic-gates.
- Smoke API con token real.
- Browser QA de UI contra API real.
- Backup + restore-test real.
- systemd instalado y health timer activo, o bloqueo declarado si Brenda decide no instalarlo.
