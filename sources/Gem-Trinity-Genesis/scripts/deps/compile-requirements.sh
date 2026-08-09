#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install pip-tools

python -m piptools compile requirements.in --output-file requirements.txt
python -m piptools compile requirements-dev.in --output-file requirements-dev.txt

echo "Dependencies compiled."
