# 🚀 MCPs de Productividad y Gestión

Este conjunto de herramientas conecta a Antigravity con plataformas de gestión, comunicación y productividad empresarial.

> ⚠️ **Nota de Activación:** Estas herramientas suelen requerir autenticación (OAuth/Tokens). Actívalas solo cuando el proyecto lo requiera explícitamente para mantener el entorno ligero.

## Herramientas Incluidas
1.  **Atlassian**: Gestión de JIRA (Issues), Confluence (Docs) y Compass.
2.  **Notion**: Gestión de bases de datos, páginas y documentación.
3.  **Google Suite**:
    *   **Gmail**: Envío y lectura de correos.
    *   **Google Calendar**: Gestión de eventos y agenda.
    *   **Google Drive**: Gestión de archivos y documentos (Docs/Sheets/Slides).
4.  **Slack**: Comunicación, mensajes y alertas en canales.

## 🎯 ¿Cuándo usar este conjunto?

### Caso 1: Gestión Ágil de Proyectos (Jira/Notion)
**Situación:** "Crea tickets en Jira para todos los TODOs encontrados en el código" o "Actualiza la documentación en Notion con la nueva arquitectura".
**Selección:** `atlassian` o `notion`.
**Uso Técnico:**
- El agente escanea el código (`filesystem`/`smart-coding`) para identificar tareas.
- Usa `atlassian` para crear issues en Jira enlazados al código.
- Usa `notion` para crear páginas de especificación técnica automáticamente.

### Caso 2: Asistente Personal y Agenda
**Situación:** "Revisa mi calendario para ver si tengo hueco para una reunión de 30 min hoy y avísame por Slack".
**Selección:** `google-calendar`, `slack`.
**Uso Técnico:**
- `google-calendar` consulta la disponibilidad (`get-freebusy`).
- Si hay hueco, `slack` envía un mensaje privado de confirmación.

### Caso 3: Automatización de Documentos
**Situación:** "Genera un reporte de gastos basado en estos correos y guárdalo en Drive".
**Selección:** `gmail`, `google-drive`.
**Uso Técnico:**
- `gmail` busca correos con facturas (`search_emails`).
- `google-drive` crea una hoja de cálculo (`createGoogleSheet`) y vuelca los datos extraídos.

## 💡 Estrategia de Selección
- **Para desarrollo/código puro:** Mantén estos MCPs desactivados.
- **Para gestión/Project Management:** Activa `atlassian` o `notion`.
- **Para automatización de oficina:** Activa las herramientas de Google o Slack según necesidad.
