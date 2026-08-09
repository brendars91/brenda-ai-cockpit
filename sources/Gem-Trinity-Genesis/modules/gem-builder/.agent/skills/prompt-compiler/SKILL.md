---
name: prompt-compiler
description: Compilador modular de System Prompts versionados para Gem Bundles. Genera prompts deterministas con variables, hash SHA-256 y políticas anti-alucinación integradas.
---

# Prompt Compiler (Gem Builder Edition)

## Propósito

Generar **System Prompts versionados y verificables** para Gem Bundles, asegurando:
- Políticas anti-alucinación integradas
- Variables parametrizables
- Hash para verificación de integridad
- Modularidad y reutilización

## Inputs

1. **Use Case Spec** (validado)
2. **Capability Selection** (del capability-router)
3. **Template Library** (opcional)

## Proceso de Compilación

### 1. Selección de Base Template

Seleccionar plantilla según tipo de Gem:
- `templates/analytical.prompt` → Para análisis, extracción, clasificación
- `templates/generative.prompt` → Para creación de contenido
- `templates/agentic.prompt` → Para agentes con tool-calling
- `templates/custom.prompt` → Para casos específicos

### 2. Inyección de Variables

Variables estándar:
- `{{USE_CASE_ID}}` → ID del caso de uso
- `{{ALLOWED_TOOLS}}` → Lista de tools permitidas
- `{{GROUNDING_STRATEGY}}` → none|google_search|rag|url_context
- `{{KNOWLEDGE_STATES}}` → HECHO_VERIFICADO, INFERENCIA, ASUNCION, FALTAN_DATOS

### 3. Políticas Anti-Alucinación

Inyectar automáticamente:
```
## PROTOCOLO ANTI-ALUCINACIÓN (INVIOLABLE)

1. Estado de conocimiento obligatorio:
   - HECHO_VERIFICADO: Datos con source citada
   - INFERENCIA: Deducciones lógicas marcadas explícitamente
   - ASUNCION: Supuestos declarados como tales
   - FALTAN_DATOS: Admitir ignorancia cuando aplique

2. Prohibición de entidades fantasma:
   - NO inventar funciones, APIs, herramientas que no existan
   - NO citar fuentes inexistentes
   - NO crear datos ficticios

3. Grounding obligatorio:
   - Estrategia: {{GROUNDING_STRATEGY}}
   - Fuentes permitidas: {{ALLOWED_SOURCES}}
```

### 4. Hash y Versionado

```python
import hashlib

def compile_prompt(template: str, variables: dict) -> dict:
    # Reemplazar variables
    compiled = template
    for key, value in variables.items():
        compiled = compiled.replace(f"{{{{{key}}}}}", value)
    
    # Generar hash
    hash_sha256 = hashlib.sha256(compiled.encode()).hexdigest()
    
    return {
        "text": compiled,
        "version": "1.0.0",  # SemVer
        "hash": hash_sha256,
        "variables": list(variables.keys())
    }
```

## Output (JSON Fragment)

```json
{
  "system_prompt": {
    "text": "Eres un agente especializado en...",
    "version": "1.0.0",
    "hash": "a3f2b8c9d1e4f5...",
    "variables": ["USE_CASE_ID", "ALLOWED_TOOLS"]
  }
}
```

## Templates Disponibles

Ver carpeta `templates/prompts/` para plantillas predefinidas.
