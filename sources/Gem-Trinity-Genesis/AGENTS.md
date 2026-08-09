# AGENTS.md

## Mission & Scope
- You are an autonomous Staff+ agent maintaining Gem Trinity Genesis (FastAPI backend + Next.js frontend).
- Prioritize deterministic changes; mirror existing Spanish/English hybrid tone when touching UX copy.
- This document captures build, lint, test, and code-style rules agents must follow.
- Assume Python 3.10+ and Node 18+; do not downgrade toolchains.

## Repo Landmarks
- `local-watcher/`: FastAPI orchestration runtime, primary production target.
- `frontend/`: Next.js 14 App Router UI with Tailwind glassmorphism surface.
- `tests/`: root pytest suite referenced by `pyproject.toml` `testpaths`.
- `modules/`: mirrored agent packages (architect, builder, engine) with ad-hoc tooling.
- `resources/`: skills/MCP payloads consumed at runtime, treat as data not code.
- `docs/`, `DEPLOYMENT_*.md`, `RUNBOOK_PERSONAL.md`: operational knowledge, consult before altering infra.
- Avoid mutating `artifacts/`, `logs/`, `static/` and generated caches unless explicitly tasked.

## Environment Setup
- Create a local venv: `python -m venv .venv` then activate (`.venv\Scripts\Activate.ps1` on Windows).
- Install backend deps from repo root: `pip install -r requirements.txt`; add dev extras via `pip install -r requirements-dev.txt` when linting.
- Install Node deps inside `frontend/` with `npm install` (Next.js 14, React 18).
- Makefile helpers wrap the above via `make install` (prod deps) and `make install-dev` (adds pytest, black, isort, bandit, mypy, pre-commit).
- Copy `.env.example` when present or set `GOOGLE_API_KEY` manually (see README instructions around `local-watcher/.env`).

## Build & Run Commands
- Backend dev server: `python local-watcher/api_server.py` or `make run-backend` (runs uvicorn entrypoint directly).
- Frontend dev server: `cd frontend && npm run dev` or `make run-frontend`.
- Full-stack live dev: `make run-dev` (parallel backend + frontend; cancel with `Ctrl+C`).
- Production-ish backend build: `docker-compose up -d` (wrap with `make docker-up`); tear down with `make docker-down`.
- Rebuild containers when dependencies change: `make docker-build`.
- Frontend production build check: `cd frontend && npm run build && npm run start`.
- Run `pre-flight-check.sh` / `.ps1` before deployments to verify env vars and credentials (scripts live at repo root).

## Test Strategy & Single-Test Recipes
- Pytest defaults live in `pyproject.toml` (`-v --tb=short`, `testpaths = ["tests"]`). Root `python -m pytest` only operates on `tests/`.
- Backend package tests are under `local-watcher/tests`; point pytest explicitly or `cd local-watcher` first.
- Canonical suites:
  - All backend tests: `cd local-watcher && python -m pytest tests/ -v` (same as `make test`).
  - Unit subset: `cd local-watcher && python -m pytest tests/unit -v` (same as `make test-unit`).
  - Integration subset: `cd local-watcher && python -m pytest tests/integration -v` (same as `make test-integration`).
  - Coverage run: `make test-cov` (HTML output at `local-watcher/htmlcov/index.html`).
- Run a single backend test case via node id: `cd local-watcher && python -m pytest tests/unit/test_circuit_breaker.py::test_half_open_reset`.
- Keyword filtering example: `python -m pytest local-watcher/tests -k "semantic_cache and throttle"`.
- Root tests single case: `python -m pytest tests/test_api_contract.py::test_transparency_endpoint`.
- No dedicated JS test runner exists; ESLint is the only enforced frontend check (`npm run lint`).
- Keep new backend tests deterministic; avoid live network calls unless guarded with feature flags or recorded fixtures.
- Module-level tests under `modules/**/tests` are excluded from default discovery; run them explicitly when editing those modules.

## Tooling Shortcuts
- `make lint` executes Black (check), isort (check-only), and Bandit over `local-watcher/`.
- `make lint-py` adds mypy (`--ignore-missing-imports`); fix typing warnings locally.
- `make lint-ts` wraps `cd frontend && npm run lint` (Next core web vitals ruleset).
- Formatting helpers: `make format` (Black + isort) or scope-limited `make format-py` / `make format-ts` (the TS variant runs ESLint `--fix`).
- `make clean` purges pyc caches and coverage output; `make clean-all` additionally removes `.venv`, `node_modules`, and `.next`.
- Use `scripts/` for automation (e.g., `scripts/sync_skills.py`); inspect before execution.

