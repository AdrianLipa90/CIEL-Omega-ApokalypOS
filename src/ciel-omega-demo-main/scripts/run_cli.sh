#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="${VENV_DIR:-.venv}"

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "Missing venv: $VENV_DIR (run scripts/install_local.sh first)" >&2
  exit 1
fi

"$VENV_DIR/bin/ciel-cli" "$@"
