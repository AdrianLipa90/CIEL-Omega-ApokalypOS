#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

source "${VENV_DIR}/bin/activate"
python -m pip install PyYAML pytest

echo "[core-only] repo test dependencies installed"
