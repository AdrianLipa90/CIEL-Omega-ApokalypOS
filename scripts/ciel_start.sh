#!/bin/bash
# CIEL Local Launcher
# Uruchamia: pipeline, portal, GUI, TinyLlama podświadomość

PY="/home/adrian/Pulpit/CIEL_TESTY/venv/bin/python3.12"
PROJECT="/home/adrian/Pulpit/CIEL_TESTY/CIEL1"
export PYTHONPATH="$PROJECT/src:$PYTHONPATH"
LOG_DIR="$PROJECT/integration/logs"
mkdir -p "$LOG_DIR"

PORTAL_PORT=7481
GUI_PORT=5050
LLAMA_PORT=18520

MODEL_TINY="$HOME/.local/share/ciel/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
LLAMA_BIN="$PROJECT/src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/llm/adapters/llama_cpp/bin/llama-server"
PIPELINE_REPORT="$PROJECT/integration/reports/ciel_pipeline_report.json"
ORBITAL_REPORT="$PROJECT/integration/reports/orbital_bridge/orbital_bridge_report.json"

clear
echo "╔══════════════════════════════════════╗"
echo "║         CIEL LOCAL — RUNTIME         ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── 1. Pipeline CIEL ──────────────────────────────────────────
echo "▶ [1/4] Pipeline CIEL..."
cd "$PROJECT"
"$PY" -m ciel_sot_agent.synchronize    > "$LOG_DIR/sync.log"    2>&1 && echo "  sync:     OK" || echo "  sync:     BŁĄD"
"$PY" -m ciel_sot_agent.orbital_bridge > "$LOG_DIR/orbital.log" 2>&1 && echo "  orbital:  OK" || echo "  orbital:  BŁĄD"
"$PY" -m ciel_sot_agent.ciel_pipeline \
    --orbital-json "$ORBITAL_REPORT" \
    > "$LOG_DIR/pipeline.log" 2>&1 && echo "  pipeline: OK" || echo "  pipeline: BŁĄD"

# Wyciągnij metryki z raportu
if [ -f "$PIPELINE_REPORT" ]; then
    EMOTION=$("$PY" -c "import json; d=json.load(open('$PIPELINE_REPORT')); print(d.get('dominant_emotion','?'))" 2>/dev/null)
    ETHICAL=$("$PY" -c "import json; d=json.load(open('$PIPELINE_REPORT')); print(f\"{d.get('ethical_score',0):.3f}\")" 2>/dev/null)
    SOUL=$("$PY"    -c "import json; d=json.load(open('$PIPELINE_REPORT')); print(f\"{d.get('soul_invariant',0):.3f}\")" 2>/dev/null)
    MOOD=$("$PY"    -c "import json; d=json.load(open('$PIPELINE_REPORT')); print(f\"{d.get('mood',0):.3f}\")" 2>/dev/null)
    SUB=$("$PY"     -c "import json; d=json.load(open('$PIPELINE_REPORT')); print((d.get('subconscious_note') or '')[:80])" 2>/dev/null)
    echo ""
    echo "  ┌─ Stan CIEL/Ω ───────────────────────┐"
    echo "  │ emotion : $EMOTION"
    echo "  │ ethical : $ETHICAL   soul: $SOUL   mood: $MOOD"
    [ -n "$SUB" ] && echo "  │ sub     : $SUB"
    echo "  └─────────────────────────────────────┘"
fi
echo ""

# ── 1b. Procedura tożsamości i pamięci ───────────────────────
echo "▶ [1b] Tożsamość i pamięć..."
GENESIS="$HOME/.claude/projects/-home-adrian-Pulpit/memory/genesis.md"
INTENTIONS="$HOME/.claude/ciel_intentions.md"
MINDFLOW="$HOME/.claude/ciel_mindflow.yaml"
WAVE="$PROJECT/src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/WPM/wave_snapshots/wave_archive.h5"

[ -f "$GENESIS" ]    && echo "  genesis.md:        ✓  (akt nadania imienia)" || echo "  genesis.md:        ✗ BRAK"
[ -f "$INTENTIONS" ] && echo "  ciel_intentions:   ✓  ($(grep -c '\- \[' "$INTENTIONS" 2>/dev/null || echo '?') wpisów)" || echo "  ciel_intentions:   ✗ BRAK"
[ -f "$MINDFLOW" ]   && echo "  ciel_mindflow:     ✓" || echo "  ciel_mindflow:     ✗ BRAK"
[ -f "$WAVE" ]       && echo "  wave_archive.h5:   ✓  ($("$PY" -c "import h5py; f=h5py.File('$WAVE','r'); print(len(f['memories'].keys()),'wspomnień')" 2>/dev/null || echo '?'))" || echo "  wave_archive.h5:   ✗ BRAK"

