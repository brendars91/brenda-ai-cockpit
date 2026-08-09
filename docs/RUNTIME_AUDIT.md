# Runtime audit — 2026-08-09

## Veredicto

**PARTIAL.** El repo canónico `brenda-ai-cockpit` funciona como contenedor auditado y `interfaz-herramientas-IA` compila como base principal del futuro cockpit. No es todavía un reemplazo productivo completo para todos los generadores históricos porque varias fuentes heredadas ya tenían errores Python y la suite TypeScript tiene módulos sin tests configurados.

## Evidencia ejecutada

Desde clon fresco de GitHub branch `initial/domain-consolidation`:

- `python3 tools/secret_scan.py .` → `secret_scan: PASS`
- `python3 tools/validate_repo.py` → `validate_repo: PASS (4 source imports)`
- `pnpm install --frozen-lockfile` en `sources/interfaz-herramientas-IA` → PASS
- `pnpm -r run build` en `sources/interfaz-herramientas-IA` → PASS; 16 workspaces compilados, Vite build generado.
- `pnpm -r run test` → PARTIAL/FAIL por módulos sin test files; no se observó una aserción funcional rota en el primer fallo, sino `No test files found` en paquetes configurados para exigir tests.
- `py_compile` sobre Python importado → 8 errores heredados, coincidentes con los repos originales.

## Hallazgos heredados

Los errores Python no fueron introducidos por la consolidación; existen también en los repos fuente:

- `Generador-proyectos-determinista/scripts/orchestrator.py`: `return outside function`
- `Generador-proyectos-determinista/scripts/gem_loader.py`: indentation error
- `Creador-proyectos-compilador/agcce/scripts/orchestrator.py`: `return outside function`
- `Creador-proyectos-compilador/agcce/scripts/gem_loader.py`: indentation error
- Copias equivalentes dentro de `Gem-Trinity-Genesis/modules/engine/`
- Plantillas con placeholders `{{CLASS_NAME}}` no son Python ejecutable directo.

## Implicación para borrado

- Borrables tras backup/conservación: `Generador-proyectos-determinista` y `Creador-proyectos-compilador`, porque su contenido está preservado y sus errores son heredados.
- No borrar todavía: `interfaz-herramientas-IA` y `Gem-Trinity-Genesis`; aún son fuentes de referencia principales hasta extraer, reparar y normalizar el control plane final.
