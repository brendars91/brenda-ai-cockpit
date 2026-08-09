#!/usr/bin/env bash
set -euo pipefail

KEEP_HOURS="${KEEP_HOURS:-168}"

docker system prune -af --filter "until=${KEEP_HOURS}h"
docker volume prune -f --filter "until=${KEEP_HOURS}h"

echo "Docker prune completed (kept last ${KEEP_HOURS}h)."
