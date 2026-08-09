# ADR-0001 — Backend Python y frontend TypeScript

## Estado

Aceptada.

## Contexto

El plan v2.0 original proponía TypeScript estricto para todo el sistema. Brenda decidió que el backend debe alinearse con Hermes, que ya es Python, y que TypeScript debe quedar limitado al frontend React/Tauri.

## Decisión

El cockpit se construye con:

- backend/control plane en Python;
- contratos backend con Pydantic;
- puertos hexagonales con `typing.Protocol`;
- event sourcing en SQLite desde Python;
- Quota Governor en Python;
- telemetría Python;
- frontend React/Tauri en TypeScript;
- CI local y GitHub Actions en repo privado.

## Consecuencias

- La carpeta `backend/` es el núcleo canónico de Fase 0.
- TypeScript queda para UI, shell Tauri y tipos generados si hacen falta.
- La implementación TypeScript previa se conserva temporalmente como referencia local hasta que Brenda apruebe su retirada del repo.
- No se avanza a Fase 1 hasta que el gate de Fase 0 pase con esta arquitectura.
