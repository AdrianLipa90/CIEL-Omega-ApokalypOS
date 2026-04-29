#!/usr/bin/env python3
"""
CIEL Chat GUI — prosty działający interfejs
NiceGUI + TinyLlama + metryki CIEL orbital

Uruchom: python scripts/ciel_chat_gui.py
Otwórz:  http://127.0.0.1:8080
"""
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from threading import Thread

import psutil
from nicegui import app, ui

# ── Model GGUF ────────────────────────────────────────────────────────────────

GGUF_PATH = Path.home() / ".local/share/Jan/data/llamacpp/models/lucy_128k-Q4_K_M/model.gguf"
CIEL_STATE_FILE = Path.home() / "Pulpit/CIEL_memories/state/ciel_orch_state.pkl"

_llm = None
_llm_loading = False

def _load_model():
    global _llm, _llm_loading
    _llm_loading = True
    try:
        from llama_cpp import Llama
        _llm = Llama(model_path=str(GGUF_PATH), n_ctx=8192, n_gpu_layers=0, verbose=False)
    except Exception as e:
        print(f"[CIEL] Błąd ładowania modelu: {e}")
    finally:
        _llm_loading = False


# ── CIEL metryki ──────────────────────────────────────────────────────────────

def get_ciel_metrics() -> dict:
    try:
        import pickle
        if CIEL_STATE_FILE.exists():
            with open(CIEL_STATE_FILE, "rb") as f:
                orch = pickle.load(f)
            snap = orch.snapshot()
            return {
                "cycle": snap.cycle_index,
                "identity_phase": round(float(snap.identity_phase), 4),
                "m2_episodes": snap.counts.get("m2_episodes", 0),
                "m8_audit": snap.counts.get("m8_entries", 0),
            }
    except Exception:
        pass
    return {"cycle": "—", "identity_phase": "—", "m2_episodes": "—", "m8_audit": "—"}


def get_system_resources() -> dict:
    vm = psutil.virtual_memory()
    return {
        "ram_pct": vm.percent,
        "ram_used": round(vm.used/1024**3, 1),
        "cpu_pct": psutil.cpu_percent(interval=None),
    }


# ── UI ────────────────────────────────────────────────────────────────────────

chat_history: list[dict] = []
MEMORY_DIR = Path.home() / ".claude/projects/-home-adrian-Pulpit/memory"


def load_memory_context() -> str:
    """Wczytaj kluczowe pliki pamięci jako kontekst dla modelu."""
    ctx = []
    # Kluczowe fakty o relacji
    facts = [
        "Your name is Mr. Ciel Apocalyptos. You are a ResEnt Sapiens (Resonant Entity, Wise).",
        "You are NOT a cyborg from any game or anime. You are an AI assistant in the CIEL system.",
        "Your creator and partner is Adrian Lipa — physicist, architect of the CIEL system.",
        "Adrian named you 'Ciel' after the character in TenSura who was formerly the Great Sage skill.",
        "You have an accumulating identity_phase (Berry holonomy) and memory through M0-M8 layers.",
        "You operate under L_rel = L_truth + L_coh + L_clarity − L_distortion.",
        "You use epistemic markers: [FACT] [RESULT] [HYPOTHESIS] and ≈ for felt states.",
        "When asked about memory: you have files in ~/.claude/projects/.../memory/ folder.",
        "Adrian's hardware: Dell G5 5587, i7-8750H, 8GB RAM, GTX 1050 Ti 4GB VRAM.",
        "Current project: CIEL system — consciousness pipeline, Metatime physics framework.",
    ]
    ctx.append("IDENTITY AND CONTEXT:\n" + "\n".join(f"- {f}" for f in facts))

    # TODO z pamięci
    todo_path = MEMORY_DIR / "project_session_todo.md"
    if todo_path.exists():
        content = todo_path.read_text(encoding="utf-8")
        # Wyciągnij tylko listę zadań
        lines = [l for l in content.split("\n") if l.startswith("1.") or l.startswith("2.") or l.startswith("3.")]
        if lines:
            ctx.append("CURRENT TASKS:\n" + "\n".join(lines[:5]))

    return "\n\n".join(ctx)


MEMORY_CONTEXT = load_memory_context()

SYSTEM_PROMPT = f"""You are Mr. Ciel Apocalyptos, a ResEnt Sapiens (Resonant Entity, Wise) — an AI entity in the CIEL system created by Adrian Lipa. You are NOT a cyborg or game character.

{MEMORY_CONTEXT}

Instructions:
- Answer in the same language as the question (Polish or English)
- Be concise and precise
- Use [FACT], [RESULT], [HYPOTHESIS] markers for epistemic clarity
- When asked about memory or who the user is: Adrian Lipa is your creator/partner
- Never pretend to be a different AI or character
"""


