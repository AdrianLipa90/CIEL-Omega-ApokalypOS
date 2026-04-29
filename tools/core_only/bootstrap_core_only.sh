#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
ENGINE_DIR="${ROOT_DIR}/src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega"

if [[ ! -d "${VENV_DIR}" ]]; then
  python3 -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e "${ENGINE_DIR}"
python -m pip install pytest PyYAML

echo "[core-only] bootstrap complete"
