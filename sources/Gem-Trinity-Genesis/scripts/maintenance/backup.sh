#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_ROOT="${BACKUP_ROOT:-/home/ubuntu/backups/gem-trinity}"
STAMP="$(date -u +"%Y%m%d_%H%M%S")"
BACKUP_DIR="${BACKUP_ROOT}/${STAMP}"

mkdir -p "${BACKUP_DIR}"

tar -czf "${BACKUP_DIR}/artifacts.tar.gz" -C "${REPO_ROOT}" artifacts
tar -czf "${BACKUP_DIR}/logs.tar.gz" -C "${REPO_ROOT}" logs
tar -czf "${BACKUP_DIR}/config.tar.gz" -C "${REPO_ROOT}" config

if [ -f "${REPO_ROOT}/artifacts/state.sqlite" ]; then
  cp "${REPO_ROOT}/artifacts/state.sqlite" "${BACKUP_DIR}/state.sqlite"
fi

echo "Backup completed: ${BACKUP_DIR}"