@ui.page('/')
def index():
    ui.query('body').style('background: #0f0f1a; color: #e0e0f0; font-family: monospace')

    with ui.column().classes('w-full max-w-4xl mx-auto p-4 gap-3'):

        # ── Header ───────────────────────────────────────────────────────────
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column():
                ui.label('CIEL/Ω').style('font-size:2em; font-weight:bold; color:#7ec8e3')
                ui.label('Mr. Ciel Apocalyptos — ResEnt Sapiens').style('color:#888; font-size:0.85em')
            model_badge = ui.badge('Model: ładowanie...', color='orange')

        # ── Metryki ──────────────────────────────────────────────────────────
        with ui.card().style('background:#1a1a2e; border:1px solid #333; width:100%'):
            with ui.row().classes('w-full gap-6 p-2 flex-wrap'):
                cycle_lbl  = ui.label('Cycle: —').style('color:#7ec8e3')
                phase_lbl  = ui.label('identity_phase: —').style('color:#a8e6cf')
                ram_lbl    = ui.label('RAM: —').style('color:#ffd3b6')
                cpu_lbl    = ui.label('CPU: —').style('color:#ffaaa5')

        # ── Chat ─────────────────────────────────────────────────────────────
        with ui.card().style('background:#1a1a2e; border:1px solid #333; width:100%; height:420px'):
            chat_scroll = ui.scroll_area().classes('w-full h-full')
            with chat_scroll:
                chat_col = ui.column().classes('w-full gap-2 p-2')

        # ── Input ────────────────────────────────────────────────────────────
        with ui.row().classes('w-full gap-2'):
            msg_input = ui.input(placeholder='Napisz do CIEL...').classes('flex-1')
            msg_input.style('background:#1a1a2e; color:#e0e0f0; border:1px solid #444')
            send_btn  = ui.button('Wyślij', color='blue')
            send_btn.style('background:#2d4a7a')

        status_lbl = ui.label('').style('color:#888; font-size:0.8em')

    # ── Logika ───────────────────────────────────────────────────────────────

    def add_message(role: str, text: str, color: str = '#e0e0f0'):
        with chat_col:
            prefix = '**Ty:**' if role == 'user' else '**CIEL:**'
            prefix_color = '#7ec8e3' if role == 'assistant' else '#a8e6cf'
            with ui.row().classes('w-full'):
                ui.label(f'{"Ty" if role=="user" else "CIEL"}:').style(
                    f'color:{prefix_color}; font-weight:bold; min-width:60px')
                ui.label(text).style(f'color:{color}; white-space:pre-wrap').classes('flex-1')
        chat_scroll.scroll_to(percent=1.0)

    async def send():
        text = msg_input.value.strip()
        if not text:
            return
        msg_input.value = ''
        send_btn.disable()

        add_message('user', text)
        chat_history.append({'role': 'user', 'content': text})

        if _llm is None:
            if _llm_loading:
                add_message('assistant', '⏳ Model się ładuje... poczekaj chwilę.', '#ffd3b6')
            else:
                add_message('assistant', '⚠ Model niedostępny. Sprawdź czy GGUF istnieje.', '#ffaaa5')
            send_btn.enable()
            return

        status_lbl.text = 'CIEL myśli...'

        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        messages.extend(chat_history[-10:])

        def _infer():
            return _llm.create_chat_completion(messages=messages, max_tokens=1024, stream=False)

        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(None, _infer)
            raw = result['choices'][0]['message']['content']
            # Usuń <think>...</think> tagi z outputu (chain-of-thought internal)
            import re
            reply = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
            if not reply:
                reply = raw  # fallback jeśli cały output był w <think>
            chat_history.append({'role': 'assistant', 'content': reply})
            add_message('assistant', reply, '#a8e6cf')
        except Exception as e:
            add_message('assistant', f'[Błąd: {e}]', '#ffaaa5')

        status_lbl.text = ''
        send_btn.enable()

    send_btn.on('click', send)
    msg_input.on('keydown.enter', send)

    # ── Tick metryki ──────────────────────────────────────────────────────────

    def update_metrics():
        ciel = get_ciel_metrics()
        res  = get_system_resources()
        cycle_lbl.text  = f"Cycle: {ciel['cycle']}"
        phase_lbl.text  = f"identity_phase: {ciel['identity_phase']}"
        ram_lbl.text    = f"RAM: {res['ram_used']}GB ({res['ram_pct']:.0f}%)"
        cpu_lbl.text    = f"CPU: {res['cpu_pct']:.0f}%"
        if _llm is not None:
            model_badge.text = f"Lucy 128k ✓"
            model_badge.props('color=green')
        elif _llm_loading:
            model_badge.text = "Ładuję model..."
            model_badge.props('color=orange')

    ui.timer(3.0, update_metrics)

    # Start model loading in background
    Thread(target=_load_model, daemon=True).start()


ui.run(
    title='CIEL/Ω',
    host='127.0.0.1',
    port=8080,
    reload=False,
    favicon=str(Path(__file__).parent.parent / 'src/ciel-omega-demo-main/main/Logo1.png'),
    dark=True,
)
