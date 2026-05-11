#!/usr/bin/env bash
set -euo pipefail

BIN="/home/adrian/Pulpit/CIEL_TESTY/CIEL1/app/src-tauri/target/release/ciel-omega"
LOG="/home/adrian/Pulpit/CIEL_memories/logs/tauri_gui.log"

mkdir -p "$(dirname "$LOG")"

# Prefer the project's venv if available; Tauri backend spawn also supports CIEL_PY override.
if [[ -x "/home/adrian/Pulpit/CIEL_TESTY/venv/bin/python3.12" ]]; then
  export CIEL_PY="/home/adrian/Pulpit/CIEL_TESTY/venv/bin/python3.12"
elif [[ -x "/home/adrian/Pulpit/CIEL_TESTY/venv/bin/python3" ]]; then
  export CIEL_PY="/home/adrian/Pulpit/CIEL_TESTY/venv/bin/python3"
fi

{
  echo ""
  echo "===== $(date -Iseconds) launch_ciel_omega ====="
  echo "CIEL_PY=${CIEL_PY:-}"
  echo "CIEL_API_URL=${CIEL_API_URL:-}"
  echo "DISPLAY=${DISPLAY:-}"
} >>"$LOG"

exec "$BIN" >>"$LOG" 2>&1

