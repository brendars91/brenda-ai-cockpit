# Product Spec — Brenda AI Cockpit

## Objetivo

Crear un repositorio canónico de nivel producción para este dominio, aprovechando lo mejor de las fuentes ya existentes sin arrastrar deuda accidental.

## Resultado esperado

Brenda AI Cockpit sería el panel de mando canónico para controlar herramientas y agentes IA: registra capacidades, enruta tareas entre Hermes/Claude/Codex/Paperclip, aplica políticas de seguridad y cuotas, guarda contexto/eventos con trazabilidad y ofrece una UI operativa para ver qué agente hace qué, por qué y con qué evidencia.

## Capacidades nucleares

- Contracts
- Policy
- Context Fabric
- Capability Registry
- Quota Governor
- Telemetry
- Adapters

## No objetivos del primer corte

- No reescribir toda la app en un único commit.
- No publicar credenciales ni historiales sensibles.
- No borrar repos fuente sin equivalente verificado.

## Definition of Done productivo

- Build reproducible.
- Tests unitarios y contractuales.
- Smoke e2e mínimo.
- Secret scan limpio.
- README visible y honesto.
- Roadmap de migración por PRs pequeños.
