#!/usr/bin/env bash
set -euo pipefail

BIN="/home/adrian/Pulpit/CIEL_TESTY/CIEL1/app/src-tauri/target/release/ciel-omega"
BACKEND_PY="/home/adrian/Pulpit/CIEL_TESTY/venv/bin/python3.12"
BACKEND_ROOT="/home/adrian/Pulpit/CIEL_TESTY/CIEL1"
BACKEND_URL="http://127.0.0.1:2435"
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

ensure_backend_2435() {
  if curl -sf --max-time 2 "$BACKEND_URL/api/status" >/dev/null 2>&1; then
    echo "[launch] backend already healthy on ${BACKEND_URL}" >>"$LOG"
    return 0
  fi
  if [[ -x "$BACKEND_PY" ]]; then
    echo "[launch] starting fallback backend on 2435" >>"$LOG"
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="$BACKEND_ROOT/src:${PYTHONPATH:-}" \
    CIEL_API_URL="$BACKEND_URL" \
    "$BACKEND_PY" -m ciel_sot_agent.gui.app --host 127.0.0.1 --port 2435 --root "$BACKEND_ROOT" >>"$LOG" 2>&1 &
    local backend_pid=$!
    sleep 2
    if curl -sf --max-time 2 "$BACKEND_URL/api/status" >/dev/null 2>&1; then
      echo "[launch] fallback backend is healthy" >>"$LOG"
      return 0
    fi
    echo "[launch] fallback backend did not answer yet (pid=${backend_pid})" >>"$LOG"
    return 1
  fi
  echo "[launch] backend python not found at ${BACKEND_PY}" >>"$LOG"
  return 1
}

fallback_web_gui() {
  if command -v xdg-open >/dev/null 2>&1; then
    echo "[launch] opening fallback web GUI: ${BACKEND_URL}" >>"$LOG"
    xdg-open "$BACKEND_URL" >/dev/null 2>&1 &
  else
    echo "[launch] xdg-open not available; web fallback URL=${BACKEND_URL}" >>"$LOG"
  fi
}

echo "[launch] trying native Tauri binary" >>"$LOG"
setsid "$BIN" >>"$LOG" 2>&1 &
native_pid=$!

sleep 3
if curl -sf --max-time 2 "$BACKEND_URL/api/status" >/dev/null 2>&1; then
  echo "[launch] native launch succeeded; backend is healthy" >>"$LOG"
  exit 0
fi

if ! kill -0 "$native_pid" 2>/dev/null; then
  echo "[launch] native process exited early during startup" >>"$LOG"
  ensure_backend_2435 || true
  fallback_web_gui
  exit 0
fi

echo "[launch] native backend not healthy after startup window; falling back" >>"$LOG"
if ! ensure_backend_2435; then
  echo "[launch] backend fallback failed" >>"$LOG"
fi
fallback_web_gui

exit 0