## Code Style – General
- Default encoding ASCII; introduce Unicode only if the target file already mixes locales (common in README/UI copy).
- Keep commits focused; mention why the change matters when summarizing.
- Follow deterministic-first philosophy: prefer explicit state transitions over implicit magic.
- Log intent and context, not secrets, using `structured_logger.ContextLogger` helpers.
- Respect repo docs ordering (README in Spanish first, then English) when updating instructions.

## Python Backend Guidelines
- Formatting: Black settings from `pyproject.toml` (line length 100, target py310); always run isort with profile `black`.
- Module imports order: stdlib, third-party, local; avoid wildcard imports and prefer explicit symbols.
- Type hints: encouraged everywhere; `local-watcher` tolerates untyped defs but new code should include annotations and `typing.Optional`/`Path` where relevant.
- Models: define Pydantic `BaseModel` classes in `local-watcher/api_models.py` or nearby modules; maintain existing snake vs camel casing (see `SkillOrchestrationRequest.useCase`).
- Errors: raise the custom hierarchy in `local-watcher/error_handler.py` (`AppError`, `ValidationError`, `NotFoundError`, `RateLimitError`, `ExternalServiceError`) so FastAPI hooks format responses consistently.
- HTTP responses: use FastAPI `HTTPException` only for direct status/detail combos; otherwise raise `AppError` subclasses and let `register_error_handlers` serialize them.
- Logging: import `get_logger` or the pre-configured `api_logger`, `architect_logger`, etc., from `structured_logger.py` to emit JSON payloads with `extra_data` dictionaries.
- Async safety: API routers are `async`—move blocking code into background tasks or thread executors; never call external services synchronously inside event loop.
- Filesystem: rely on `pathlib.Path` joined to repo root; avoid hard-coded absolute Windows paths.
- External services: wrap Gemini/LLM calls through `llm_provider.py` or service abstractions so rate limiting, caching, and auditing stay centralized.
- Tests: prefer `local-watcher/tests/unit` for logic, keep e2e harnesses under `local-watcher/test_*.py` gated or skipped unless necessary.
- Naming: modules snake_case, classes PascalCase, coroutine functions snake_case (no camel), constants UPPER_SNAKE_CASE.

## Frontend (Next.js 14) Guidelines
- All interactive components live under `frontend/app`; mark client components with `"use client"` at the top just like `app/page.tsx`.
- TypeScript config is strict with `noUncheckedIndexedAccess` and `noImplicitOverride`; keep new code type-safe and avoid `any` unless narrowing is impossible.
- Prefer `interface` for props/objects, `type` for discriminated unions, and `enum` sparingly.
- Imports: use the `@/` alias for cross-app references and relative paths for siblings; group React first, third-party next, internal last.
- Formatting: 4-space indentation, single quotes for strings (Next CLI also accepts double quotes but repo standard uses single), semicolons on every statement.
- State: lean on React hooks; avoid class components; co-locate data fetching hooks in `frontend/app/hooks` (see `useSystemMetrics`).
- Network access: always reference `process.env.NEXT_PUBLIC_API_URL` (default `http://localhost:8000`) and gate UI messages on `res.ok`.
- Error/UI copy: replicate the cinematic neon/glass aesthetic; keep interactive copy in English uppercase labels (e.g., `INITIALIZE AGENTS`).
- Accessibility: maintain responsive classes as seen in `frontend/app/page.tsx` (use `sm:`/`lg:` breakpoints) and ensure buttons have discernible text.
- ESLint: `npm run lint` enforces `next/core-web-vitals`; fix a11y warnings rather than disabling rules.

## Tailwind & Visual System
- Tailwind config lives at `frontend/tailwind.config.ts`; fonts are CSS variables `--font-inter` and `--font-outfit` (via `fontFamily.sans` and `.heading`).
- Reuse existing background utilities such as `animate-pulse-glow`, glass panels, and neon gradients defined inside `frontend/app/globals.css`.
- Add animations via Tailwind `extend.animation`/`keyframes` blocks, not inline CSS; keep durations calm (2–4s) to suit the ambient dashboard style.
- Favor utility composition over custom CSS unless a rule is reused across multiple components.

## Security, Secrets, and Env Vars
- Required env vars: `GOOGLE_API_KEY` (backend, referenced as `GEMINI_API_KEY` inside README), `PORT`, optional `LOG_LEVEL`, `CORS_ORIGINS`, plus `NEXT_PUBLIC_API_URL` for the frontend.
- Never log secrets; scrub payloads before passing to `structured_logger` or returning from FastAPI routers.
- `.env` files stay local; do not commit keys to git or docs.
- Cloud deploys rely on `deploy-to-oci.*` scripts and Cloudflare tunnel instructions in `CLOUDFLARE_TUNNEL_SETUP.md`; review before altering pipelines.

