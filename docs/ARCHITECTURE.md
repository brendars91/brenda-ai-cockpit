# Arquitectura — Brenda AI Cockpit

## Decisión de dominio

Brenda AI Cockpit sería el panel de mando canónico para controlar herramientas y agentes IA: registra capacidades, enruta tareas entre Hermes/Claude/Codex/Paperclip, aplica políticas de seguridad y cuotas, guarda contexto/eventos con trazabilidad y ofrece una UI operativa para ver qué agente hace qué, por qué y con qué evidencia.

## Principios

- Dominio separado: no mezclar responsabilidades con otros productos de Brenda.
- APIs server-side para cualquier credencial o proveedor IA.
- Contratos versionados para datos, eventos y comandos.
- Fuente original preservada bajo `sources/`, migración productiva bajo `apps/` y `packages/`.
- Gates deterministas antes de borrar repos fuente.

## Capas objetivo

1. Apps: experiencias finales del usuario/operador.
2. Packages: lógica compartida reutilizable y testeable.
3. Services/adapters: proveedores, runtimes y APIs externas.
4. Governance: decisiones de migración, borrado y privacidad.
5. Evidence: manifest de fuentes, checks, scans y smoke tests.

## Fronteras de seguridad

- Ningún token real en cliente o repo.
- Los archivos de entorno quedan sustituidos por ejemplos locales.
- Los repos originales con posible historial sensible se borran solo tras backup, rotación y gate explícito.
