# Migration Roadmap — Brenda AI Cockpit

## Fase 0 — Corte actual

- Fuentes saneadas importadas.
- Gates básicos creados.
- Arquitectura y spec documentadas.

## Fase 1 — Normalización

- Extraer piezas únicas de `interfaz-herramientas-IA`.
- Extraer piezas únicas de `Gem-Trinity-Genesis`.
- Extraer piezas únicas de `Creador-proyectos-compilador`.
- Extraer piezas únicas de `Generador-proyectos-determinista`.

## Fase 2 — Núcleo funcional

- Crear contratos mínimos para datos/comandos/eventos.
- Migrar lógica reutilizable a `packages/`.
- Crear una app shell en `apps/` con navegación y health check.

## Fase 3 — Verificación productiva

- Unit tests para paquetes.
- Contract tests para fronteras.
- Smoke e2e para flujos críticos.
- CI verde.

## Fase 4 — Borrado controlado

- Comparar funcionalidad original vs equivalente.
- Marcar repos como `deletable` solo con evidencia.
- Pedir `PROCEDER` literal antes de ejecutar `gh repo delete`.
