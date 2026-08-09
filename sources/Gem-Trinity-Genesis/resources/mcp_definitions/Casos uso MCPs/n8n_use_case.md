# ⚡ MCPs de Automatización (n8n)

Estas herramientas conectan a Antigravity con tu servidor de automatización **n8n**, permitiéndole ejecutar flujos de trabajo complejos que interactúan con servicios externos.

## Herramientas Incluidas
1.  **n8n-native**: Conexión vía protocolo "Supergateway" (Recomendado/Rápido).
2.  **n8n-mcp**: Conexión vía contenedor Docker (Backup/Legacy).

## 🎯 ¿Cuándo usar este conjunto?

### Caso 1: Orquestación de Procesos de Negocio
**Situación:** Necesitas procesar una factura, enviarla por email, guardarla en Drive y notificar en Slack.
**Acción Agente:** "Ejecuta el workflow de procesamiento de facturas para este archivo."
**Uso Técnico:** El agente dispara un workflow de n8n pasando el archivo como input. n8n maneja las integraciones (Gmail, Slack, Drive) usando sus propios credenciales.

### Caso 2: Webhooks y Eventos
**Situación:** Quieres que el agente reaccione cuando ocurra algo externo.
**Acción Agente:** "Revisa si hay ejecuciones fallidas en el workflow de CRM."
**Uso Técnico:** El agente consulta el historial de ejecuciones de n8n para diagnosticar problemas.

### Caso 3: Integración con Servicios no Soportados Nativamente
**Situación:** Necesitas enviar datos a una API rara para la cual no tenemos un MCP específico.
**Acción Agente:** "Crea y ejecuta un flujo en n8n que haga POST a esta API custom."
**Uso Técnico:** n8n actúa como un "adaptador universal" para cualquier API HTTP.

## ⚠️ Requisitos
- **Servidor n8n corriendo:** Debe estar activo en `localhost:5678`.
- **API Key:** Configurada correctamente en `settings.json`.
