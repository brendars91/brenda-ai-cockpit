#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="${LOG_DIR:-${REPO_ROOT}/logs}"
MAX_DAYS="${MAX_DAYS:-14}"

if [ -d "${LOG_DIR}" ]; then
  find "${LOG_DIR}" -type f -mtime +"${MAX_DAYS}" -delete
fi

echo "Log cleanup completed (kept ${MAX_DAYS} days)."