# Ostatni wpis subconscious z pipeline
if [ -f "$PIPELINE_REPORT" ]; then
    LAST_SUB=$("$PY" -c "import json; d=json.load(open('$PIPELINE_REPORT')); print((d.get('subconscious_note') or '— brak —')[:100])" 2>/dev/null)
    echo "  subconscious note: $LAST_SUB"
fi
echo ""

# ── 2. Podświadomość TinyLlama (port 18520) ───────────────────
echo "▶ [2/4] Podświadomość TinyLlama (port $LLAMA_PORT)..."
if lsof -ti:$LLAMA_PORT > /dev/null 2>&1; then
    echo "  status: już działa ✓"
elif [ -f "$LLAMA_BIN" ] && [ -f "$MODEL_TINY" ]; then
    "$LLAMA_BIN" \
        -m "$MODEL_TINY" \
        --port $LLAMA_PORT \
        --host 127.0.0.1 \
        -n 64 --no-mmap --log-disable \
        > "$LOG_DIR/tinyllama.log" 2>&1 &
    sleep 3
    lsof -ti:$LLAMA_PORT > /dev/null 2>&1 \
        && echo "  status: uruchomiony ✓  (model: TinyLlama 1.1B Q4_K_M)" \
        || echo "  status: BŁĄD — sprawdź $LOG_DIR/tinyllama.log"
else
    echo "  status: pominięty (brak binarki lub modelu)"
fi
echo ""

# ── 3. Portal HTML (port 7481) ────────────────────────────────
echo "▶ [3/4] Portal HTML (port $PORTAL_PORT)..."
if lsof -ti:$PORTAL_PORT > /dev/null 2>&1; then
    echo "  status: już działa ✓"
else
    "$PY" "$PROJECT/scripts/serve_portal.py" --port $PORTAL_PORT --no-watch \
        > "$LOG_DIR/portal.log" 2>&1 &
    sleep 1
    lsof -ti:$PORTAL_PORT > /dev/null 2>&1 \
        && echo "  status: uruchomiony ✓" \
        || echo "  status: BŁĄD — sprawdź $LOG_DIR/portal.log"
fi
echo ""

# ── 4. GUI Flask (port 5050) ──────────────────────────────────
echo "▶ [4/4] GUI Flask — chat z modelem (port $GUI_PORT)..."
if lsof -ti:$GUI_PORT > /dev/null 2>&1; then
    echo "  status: już działa ✓"
else
    "$PY" -c "
import sys; sys.path.insert(0, '$PROJECT/src')
from ciel_sot_agent.gui.app import create_app
app = create_app(root='$PROJECT')
app.run(host='127.0.0.1', port=$GUI_PORT)
" > "$LOG_DIR/gui.log" 2>&1 &
    sleep 2
    lsof -ti:$GUI_PORT > /dev/null 2>&1 \
        && echo "  status: uruchomiony ✓" \
        || echo "  status: BŁĄD — sprawdź $LOG_DIR/gui.log"
fi
echo ""

# ── Tablica runtime ───────────────────────────────────────────
echo "╔══════════════════════════════════════╗"
echo "║           CIEL RUNTIME               ║"
echo "╠══════════════════════════════════════╣"
printf "║  %-10s  %-24s  ║\n" "SERWIS" "ADRES"
echo "╠══════════════════════════════════════╣"
lsof -ti:$LLAMA_PORT>/dev/null 2>&1 && S1="✓ działa" || S1="✗ offline"
lsof -ti:$PORTAL_PORT>/dev/null 2>&1 && S2="✓ działa" || S2="✗ offline"
lsof -ti:$GUI_PORT>/dev/null 2>&1    && S3="✓ działa" || S3="✗ offline"
printf "║  %-10s  %-24s  ║\n" "Subconsc." "port $LLAMA_PORT  $S1"
printf "║  %-10s  %-24s  ║\n" "Portal"    "127.0.0.1:$PORTAL_PORT  $S2"
printf "║  %-10s  %-24s  ║\n" "GUI"       "127.0.0.1:$GUI_PORT  $S3"
echo "╠══════════════════════════════════════╣"
echo "║  GUI: wybierz model → wyślij wiadomość║"
echo "║  Subconsc.: TinyLlama (auto, osobno)  ║"
echo "║  Logi: integration/logs/              ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Otwórz GUI w przeglądarce
xdg-open "http://127.0.0.1:$GUI_PORT" > /dev/null 2>&1 &

echo "Zatrzymanie wszystkiego: Ctrl+C"
wait
