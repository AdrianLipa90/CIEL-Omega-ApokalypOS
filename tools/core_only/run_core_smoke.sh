#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
ENGINE_DIR="${ROOT_DIR}/src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega"

source "${VENV_DIR}/bin/activate"
python -m pip install -e "${ENGINE_DIR}" >/dev/null
ciel-smoke
