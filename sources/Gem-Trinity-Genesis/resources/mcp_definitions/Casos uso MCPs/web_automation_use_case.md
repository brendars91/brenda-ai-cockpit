# 🌐 MCPs de Automatización y Navegación Web

Herramientas que permiten a Antigravity interactuar con el internet "vivo": leer páginas, probar aplicaciones web y extraer datos.

## Herramientas Incluidas
1.  **fetch**: Descarga optimizada de contenido web (HTML -> Markdown). Rápido y ligero.
2.  **playwright**: Navegador completo (Headless Browser). Ejecuta JavaScript, permite clicks, llenado de formularios y pruebas E2E.

## 🎯 ¿Cuándo usar este conjunto?

### Caso 1: Documentación y Research
**Situación:** "Lee la documentación oficial de MCP y resúmeme los tipos de servidores."
**Selección:** `fetch`.
**Por qué:** Es rápido, eficiente y no necesita renderizar visualmente. Ideal para blogs, docs y artículos.

### Caso 2: Pruebas End-to-End (QA)
**Situación:** "Verifica que el botón de login funcione y redirija al dashboard."
**Selección:** `playwright`.
**Por qué:** Necesita interactuar con la UI, esperar cargas dinámicas y verificar cambios en el DOM que requieren JavaScript.

### Caso 3: Scraping de Sitios Dinámicos (SPA)
**Situación:** "Extrae los precios de este sitio de e-commerce (construido en React/Angular)."
**Selección:** `playwright`.
**Por qué:** `fetch` solo vería el HTML vacío de una SPA. `playwright` renderiza la app completa y extrae la información real.

## ⚠️ Consideraciones
- **Fetch:** Es la primera opción por velocidad.
- **Playwright:** Úsalo solo cuando sea necesario interactuar o renderizar JS complejo, ya que consume más recursos.
