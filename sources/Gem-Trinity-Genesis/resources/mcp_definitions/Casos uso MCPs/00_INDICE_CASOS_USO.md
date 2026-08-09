# 🧭 Directorio de Casos de Uso MCP

Este directorio contiene guías prácticas para seleccionar los **Model Context Protocol (MCP)** servers adecuados para tu proyecto actual.

## ¿Cómo usar esto?

1.  **Define tu Objetivo**: ¿Qué quieres construir? (Web App, Auditoría, Automatización, Agente autónomo).
2.  **Consulta esta Tabla**: Busca la categoría que mejor encaje.
3.  **Activa los MCPs**: Asegúrate de que los MCPs listados estén habilitados en tu configuración.

## 🚀 Guía Rápida de Selección

| Tipo de Proyecto | MCPs Esenciales | MCPs Complementarios | Archivo de Detalle |
| :--- | :--- | :--- | :--- |
| **Desarrollo Web (Frontend/Backend)** | `filesystem`, `github`, `smart-coding-mcp` | `fetch`, `playwright` | [Desarrollo General](./smart_coding_use_case.md) |
| **Auditoría de Seguridad & DevSecOps** | `snyk`, `semgrep`, `trivy`, `opa` | `github`, `filesystem`, `mcp-sbom` | [Seguridad Integral](./security_suite_use_cases.md) |
| **Automatización de Flujos (Workflows)** | `n8n-native`, `n8n-mcp` | `fetch`, `google-calendar`* | [Automatización n8n](./n8n_use_case.md) |
| **Investigación & Navegación Web** | `fetch`, `playwright` | `context7` | [Navegación Web](./web_automation_use_case.md) |
| **Productividad & Gestión** | `atlassian`, `notion` | `google-*`, `slack` | [Productividad](./productivity_use_case.md) |
| **Razonamiento Complejo / Arquitectura** | `sequential-thinking` | `context7` | [Razonamiento](./cognitive_use_case.md) |

> (*) *Nota: Las herramientas de productividad (Google/Slack/Atlassian) suelen mantenerse desactivadas por defecto para optimizar recursos. El agente debe solicitar su activación explícita leyendo el archivo [Productividad](./productivity_use_case.md) cuando el usuario requiera gestión de proyectos o integración con herramientas de oficina.*

## 📂 Archivos de Detalle
Revisa los archivos individuales en esta carpeta para entender a profundidad qué capacidades aporta cada herramienta.
