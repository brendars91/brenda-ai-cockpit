# Creador de Proyectos Compilador (Gem Ecosystem)

Este repositorio contiene el **Ecosistema Completo de Factoría de Agentes**, diseñado para producir software de IA determinista, seguro y de alta calidad.

## 🏛️ Estructura del Ecosistema

El flujo de trabajo sigue una arquitectura de tres niveles, donde cada componente alimenta al siguiente con creciente precisión:

### 1. `gem-architect` (El Arquitecto)
**Rol:** Diseño y Especificación.
- **Función:** Transforma ideas vagas en especificaciones técnicas rigurosas (Use Case Specs).
- **Core:** Un agente "Trinity" (Optimizador + PRD + Spec Architect) que produce el input JSON perfecto.
- **Output:** `use_case_spec.json`.

### 2. `gem-builder` (El Constructor)
**Rol:** Compilación y Validación.
- **Función:** Toma el `use_case_spec.json` y compila un "Gem Bundle" (el software del agente).
- **Características:**
    - Pipeline de 6 fases (Risk Engine, Router, Verifier Gate...).
    - Validación automática de Esquemas.
    - Smoke Tests integrados.
- **Output:** `gem_bundle.json` (Artifact compilado).

### 3. `agcce` (Agente Copilot Engine - El Motor)
**Rol:** Runtime y Ejecución.
- **Función:** El entorno donde vive y respira el agente compilado.
- **Características:**
    - Motor de ejecución determinista.
    - Manejo seguro de MCPs con Whitelists.
    - Observabilidad y trazas.
- **Input:** Ejecuta el `gem_bundle.json`.

---

## 🚀 Cómo Clonar y Usar

### Prerrequisitos
- Git
- Python 3.10+
- Node.js (para MCPs)

### Clonación
```bash
git clone https://github.com/brendars91/Creador-proyectos-compilador.git
cd Creador-proyectos-compilador
```

### Estructura de Carpetas
```text
C:\Users\ASUS\.gemini\
├── Miss carpetas\
│   ├── Gem Architect\      # (Diseño)
│   └── Gem Builder\        # (Compilación)
└── Agente Copilot Engine\  # (Ejecución - AGCce)
```

### Flujo de Trabajo Típico
1.  **Diseñar:** Interactúa con `Gem Architect` para definir tu agente.
2.  **Compilar:** Usa `gem-builder` CLI:
    ```bash
    python cli.py compile --spec tu_spec.json
    ```
3.  **Ejecutar:** Despliega el bundle resultante en `Agente Copilot Engine`.

---
*Propiedad Privada - Confidencial*
