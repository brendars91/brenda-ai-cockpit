# 🧠 MCPs de Habilidades Cognitivas

Herramientas abstractas que mejoran la capacidad de razonamiento y acceso a conocimiento externo de Antigravity.

## Herramientas Incluidas
1.  **sequential-thinking**: Permite un proceso de pensamiento paso a paso, con revisión de hipótesis y corrección de errores (Cadena de Pensamiento Dinámica).
2.  **context7**: Base de conocimientos externa sobre librerías y frameworks técnicos.

## 🎯 ¿Cuándo usar este conjunto?

### Caso 1: Resolución de Problemas Complejos (Debugging)
**Situación:** "El servidor se cae aleatoriamente y los logs no son claros. Investiga la causa raíz."
**Uso:**
- `sequential-thinking`: Descompone el problema:
  1. Hipótesis: Fuga de memoria.
  2. Verificación: Revisar métricas.
  3. Revisión: No es memoria, es timeout de DB.
  4. Conclusión.
- Ayuda a evitar conclusiones precipitadas.

### Caso 2: Uso de Librerías Desconocidas
**Situación:** "Implementa autenticación usando la librería 'Supabase Auth' (que no conoces a fondo)."
**Uso:**
- `context7`: Busca la documentación actual y ejemplos de código de 'Supabase Auth' para asegurar que la implementación siga las prácticas recomendadas más recientes, evitando alucinaciones sobre APIs inexistentes.

### Caso 3: Planificación de Arquitectura
**Situación:** "Diseña la arquitectura de microservicios para este sistema."
**Uso:** `sequential-thinking` para evaluar trade-offs, escalabilidad y dependencias antes de escribir una sola línea de código.

## 💡 Impacto
Activa estas herramientas cuando la tarea requiera **pensar antes de actuar** o **conocimiento especializado externo**.
