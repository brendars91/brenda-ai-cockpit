# Google Drive MCP Usage Rules

Integración segura con Google Drive, Docs, Sheets y Slides.

> ⚠️ **Community MCP** - Revisar permisos, minimizar scopes, rotar credenciales.

## Primera Configuración

1. Crear proyecto en [Google Cloud Console](https://console.cloud.google.com)
2. Habilitar APIs: Drive, Docs, Sheets, Slides
3. Configurar OAuth consent screen
4. Crear credenciales OAuth 2.0
5. Primera ejecución: `npx @piotr-agier/google-drive-mcp auth`

## Herramientas Disponibles

### Navegación
| Tool | Descripción |
|------|-------------|
| `search` | Buscar archivos en Drive |
| `listFolder` | Listar contenido de carpeta |

### Gestión de Archivos
| Tool | Descripción |
|------|-------------|
| `createTextFile` | Crear archivo .txt o .md |
| `updateTextFile` | Actualizar archivo texto |
| `deleteItem` | Mover a papelera |
| `renameItem` | Renombrar archivo/carpeta |
| `moveItem` | Mover archivo/carpeta |
| `createFolder` | Crear carpeta |

### Google Docs
| Tool | Descripción |
|------|-------------|
| `createGoogleDoc` | Crear documento |
| `updateGoogleDoc` | Actualizar documento |
| `getGoogleDocContent` | Obtener contenido |
| `formatGoogleDocText` | Formatear texto |
| `formatGoogleDocParagraph` | Formatear párrafo |

### Google Sheets
| Tool | Descripción |
|------|-------------|
| `createGoogleSheet` | Crear hoja de cálculo |
| `updateGoogleSheet` | Actualizar celdas |

### Google Slides
| Tool | Descripción |
|------|-------------|
| `createGoogleSlides` | Crear presentación |
| `updateGoogleSlides` | Actualizar presentación |

## Cuándo Usar

**Trigger:** Gestión de archivos en Google Drive o creación de documentos.

**Action:**
- Buscar y organizar archivos en Drive
- Crear documentos desde código/especificaciones
- Actualizar hojas de cálculo con datos
- Generar presentaciones automáticamente
