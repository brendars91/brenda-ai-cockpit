# Brenda AI Cockpit

Control plane avanzado para agentes, context fabric, policy, adapters y ejecución determinista.

## Qué haría

Brenda AI Cockpit sería el panel de mando canónico para controlar herramientas y agentes IA: registra capacidades, enruta tareas entre Hermes/Claude/Codex/Paperclip, aplica políticas de seguridad y cuotas, guarda contexto/eventos con trazabilidad y ofrece una UI operativa para ver qué agente hace qué, por qué y con qué evidencia.

## Fuentes integradas

- `interfaz-herramientas-IA`
- `Gem-Trinity-Genesis`
- `Creador-proyectos-compilador`
- `Generador-proyectos-determinista`

## Apps objetivo

- `apps/cockpit-ui`
- `apps/control-plane-api`
- `apps/agent-runtime-console`

## Paquetes objetivo

- `packages/contracts`
- `packages/policy`
- `packages/context-fabric`
- `packages/capability-registry`
- `packages/quota-governor`
- `packages/telemetry`
- `packages/adapters`

## Estado actual

Este repo es un corte inicial canónico: fuentes saneadas, documentación de arquitectura, roadmap de migración, gates deterministas y escaneo de secretos. No afirma que las apps ya estén reimplementadas como producto único; conserva las piezas útiles y fija el camino de producción.

## Verificación

```bash
python3 tools/secret_scan.py .
python3 tools/validate_repo.py
```
