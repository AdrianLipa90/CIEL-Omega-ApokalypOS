#!/usr/bin/env bash
set -euo pipefail

VENV_DIR="${VENV_DIR:-.venv}"
HOST="${CIEL_HOST:-127.0.0.1}"
PORT="${CIEL_PORT:-8080}"

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "Missing venv: $VENV_DIR (run scripts/install_local.sh first)" >&2
  exit 1
fi

CIEL_HOST="$HOST" CIEL_PORT="$PORT" "$VENV_DIR/bin/ciel-omega"
