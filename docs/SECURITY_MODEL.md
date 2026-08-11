# Security Model

## Objetivo
Proteger un control plane personal de agentes contra exposición accidental, uso no autorizado, ejecución peligrosa sin aprobación y pérdida de trazabilidad.

## Activos
- Token bearer del Cockpit.
- DB propia `cockpit.db`.
- DBs readonly de Hermes.
- Command queue persistente.
- Audit ledger append-only con hash-chain.
- GitHub/CLI/local services invocados por acciones permitidas.

## Boundary de red
- Default: `127.0.0.1`.
- Acceso remoto permitido solo vía Tailscale o proxy limitado a tailnet.
- Public bind (`0.0.0.0` o `::`) falla salvo override explícito `COCKPIT_ALLOW_PUBLIC_BIND=1`.

## Auth
- `/api/health` es público y superficial.
- Endpoints readonly requieren scope `read`.
- Endpoints mutativos requieren scope `command` o `admin`.
- Si auth no está configurada, los endpoints útiles fallan cerrado con `auth_not_configured`.
- Los tokens se comparan por hash SHA-256 con comparación timing-safe.
- La UI no persiste el token: lo mantiene en memoria del navegador.

## CORS
- Sin wildcard en modo producción.
- Origins permitidos por allowlist.
- Requests sin `Origin` se permiten para CLI/curl local, siempre sujetos a auth si el endpoint lo requiere.

## Policy y ejecución
- Submit de comandos valida `action`, `risk`, target e identidad antes de llamar a policy.
- `credential_access` se deniega siempre.
- R3+ y deploy/delete quedan `pending_approval` hasta receipt owner.
- El executor solo corre acciones catalogadas con `spawn(..., shell:false)`, timeout y output cap.
- No existe endpoint de shell libre.

## Audit y recuperación
- Cada submit/approval/running/succeeded/failed se registra en `audit_events`.
- La cadena `previous_hash`/`event_hash` detecta manipulación de eventos.
- Backup físico de SQLite usa `better-sqlite3.backup()` y manifest con sha256.
- Restore-test copia el backup a un directorio temporal, abre DB restaurada y verifica migraciones + audit chain.

## Tests adversariales mínimos implementados
- missing auth -> 401.
- invalid token -> 401 sin filtrar token.
- read token en POST -> 403.
- CORS origin desconocido -> 403.
- payload grande -> 413.
- public bind sin override -> error.
- auth no configurada -> fail closed.
- action/risk desconocidos -> 400.
- audit tampering -> chain false.
- uncatalogued action -> failed audited.
- timeout executor -> failed audited.
