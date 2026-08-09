# Configuración MCP para Antigravity

Esta carpeta contiene la configuración completa de los servidores MCP (Model Context Protocol) para Antigravity.

## 📊 Estado: 11 de 12 MCPs Operativos (91.7%)

### ✅ MCPs Activos
1. **filesystem** - Acceso a workspaces
2. **github** - Integración con GitHub
3. **notebooklm-mcp** - Google NotebookLM
4. **context7** - Documentación de librerías
5. **sequential-thinking** - Razonamiento paso a paso
6. **playwright** - Automatización web
7. **fetch** - Web scraping
8. **docker** - Control Docker remoto
9. **semgrep** - Análisis de código
10. **n8n-mcp** - Documentación n8n + workflows (1,084 nodos)
11. **rube** - Composio (500+ integraciones)

### ⚠️ MCP Deshabilitado
- **n8n-native** - Requiere n8n con soporte MCP nativo

## 📁 Archivos

### Configuración Principal
- **`mcp_config.json`** - Configuración de todos los MCPs
- **`.env.example`** - Template de variables de entorno (NO incluir .env real)
- **`antigravity.gitignore`** - Archivos a ignorar en Git

### Servidor MCP Personalizado (Rube/Composio)
- **`composio-mcp-server.py`** - Servidor MCP para Composio API
- **`composio-requirements.txt`** - Dependencias Python

### Documentación
- **`MCP_FINAL_REPORT.md`** - Reporte completo de configuración
- **`COMPOSIO_SETUP.md`** - Guía de setup de Composio
- **`README.md`** - Este archivo

## 🚀 Uso

### 1. Configurar Variables de Entorno
Crea un archivo `.env` en `c:\Users\ASUS\.gemini\antigravity\` con:
```bash
N8N_API_KEY=tu_api_key_aqui
COMPOSIO_API_KEY=tu_api_key_aqui
GITHUB_PERSONAL_ACCESS_TOKEN=tu_token_aqui
DOCKER_HOST=ssh://ubuntu@100.69.240.73
```

### 2. Copiar Configuración
Copia `mcp_config.json` a la ubicación de configuración de Antigravity.

### 3. Desplegar Servidor Composio
```bash
scp composio-mcp-server.py ubuntu@100.69.240.73:/tmp/
ssh ubuntu@100.69.240.73 'pip3 install --user httpx'
```

### 4. Reiniciar Antigravity
Reinicia Antigravity para cargar la nueva configuración.

## 🔐 Seguridad

- **NUNCA** commitear archivos `.env` con credenciales reales
- Usar `.gitignore` para proteger archivos sensibles
- Las API keys deben regenerarse si se exponen

## 📝 Notas

- **n8n-mcp** requiere las variables de entorno específicas del repositorio oficial
- **Rube (Composio)** es un servidor MCP personalizado que usa la API REST v3
- Todos los MCPs han sido verificados y funcionan correctamente

## 🔗 Referencias

- [Repositorio n8n-mcp](https://github.com/czlonkowski/n8n-mcp)
- [Composio API](https://composio.dev)
- [MCP Specification](https://modelcontextprotocol.io)

---

**Última actualización**: 2026-02-14  
**Versión**: 1.0.0
