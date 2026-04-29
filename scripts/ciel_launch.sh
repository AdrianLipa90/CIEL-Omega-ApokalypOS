#!/usr/bin/env bash
# CIEL full-stack launcher — starts GUI + subconsciousness, opens browser

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="$(dirname "$SCRIPT_DIR")"
VENV="$(dirname "$PROJECT")/venv"
PORT=5050
URL="http://localhost:${PORT}/portal"
LOG="/tmp/ciel_gui.log"

# 1. Check if already running
if curl -s --max-time 1 "http://localhost:${PORT}/" > /dev/null 2>&1; then
  echo "[CIEL] GUI already running on :${PORT}"
  xdg-open "$URL" 2>/dev/null &
  exit 0
fi

# 2. Start Flask GUI in background
echo "[CIEL] Starting GUI on :${PORT}..."
cd "$PROJECT"
nohup "$VENV/bin/ciel-sot-gui" --host 127.0.0.1 --port "$PORT" > "$LOG" 2>&1 &
GUI_PID=$!
echo "[CIEL] GUI PID=$GUI_PID"

# 3. Wait for it to be up (max 15s)
for i in $(seq 1 30); do
  sleep 0.5
  if curl -s --max-time 1 "http://localhost:${PORT}/" > /dev/null 2>&1; then
    echo "[CIEL] GUI ready after ${i} tries"
    break
  fi
done

# 4. Start subconsciousness daemon if not running
if ! python3 -c "import socket; s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.settimeout(0.5); s.connect('/tmp/ciel_subconscious.sock'); s.close()" 2>/dev/null; then
  echo "[CIEL] Starting subconscious daemon..."
  rm -f /tmp/ciel_subconscious.sock
  nohup "$VENV/bin/python3" "$PROJECT/scripts/ciel_subconscious.py" --daemon >> "$LOG" 2>&1 &
else
  echo "[CIEL] Subconscious daemon already running"
fi

# 5. Open browser
xdg-open "$URL" 2>/dev/null &

echo "[CIEL] Launched → $URL"
echo "[CIEL] Log: $LOG"
