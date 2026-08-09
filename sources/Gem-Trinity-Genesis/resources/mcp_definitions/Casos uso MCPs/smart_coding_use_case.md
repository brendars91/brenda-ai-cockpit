# 💻 MCPs de Desarrollo de Software

El núcleo del trabajo de Antigravity como Ingeniero de Software. Estas herramientas son **obligatorias** para cualquier tarea de codificación.

## Herramientas Incluidas
1.  **filesystem**: Acceso de lectura/escritura a tus archivos locales.
2.  **github**: Gestión de repositorios, Pull Requests, Issues y búsquedas en código remoto.
3.  **smart-coding-mcp**: Análisis semántico del código ("Entiende" el proyecto, no solo lee texto).

## 🎯 ¿Cuándo usar este conjunto?

### Caso 1: Desarrollo de Nuevas Features
**Situación:** "Agrega un botón de login en la página de inicio."
**Uso Combinado:**
1.  `smart-coding-mcp`: Busca dónde está el componente de "página de inicio" y si ya existe lógica de login (`search_code_by_semantics`).
2.  `filesystem`: Lee los archivos identificados y aplica la edición.
3.  `smart-coding-mcp`: Re-indexa para actualizar su "mapa mental" del código.

### Caso 2: Onboarding en Proyecto Nuevo
**Situación:** "Explícame cómo funciona la autenticación en este proyecto que acabo de bajar."
**Uso Combinado:**
1.  `filesystem`: Lista la estructura de directorios.
2.  `smart-coding-mcp`: Indexa el código y permite preguntar "¿Cómo se gestionan los tokens JWT?" obteniendo respuestas basadas en el código real.

### Caso 3: Gestión de Versiones (GitOps)
**Situación:** "Sube estos cambios a una nueve rama llamada 'feat/login' y crea un PR."
**Uso Combinado:**
1.  `github`: Crea la rama, hace commit de los cambios (preparados en filesystem) y abre el Pull Request con descripción automática.

## 💡 Consejo Pro
Siempre que preguntes "dónde está X cosa" o "cómo funciona Y", Antigravity usará internamente **Smart Coding** para darte una respuesta precisa en lugar de adivinar. ¡Mantenlo activo!
