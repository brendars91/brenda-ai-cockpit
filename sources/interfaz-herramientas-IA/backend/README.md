# Cockpit Backend

Python control-plane backend for the Cockpit Unificado Multi-Agente.

This backend replaces the earlier TypeScript core direction. TypeScript remains for the React/Tauri frontend only.

Phase 0 responsibilities:

- versioned contracts with Pydantic
- hexagonal ports with Python Protocols
- SQLite append-only event log and deterministic replay
- Quota Governor for Z.AI, ChatGPT/Codex, and Claude subscription windows
- telemetry primitives with redaction