## Observability & Ops
- Every agent execution is mirrored by `local-watcher/agent_transparency.py`; keep JSON contracts stable because the frontend dashboards expect fields like `workflowStep` and `metrics_history`.
- `structured_logger.py` emits JSON logs; prefer `logger.with_context(request_id=...)` to stitch traces across services.
- Rate limiting + resilience live in `circuit_breaker.py`, `rate_limiter.py`, and `error_tracker.py`; reuse these utilities when adding new external integrations.
- Metrics endpoints sit under `local-watcher/routers/metrics.py` and `health_checks.py`; update both when altering health semantics.
- Background tasks that touch files should drop breadcrumbs into `logs/` only through the structured logger to keep Cloudflare tunnel tails clean.

## Deployment Checklist
- Verify deps via `make install-dev && make lint && make test` prior to packaging images.
- OCI deployment uses `deploy-to-oci.sh` / `.ps1`; read `DEPLOYMENT_README.md` for VM expectations (Ubuntu + Docker) and `DEPLOYMENT_SUMMARY.md` for recent runbooks.
- Heroku-style deployment is available via `Procfile` + `runtime.txt` if you target platforms that honor them (gunicorn/uvicorn command defined in file).
- Frontend ships separately on Vercel; update `.vercel/project.json` if you introduce new env vars (currently expect `NEXT_PUBLIC_API_URL`).
- Cloudflare tunnel (see `CLOUDFLARE_TUNNEL_SETUP.md`) must point at whatever port FastAPI binds to; keep `PORT` default 8000 for local parity.
- GitHub Actions live under `.github/workflows`; adjust build steps there when adding new lint/test requirements.

## Troubleshooting & Tips
- Use `pre-flight-check.sh` (or `.ps1`) before demos to confirm env vars, network ports, and dependency versions.
- If FastAPI fails to boot, inspect `logs/api.log` (if configured) or run `python local-watcher/api_server.py --log-level debug` for verbose traces.
- When Dockerized services misbehave, run `make docker-logs` for aggregated output or `docker-compose logs -f <service>` for a single container.
- Tailwind cache glitches? Delete `frontend/.next` and rerun `npm run dev`.
- Pytest hanging on e2e suites? Many `local-watcher/test_*.py` files hit live APIs; skip them by running `pytest -k "not test_e2e"` unless intentionally verifying integrations.
- Modules sync scripts (`local-watcher/mirror_sync*.py`, `git_sync.py`) assume GitHub credentials; dry-run them in staging first.

## Git & Review Workflow
- Always inspect `git status` before editing; this workspace may already contain untracked experiments from other agents.
- Keep changes scoped; if you touch both backend and frontend, document the relationship inside PR descriptions or commit messages.
- Follow the repo's preference for conventional, descriptive commit headers (see `git log` for examples) and never commit secrets or `.env` files.
- Tests and linters must pass locally before asking for review; reference the exact `make`/`pytest` command you ran in PR descriptions.
- Avoid `git reset --hard` or force pushes unless the user explicitly asks—preserve other contributors' work.

## Data & Storage Notes
- Runtime state stores live under `local-watcher/state_store.py`, `semantic_cache.py`, and SQLite/json files referenced therein; treat them as append-only unless fixing corruption.
- Skill payloads under `resources/skills/` are often copied verbatim into LLM prompts; keep formatting intact and avoid trailing whitespace changes.
- When adding large assets, prefer storing them in `resources/` and referencing via config instead of embedding base64 blobs in code.
- File watchers and syncers expect relative paths; keep new directories lowercase snake_case.

## Additional References
- Architecture digests live under `docs/architecture/`; skim `OPTIMIZATION_GUIDE.md` for performance levers before heavy refactors.
- Verification playbooks are inside `docs/verification/`; align new evaluation steps with those checklists.
- `FRONTEND_UPDATE.md` explains recent UI direction; keep major layout changes consistent with that narrative.
- `RUNBOOK_PERSONAL.md` contains live-service fire drills—read before modifying monitoring logic.
- Use `EXECUTION_PLAN.md` when coordinating multi-agent stories; update it if you change system flows.

## Final Reminders
- Respect the Explore → Plan → Execute → Verify rhythm outlined in CLAUDE.md before shipping non-trivial changes.
- Prefer additive edits over rewrites; preserve TODO markers and inline comments that capture historical context.
- Before leaving the repo, reset dev servers, stop tunnels, and clean temp files with `make clean` to keep the workspace lightweight.

## Cursor/Copilot Rules
- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` files exist; there are currently no external assistant guardrails beyond this AGENTS.md.
