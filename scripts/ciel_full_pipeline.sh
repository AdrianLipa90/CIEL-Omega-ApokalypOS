#!/usr/bin/env bash
# CIEL Full Pipeline Launcher (hardcoded, single command)
# Starts:
# - Codex -> CIEL raw_logs bridge (follow mode)
# - Memory consolidator (daemon)
# - Subconscious supervisor (daemon; keeps llama-server alive if configured)
# - Existing CIEL local runtime (pipeline + portal + GUI)
#
# Stop: Ctrl+C (kills spawned background processes).

set -euo pipefail

PROJECT="/home/adrian/Pulpit/CIEL_TESTY/CIEL1"
MEMORIES="$HOME/Pulpit/CIEL_memories"
LOG_DIR="$MEMORIES/logs"
mkdir -p "$LOG_DIR"

PY_CANDIDATES=(
  "/home/adrian/Pulpit/CIEL_TESTY/venv/bin/python3.12"
  "/home/adrian/Pulpit/CIEL_TESTY/venv/bin/python3"
  "python3"
)

PY="python3"
for p in "${PY_CANDIDATES[@]}"; do
  if command -v "$p" >/dev/null 2>&1; then
    PY="$p"
    break
  fi
done

export PYTHONPATH="$PROJECT/src:${PYTHONPATH:-}"

PIDS=()
cleanup() {
  for pid in "${PIDS[@]:-}"; do
    kill "$pid" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT INT TERM

echo "[full] starting codex bridge..."
"$PROJECT/scripts/ciel_codex_bridge.sh" >>"$LOG_DIR/codex_bridge.log" 2>&1 &
PIDS+=("$!")

echo "[full] starting memory consolidator..."
"$PY" "$PROJECT/scripts/ciel_memory_consolidator.py" --daemon --interval 300 >>"$LOG_DIR/memory_consolidator.log" 2>&1 &
PIDS+=("$!")

echo "[full] starting subconscious supervisor..."
"$PY" "$PROJECT/scripts/ciel_subconscious_supervisor.py" --interval 15 >>"$LOG_DIR/subconscious_supervisor.log" 2>&1 &
PIDS+=("$!")

echo "[full] starting runtime (pipeline + portal + GUI)..."
exec "$PROJECT/scripts/ciel_start.sh"

