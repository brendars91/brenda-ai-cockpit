# 🔧 Cómo Habilitar Rube (Composio MCP)

## Estado Actual
❌ **Deshabilitado** - La API key de Composio es inválida o expirada

## Problema
La API key actual de Composio retorna error:
```
{"error":{"message":"Invalid API key","code":10401}}
```

Composio migró de API v1 a **API v3** y las keys antiguas ya no funcionan.

---

## ✅ Solución: Regenerar API Key

### Paso 1: Obtener nueva API Key de Composio

1. Ve a **https://app.composio.dev/settings/api-keys**
2. Inicia sesión con tu cuenta
3. Crea una nueva API Key:
   - Click en **"Create API Key"**
   - Dale un nombre: `"Antigravity MCP"`
   - Copia la key generada (formato: `comp_xxxxx...`)

### Paso 2: Actualizar la configuración

Una vez tengas la nueva API key, actualiza el archivo `.env`:

```bash
# En c:\Users\ASUS\.gemini\antigravity\.env
COMPOSIO_API_KEY=comp_tu_nueva_api_key_aqui
```

### Paso 3: Actualizar mcp_config.json

Reemplaza la configuración de `rube` en `mcp_config.json`:

```json
"rube": {
  "command": "ssh",
  "args": [
    "-o", "StrictHostKeyChecking=no",
    "ubuntu@100.69.240.73",
    "python3", "/tmp/composio-mcp-server.py"
  ],
  "env": {
    "COMPOSIO_API_KEY": "comp_tu_nueva_api_key_aqui",
    "HOME": "C:\\Users\\ASUS"
  }
}
```

### Paso 4: Subir el servidor actualizado al servidor OCI

```powershell
scp c:\Users\ASUS\.gemini\antigravity\composio-mcp-server.py ubuntu@100.69.240.73:/tmp/
```

### Paso 5: Probar que funciona

```powershell
ssh ubuntu@100.69.240.73 'export COMPOSIO_API_KEY="comp_tu_nueva_key" && echo "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{},\"clientInfo\":{\"name\":\"test\",\"version\":\"1.0\"}}}" | python3 /tmp/composio-mcp-server.py'
```

Deberías ver:
```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05",...}}
```

### Paso 6: Habilitar en mcp_config.json

Quita `"disabled": true` de la configuración de `rube`.

### Paso 7: Reiniciar Antigravity

Reinicia Antigravity para que cargue la nueva configuración.

---

## 📋 Servidor MCP Personalizado

He creado un **servidor MCP personalizado** (`composio-mcp-server.py`) que:

✅ Usa la **API REST v3 de Composio**  
✅ Expone herramientas de Composio via **protocolo MCP stdio**  
✅ Funciona con **500+ integraciones** (Slack, GitHub, Gmail, etc.)  
✅ Se ejecuta en tu **servidor OCI remoto** (Python 3.10)

### Características:
- **Protocolo**: MCP stdio (compatible con Antigravity)
- **API**: Composio REST API v3
- **Transporte**: SSH al servidor remoto
- **Dependencias**: Solo `httpx` (ya instalado)

---

## 🔐 Seguridad

- ✅ API key guardada en `.env` (protegido por `.gitignore`)
- ✅ Comunicación via SSH encriptado (Tailscale)
- ✅ Sin exposición de puertos públicos

---

## 📊 Herramientas Disponibles

Una vez habilitado, tendrás acceso a **500+ herramientas** de Composio:

- **Comunicación**: Slack, Discord, Gmail, Outlook
- **Desarrollo**: GitHub, GitLab, Jira, Linear
- **Productividad**: Google Drive, Notion, Asana, Trello
- **CRM**: Salesforce, HubSpot, Pipedrive
- **Y muchas más...**

---

## ❓ Preguntas Frecuentes

**P: ¿Por qué no usar `@composio/mcp` directamente?**  
R: Ese paquete es un **cliente** que se conecta a servidores MCP, no un servidor MCP de Composio. No soporta stdio.

**P: ¿Por qué usar SSH al servidor remoto?**  
R: Windows no tiene Python instalado localmente. El servidor OCI ya tiene Python 3.10 y está disponible 24/7.

**P: ¿Puedo usar Composio sin MCP?**  
R: Sí, puedes usar el SDK de Composio directamente en tu código Python/TypeScript, pero MCP permite que Antigravity use las herramientas automáticamente.

---

**Archivo creado**: 2026-02-14  
**Versión del servidor**: 1.0.0  
**API de Composio**: v3
