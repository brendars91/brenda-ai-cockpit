# Gmail MCP Server Usage Rules

MCP Server para integración con Gmail - enviar, leer, buscar y gestionar correos.

> ⚠️ **Community MCP** - Revisar permisos, minimizar scopes, rotar credenciales.

## Primera Configuración

1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com)
2. Habilitar Gmail API
3. Crear credenciales OAuth 2.0
4. Guardar como `gcp-oauth.keys.json` en `~/.gmail-mcp/`
5. Primera ejecución: autenticación automática vía navegador

## Herramientas Disponibles

### Envío y Borradores
| Tool | Descripción |
|------|-------------|
| `send_email` | Enviar email (text/HTML/adjuntos) |
| `draft_email` | Crear borrador |

### Lectura y Búsqueda
| Tool | Descripción |
|------|-------------|
| `read_email` | Leer contenido de email |
| `search_emails` | Buscar con sintaxis Gmail |
| `download_attachment` | Descargar adjuntos |

### Gestión
| Tool | Descripción |
|------|-------------|
| `modify_email` | Añadir/quitar etiquetas |
| `delete_email` | Eliminar permanentemente |
| `batch_modify_emails` | Modificar múltiples |
| `batch_delete_emails` | Eliminar múltiples |

### Etiquetas
| Tool | Descripción |
|------|-------------|
| `list_email_labels` | Listar etiquetas |
| `create_label` | Crear etiqueta |
| `update_label` | Actualizar etiqueta |
| `delete_label` | Eliminar etiqueta |

### Filtros
| Tool | Descripción |
|------|-------------|
| `create_filter` | Crear filtro |
| `list_filters` | Listar filtros |
| `delete_filter` | Eliminar filtro |

## Sintaxis de Búsqueda

```
from:sender@example.com after:2024/01/01 has:attachment
subject:"meeting" is:unread
```

## Cuándo Usar

**Trigger:** Automatización de email, búsquedas o gestión de correo.

**Action:**
- Enviar emails desde código/especificaciones
- Buscar y procesar emails automáticamente
- Gestionar etiquetas y filtros
- Descargar adjuntos
