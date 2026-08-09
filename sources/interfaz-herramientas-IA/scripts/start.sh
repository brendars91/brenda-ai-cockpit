#!/usr/bin/env bash
# Cockpit launcher: starts backend API + frontend dev server
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$ROOT/backend"

echo "🚀 Starting Cockpit backend (FastAPI on :8000)..."
cd "$BACKEND_DIR"
uv run python run.py &
BACKEND_PID=$!

cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill "$BACKEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "🚀 Starting Cockpit frontend (Vite on :1420)..."
cd "$ROOT/cockpit"
pnpm dev &
FRONTEND_PID=$!

echo ""
echo "✅ Cockpit running:"
echo "   API:       http://127.0.0.1:8000/api/health"
echo "   Frontend:  http://127.0.0.1:1420"
echo "   WebSocket: ws://127.0.0.1:8000/api/ws/events"
echo ""
echo "Press Ctrl+C to stop."

wait
