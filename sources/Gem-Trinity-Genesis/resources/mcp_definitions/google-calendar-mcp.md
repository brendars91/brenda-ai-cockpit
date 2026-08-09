# Google Calendar MCP Usage Rules

MCP Server para gestión de Google Calendar - eventos, disponibilidad y múltiples cuentas.

> ⚠️ **Community MCP** - Revisar permisos, minimizar scopes, rotar credenciales.

## Primera Configuración

1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com)
2. Habilitar Google Calendar API
3. Crear credenciales OAuth 2.0
4. Guardar como `gcp-oauth.keys.json`
5. Configurar `GOOGLE_OAUTH_CREDENTIALS` con la ruta al archivo
6. Primera ejecución: autenticación automática vía navegador

## Variables de Entorno

```bash
GOOGLE_OAUTH_CREDENTIALS=/path/to/gcp-oauth.keys.json
GOOGLE_CALENDAR_MCP_TOKEN_PATH=/custom/token/path  # opcional
ENABLED_TOOLS=list-events,create-event,delete-event  # opcional
```

## Herramientas Disponibles

| Tool | Descripción |
|------|-------------|
| `list-calendars` | Listar todos los calendarios |
| `list-events` | Listar eventos |
| `get-event` | Obtener detalles de evento |
| `search-events` | Buscar eventos |
| `create-event` | Crear evento |
| `update-event` | Actualizar evento |
| `delete-event` | Eliminar evento |
| `respond-to-event` | Responder a invitación |
| `get-freebusy` | Consultar disponibilidad |
| `get-current-time` | Obtener hora actual |
| `list-colors` | Listar colores disponibles |
| `manage-accounts` | Gestionar múltiples cuentas |

## Cuándo Usar

**Trigger:** Gestión de calendario, programación de reuniones, consultar disponibilidad.

**Action:**
- Crear eventos desde especificaciones/notas
- Consultar disponibilidad de participantes
- Buscar eventos por fecha/título
- Automatizar respuestas a invitaciones

## Nota sobre Test Mode

En modo test (por defecto), los tokens expiran cada 7 días. Para evitarlo:
1. Google Cloud Console → OAuth consent screen
2. Click "PUBLISH APP"
