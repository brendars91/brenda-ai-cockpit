# Slack MCP Server Usage Rules

MCP Server para Slack - mensajes, canales, historial y búsqueda.

> ⚠️ **Community MCP** - Verificar seguridad, fijar versión, minimizar scopes.

## Configuración

⚠️ **Reemplaza `YOUR_SLACK_TOKEN_HERE`** en settings.json con tu token de Slack.

### Obtener Token
1. Crear Slack App en https://api.slack.com/apps
2. OAuth & Permissions → Bot Token Scopes:
   - `channels:history`
   - `channels:read`
   - `chat:write`
   - `users:read`
   - `search:read`
3. Install to Workspace
4. Copiar Bot User OAuth Token (`xoxb-...`)

## Herramientas Disponibles

| Tool | Descripción |
|------|-------------|
| `conversations_history` | Obtener mensajes de canal/DM |
| `conversations_replies` | Obtener respuestas en hilo |
| `conversations_add_message` | Enviar mensaje |
| `conversations_search_messages` | Buscar mensajes |
| `channels_list` | Listar canales |

## Recursos

| Resource | Descripción |
|----------|-------------|
| `slack://<workspace>/channels` | Directorio de canales |
| `slack://<workspace>/users` | Directorio de usuarios |

## Cuándo Usar

**Trigger:** Automatización de Slack, búsqueda de mensajes, envío de notificaciones.

**Action:**
- Enviar mensajes desde código
- Buscar información en conversaciones
- Obtener historial de canales
- Automatizar notificaciones

## Best Practices de Seguridad

1. **Minimizar scopes** - Solo permisos necesarios
2. **Token rotation** - Rotar tokens regularmente
3. **Fijar versión** - Usar versión específica del paquete
4. **Auditar uso** - Revisar logs de acceso
