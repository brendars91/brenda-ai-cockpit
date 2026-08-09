#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <backup-dir>"
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_DIR="$1"

if [ ! -d "${BACKUP_DIR}" ]; then
  echo "Backup directory not found: ${BACKUP_DIR}"
  exit 1
fi

tar -xzf "${BACKUP_DIR}/artifacts.tar.gz" -C "${REPO_ROOT}"
tar -xzf "${BACKUP_DIR}/logs.tar.gz" -C "${REPO_ROOT}"
tar -xzf "${BACKUP_DIR}/config.tar.gz" -C "${REPO_ROOT}"

if [ -f "${BACKUP_DIR}/state.sqlite" ]; then
  cp "${BACKUP_DIR}/state.sqlite" "${REPO_ROOT}/artifacts/state.sqlite"
fi

echo "Restore completed from: ${BACKUP_DIR}"
