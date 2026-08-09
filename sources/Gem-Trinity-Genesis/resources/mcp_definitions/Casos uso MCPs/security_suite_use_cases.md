# 🛡️ MCPs de Seguridad & Auditoría

Este conjunto de herramientas convierte a Antigravity en un auditor de seguridad experto (DevSecOps).

## Herramientas Incluidas
1.  **Snyk**: Análisis de vulnerabilidades en código (SAST) y dependencias.
2.  **Semgrep**: Búsqueda de patrones de código inseguro y secretos hardcodeados.
3.  **MCP-SBOM**: Generación y análisis de "Bill of Materials" (Inventario de software) de imágenes Docker.
4.  **OPA (Open Policy Agent)**: Validación de archivos de configuración (Terraform, K8s) contra políticas de seguridad.
5.  **Trivy**: Escaneo integral de contenedores, filesystem y repositorios remotos. Ideal para imágenes Docker y configs.

## 🎯 ¿Cuándo usar este conjunto?

### Caso 1: Auditoría de Seguridad de Nuevo Proyecto
**Situación:** Acabas de clonar un repo desconocido o vas a entregar un proyecto al cliente.
**Acción Agente:** "Analiza este repositorio en busca de vulnerabilidades críticas."
**Uso Técnico:**
- `snyk` escanea `package.json` / `requirements.txt` y código fuente.
- `semgrep` busca credenciales expuestas o funciones peligrosas (`eval()`, etc.).

### Caso 2: Validación de Infraestructura (IaC)
**Situación:** Tienes archivos Dockerfile, Kubernetes o Terraform.
**Acción Agente:** "Verifica que este Dockerfile siga las mejores prácticas."
**Uso Técnico:**
- `opa` valida el archivo contra reglas predefinidas (ej. no correr como root).
- `trivy` escanea la imagen Docker final en busca de vulnerabilidades de SO (`trivy scan_image`).
- `mcp-sbom` genera el inventario de la imagen para detectar paquetes del SO vulnerables.

### Caso 3: Refactorización Segura
**Situación:** Estás modificando código legacy.
**Acción Agente:** "Asegúrate de no introducir nuevas vulnerabilidades al cambiar esta función."
**Uso Técnico:** Ejecución continua de `semgrep` sobre los archivos modificados.

## ⚠️ Requisitos
- **Snyk:** Requiere autenticación (Token configurado).
- **Semgrep/OPA/SBOM:** Funcionan localmente (correctamente configurados en `settings.json`).
