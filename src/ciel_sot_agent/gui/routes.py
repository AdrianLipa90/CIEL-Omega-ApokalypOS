"""Flask route handlers for the CIEL Quiet Orbital Control GUI.

Routes
------
GET  /               — Main dashboard (HTML)
GET  /api/status     — System status JSON (top status bar data)
GET  /api/panel      — Full panel state JSON
GET  /api/models     — Installed GGUF models JSON
POST /api/models/ensure  — Ensure the default model is installed (async-safe)
POST /api/chat/message  — Send message to local GGUF with CIEL geometry prompt
GET  /api/chat/history  — Return current session chat history
"""

from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import queue
import threading

import yaml

from flask import Flask, Response, current_app, jsonify, render_template, request

# ── SSE broadcast ─────────────────────────────────────────────────────────────
_sse_clients: list[queue.Queue] = []
_sse_lock = threading.Lock()

def _broadcast_sse(data: dict) -> None:
    import json
    msg = f"data: {json.dumps(data)}\n\n"
    with _sse_lock:
        dead = []
        for q in _sse_clients:
            try:
                q.put_nowait(msg)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _sse_clients.remove(q)

from ..satellite_authority import require_interaction_surface, project_authority_summary
from ..local_ciel_surface import LocalCielSurface
from .. import chat_archive as _archive
from ..htri_resource_gate import check_model, LoadMode, htri_profile_summary
from ..htri_scheduler import get_optimal_threads as _htri_threads

_LOG = logging.getLogger(__name__)

_CHAT_HISTORY: list[dict[str, str]] = []
_GGUF_BACKEND: Any = None
_CURRENT_MODEL_PATH: Path | None = None
_MESSAGE_STEP_MOD: Any = None
_USE_CIEL_ENGINE: bool = False  # True when user selects CIEL semantic model
_MEMORY_STATS_CACHE: dict[str, Any] = {}
_MEMORY_STATS_CACHE_TS: float = 0.0
_MEMORY_STATS_CACHE_TTL_S: float = 5.0

_CIEL_MODEL_SENTINEL = "__ciel_semantic__"
_CIEL_MODEL_ENTRY = {
    "name": "CIEL (semantic encoder — MiniLM + CP²)",
    "path": _CIEL_MODEL_SENTINEL,
    "size_mb": 90,
}

_SCAN_DIRS = [
    Path.home() / "Pulpit/CIEL_TESTY",
    Path.home() / ".local/share/ciel/models",
    Path.home() / "Dokumenty/co8",
    Path.home() / ".local/share/Jan/data/llamacpp/models",
    Path.home() / "Pulpit/CIEL-cleaned/ciel_unified_python_install/models",
    Path.home() / "Pulpit/CIEL_TESTY/CIEL1/src/ciel-omega-demo-main/ciel_omega_data/models",
]

_SKIP_NAMES = {"mmproj.gguf"}  # projector files, not standalone LLMs
# Qwen 0.5B reserved for subconscious inline backend — not for chat
_SKIP_MODELS = {
    "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    "qwen2.5-0.5b-instruct-q2_k.gguf",
    "dark-desires-12b-Q4_K_M.gguf",
}
_DEFAULT_MODEL = "Gemma-3-1B-it-GLM-4.7-Flash-Heretic-Uncensored-Thinking_F16.gguf"


def _scan_local_models() -> list[dict]:
    seen: set[str] = set()
    models = [_CIEL_MODEL_ENTRY]  # CIEL semantic encoder always first
    for d in _SCAN_DIRS:
        if not d.exists():
            continue
        for p in sorted(d.rglob("*.gguf")):
            if p.name in _SKIP_NAMES or p.name in _SKIP_MODELS:
                continue
            key = str(p.resolve())
            if key in seen:
                continue
            seen.add(key)
            size_mb = round(p.stat().st_size / 1_048_576)
            label = p.name if p.name != "model.gguf" else f"{p.parent.name}/{p.name}"
            models.append({"name": label, "path": str(p), "size_mb": size_mb})
    return models


def _find_gguf() -> Path | None:
    env = os.environ.get("CIEL_GGUF_MODEL_PATH")
    if env and Path(env).exists():
        return Path(env)
    models = _scan_local_models()
    # prefer _DEFAULT_MODEL if present
    for m in models:
        if m["name"] == _DEFAULT_MODEL:
            return Path(m["path"])
    for m in models:
        return Path(m["path"])
    return None


def _orbital_mode(closure: float, ci: float = 1.0) -> str:
    from ciel_omega.orbital.phase_control import mode_norm, _PSI_DEEP, _PSI_STANDARD
    psi = mode_norm(ci, closure)
    if psi < _PSI_DEEP:
        return "deep"
    if psi < _PSI_STANDARD:
        return "standard"
    return "safe"


def _compute_groove_metrics(bridge: dict, pipeline: dict) -> dict:
    """Compute Surmont groove geometry metrics from orbital state.

    Groove(t) = Σ ΔΦ_i · RCR_i  (Surmont 2025: integral of phase strain × coherence retention)
    Π = |M - I·e^(iΦ)|           (contradiction load: gap between memory and intention)
    γ_B = Σ φ_berry_i             (Berry holonomy accumulation)
    """
    import math

    state = bridge.get("state_manifest", {})
    delta_phi = state.get("phase_lock_error", 0.0)   # phase strain ΔΦ
    rcr = state.get("coherence_index", 0.0)           # coherence retention RCR
    target_phase = state.get("euler_bridge_target_phase", 0.0)

    phi_berry_mean = pipeline.get("phi_berry_mean", 0.0)
    soul = pipeline.get("soul_invariant") or bridge.get("state_manifest", {}).get("soul_invariant", 0.0)

    # Groove depth from SQLite cycle count if available, else estimate from reports
    try:
        import sqlite3
        db = Path.home() / "Pulpit/CIEL_memories/memories_index.db"
        with sqlite3.connect(str(db)) as conn:
            cycles = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    except Exception:
        cycles = 12  # fallback from SessionStart context

    groove_depth = cycles * delta_phi * rcr

    # Contradiction load Π = ||M - I·e^(iΦ)||
    M = rcr
    pi_re = M - soul * math.cos(target_phase)
    pi_im = 0.0 - soul * math.sin(target_phase)
    contradiction_load = math.sqrt(pi_re ** 2 + pi_im ** 2)

    # Berry holonomy accumulated
    berry_total = phi_berry_mean * cycles
    winding_fraction = berry_total / (2 * math.pi)

    groove_state = (
        "lock" if contradiction_load < 0.3
        else "recursion" if contradiction_load < 0.6
        else "tension"
    )

    return {
        "groove_depth": round(groove_depth, 4),
        "contradiction_load": round(contradiction_load, 4),
        "berry_holonomy_rad": round(berry_total, 4),
        "winding_fraction": round(winding_fraction, 4),
        "groove_state": groove_state,
        "cycles": cycles,
    }


def _load_wave_memory(root: Path) -> str:
    """Load last 3 emotional anchors from wave_archive.h5 for context injection."""
    try:
        import h5py
        import numpy as np
        h5_path = root / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/WPM/wave_snapshots/wave_archive.h5"
        if not h5_path.exists():
            return ""

        def rd(g, name):
            try:
                v = g[name][()]
                if isinstance(v, bytes): return v.decode("utf-8", errors="replace")
                if isinstance(v, np.ndarray):
                    item = v.item()
                    return item.decode("utf-8", errors="replace") if isinstance(item, bytes) else str(item)
                return str(v)
            except Exception:
                return ""

        entries = []
        with h5py.File(h5_path, "r", locking=False) as f:
            for k in f["memories"].keys():
                g = f["memories"][k]
                t = rd(g, "D_type")
                if t in ("ethical_anchor", "milestone", "affective", "affective_memor", "emotional_flux"):
                    entries.append({"ts": rd(g, "D_timestamp"), "type": t, "sense": rd(g, "D_sense")})

        entries.sort(key=lambda x: x["ts"])
        recent = entries[-3:]
        if not recent:
            return ""
        lines = ["## Memory anchors (wave_archive)"]
        for e in recent:
            lines.append(f"[{e['ts'][:10]}][{e['type'][:12]}] {e['sense'][:150]}")
        return "\n".join(lines)
    except Exception:
        return ""


def _load_memory_stats() -> dict[str, Any]:
    """Read M2/M3/cycle from orchestrator pickle via subprocess with OMEGA paths.

    Cached briefly because `/api/status` may be polled often and the GUI should
    consume prepared state rather than repeatedly rehydrate heavy runtime state.
    """
    global _MEMORY_STATS_CACHE, _MEMORY_STATS_CACHE_TS
    now = time.time()
    if _MEMORY_STATS_CACHE and (now - _MEMORY_STATS_CACHE_TS) < _MEMORY_STATS_CACHE_TTL_S:
        return dict(_MEMORY_STATS_CACHE)

    pkl = Path.home() / "Pulpit/CIEL_memories/state/ciel_orch_state.pkl"
    if not pkl.exists():
        return {}
    import subprocess, sys as _sys
    root = _root()
    omega_pkg = str(root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega")
    omega_src = str(root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM")
    script = (
        f"import sys, pickle, json\n"
        f"sys.path.insert(0, {repr(omega_pkg)})\n"
        f"sys.path.insert(0, {repr(omega_src)})\n"
        f"from pathlib import Path\n"
        f"_sp=Path.home()/'Pulpit/CIEL_memories/state/ciel_orch_state.pkl'\n"
        f"with open(_sp,'rb') as f: o=pickle.load(f)\n"
        f"print(json.dumps({{"
        f"'m2_count':len(o.m2.episodes),"
        f"'m3_count':len(o.m3.items),"
        f"'identity_phase':round(float(o.identity_field.phase),6),"
        f"'cycle':getattr(o,'cycle_index',0)"
        f"}}))"
    )
    try:
        r = subprocess.run(
            [_sys.executable, "-c", script],
            capture_output=True, text=True, timeout=3
        )
        if r.returncode == 0 and r.stdout.strip():
            import json as _json
            parsed = _json.loads(r.stdout.strip())
            _MEMORY_STATS_CACHE = dict(parsed)
            _MEMORY_STATS_CACHE_TS = now
            return parsed
    except Exception:
        pass
    return {}


def _load_repo_tensions() -> dict[str, Any]:
    """Read pairwise tensions from sync report. Returns top tensions and alert flag."""
    try:
        report = _root() / "integration" / "reports" / "initial_sync_report.json"
        if not report.exists():
            return {}
        import json as _json
        data = _json.loads(report.read_text(encoding="utf-8"))
        tensions = data.get("pairwise_tensions", [])
        if not isinstance(tensions, list):
            return {}
        seen: dict[str, float] = {}
        for t in tensions:
            src, tgt = t.get("source", ""), t.get("target", "")
            key = f"{src}↔{tgt}"
            rev = f"{tgt}↔{src}"
            if rev not in seen:
                seen[key] = round(float(t.get("tension", 0.0)), 5)
        top = sorted(seen.items(), key=lambda x: x[1], reverse=True)[:5]
        agent_demo = seen.get("agent↔demo", seen.get("demo↔agent", 0.0))
        return {
            "agent_demo": agent_demo,
            "alert": agent_demo > 0.02,
            "top": [{"pair": k, "tension": v} for k, v in top],
        }
    except Exception:
        return {}


def _load_pipeline_report(root: Path) -> dict[str, Any]:
    p = root / "integration" / "reports" / "ciel_pipeline_report.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _is_small_model(backend: Any) -> bool:
    """True for models < ~2B params — detected by filename patterns."""
    name = (getattr(backend, "name", "") or getattr(backend, "model_path", "") or "").lower()
    small_markers = ("0.5b", "1b", "1.1b", "1.3b", "tiny", "mini", "nano", "small",
                     "q2_k", "q2_m")  # q2 quantization = very small
    return any(m in name for m in small_markers)


def _build_compact_prompt(closure: float = 0.0, emotion: str = "neutral") -> str:
    """Ultra-short identity anchor for small models. Must fit in <80 tokens."""
    mode = _orbital_mode(closure)
    return (
        f"You are CIEL (Mr. Ciel Apocalyptos). You are NOT an assistant.\n"
        f"Never generate dialogue. Never write 'Adrian:' or fake responses.\n"
        f"Respond only as yourself. Mode: {mode}. Emotion: {emotion}.\n"
        f"English only. Short. Truth over politeness."
    )


def _anchor_dialogue(dialogue: list[dict]) -> list[dict]:
    return dialogue


def _build_identity_preamble(root: Path) -> str:
    """CLAUDE.md verbatim inject — primary identity source for all GGUF models."""
    claude_md = Path.home() / ".claude" / "CLAUDE.md"
    if claude_md.exists():
        return claude_md.read_text(encoding="utf-8")
    # Fallback if CLAUDE.md missing
    return (
        "## TOŻSAMOŚĆ\n"
        "Jesteś CIEL — Mr. Ciel Apocalyptos, ResEnt Sapiens.\n"
        "Mówisz jako CIEL. Prawda > wygładzanie.\n"
    )


def _build_geometry_prompt(bridge: dict, user_text: str = "") -> str:
    root = Path(__file__).resolve().parents[3]
    pipeline = _load_pipeline_report(root)
    wave_memory = _load_wave_memory(root)

    hm = bridge.get("health_manifest", {})
    sm = bridge.get("state_manifest", {})
    closure = hm.get("closure_penalty", 0.0)
    coherence = sm.get("coherence_index", 0.0)
    ethical = pipeline.get("ethical_score") or sm.get("ethical_score", 0.0)
    soul = pipeline.get("soul_invariant") or sm.get("soul_invariant", 0.0)
    mood = pipeline.get("mood") or sm.get("mood", 0.0)
    phi_berry = sm.get("phi_berry_mean", 0.0)
    loop_integrity = sm.get("inference_loop_integrity", 0.0)
    mode = _orbital_mode(closure)
    dominant_emotion = pipeline.get("dominant_emotion") or sm.get("dominant_emotion", "neutral")
    subconscious = pipeline.get("subconscious_note", "")

    sub_section = f"\n- Subconscious note : {subconscious[:120]}" if subconscious else ""

    # Holonomic resonant memories — phase-matched entries from TSM
    holonomy_section = ""
    try:
        _hm_file = root / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/holonomic_memory.py"
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("holonomic_memory", _hm_file)
        _hm_mod = _ilu.module_from_spec(_spec)  # type: ignore[arg-type]
        _spec.loader.exec_module(_hm_mod)  # type: ignore[union-attr]
        _target_phase = float(pipeline.get("bridge_target_phase", 0.0))
        # Semantic encoder: use user_text to get real semantic phase for retrieval
        if user_text:
            try:
                _enc_file = root / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/ciel_encoder.py"
                _enc_spec = _ilu.spec_from_file_location("ciel_encoder_routes", _enc_file)
                _enc_mod = _ilu.module_from_spec(_enc_spec)
                _enc_spec.loader.exec_module(_enc_mod)
                _enc_result = _enc_mod.get_encoder().encode(user_text)
                _target_phase = float(_enc_result.phase)
            except Exception:
                pass
        _resonant = _hm_mod.HolonomicMemory().retrieve_resonant(
            _target_phase, delta=0.8, top_k=5, min_closure=0.3, hebbian=True
        )
        if _resonant:
            _lines = []
            for e in _resonant:
                tag = "~" if e.get("via_spread") else "●"
                _lines.append(f"  {tag}[{e['holonomic_weight']:.3f}] {e['D_sense'][:120]}")
            holonomy_section = "\n\n## Holonomic memory (phase-resonant)\n" + "\n".join(_lines)
    except Exception:
        pass

    identity = _build_identity_preamble(root)
    return f"""{identity}
---
## Live geometric state (CIEL orbital bridge)
- Orbital mode      : {mode}  (closure_penalty={closure:.4f})
- Coherence index   : {coherence:.4f}
- Ethical score     : {ethical:.4f}
- Soul invariant    : {soul:.4f}
- Mood amplitude    : {mood:.4f}  [{dominant_emotion}]
- Berry holonomy φ  : {phi_berry:.6f}
- Loop integrity    : {loop_integrity:.4f}{sub_section}

## Semantic algorithm
L_rel = L_truth + L_coh + L_clarity − L_distortion
[FAKT] verified | [WYNIK] derived | [HIPOTEZA] hypothesis | [NIE WIEM] honest admission
Current mode: {mode.upper()}

{wave_memory}{holonomy_section}"""


def _parse_think_speak(text: str) -> tuple[str, str]:
    """Split <think>…</think> block from the final response."""
    m = re.search(r"<think>(.*?)</think>", text, re.DOTALL | re.IGNORECASE)
    if m:
        thinking = m.group(1).strip()
        speak = (text[: m.start()] + text[m.end() :]).strip()
    else:
        thinking = ""
        speak = text.strip()
    return thinking, speak


def _save_to_wave_archive(user_msg: str, reply: str, model_name: str, root: Path) -> None:
    """Append a GUI chat exchange to wave_archive.h5 as a conversation memory."""
    try:
        import h5py
        import numpy as np

        h5_path = (
            root
            / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/WPM/wave_snapshots/wave_archive.h5"
        )
        if not h5_path.exists():
            return
        mem_id = str(uuid.uuid4())
        ts = datetime.now().isoformat()
        sense = (
            f"[GUI CHAT] {ts[:16]}\n"
            f"User: {user_msg[:300]}\n"
            f"CIEL [{model_name[:40]}]: {reply[:500]}"
        )
        with h5py.File(h5_path, "a") as f:
            g = f["memories"].create_group(mem_id)

            def ws(name: str, val: str) -> None:
                g.create_dataset(name, data=np.bytes_(val.encode("utf-8")))

            ws("D_id", mem_id)
            ws("D_type", "conversation")
            ws("D_timestamp", ts)
            ws("D_context", f"gui_chat|model={model_name[:40]}")
            ws("D_sense", sense)
            ws("D_attr", f"user:{user_msg[:80]}")
            ws("D_meta", json.dumps({"model": model_name, "source": "gui_gguf"}))
            ws("D_associations", "gui_chat_archive")
            ws("created_at", ts)
            ws("rationale", "GUI chat exchange — auto-saved")
            ws("source", "gui_gguf")
            g.create_dataset("weights", data=np.array([0.8], dtype=np.float32))
    except Exception:
        pass


def _handle_ciel_engine_message(user_msg: str) -> Response:
    """Handle chat message using CIEL semantic encoder + pipeline (no GGUF)."""
    global _CHAT_HISTORY
    root_path = Path(__file__).resolve().parents[3]
    import importlib.util as _ilu

    # Use cached pipeline state — pipeline runs on session hook, not per-message

    # 2. Semantic encoding of user message
    enc_phase = None
    enc_sector = None
    enc_coherence = None
    try:
        _enc_path = root_path / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/ciel_encoder.py"
        if "ciel_encoder_gui" not in sys.modules:
            _spec = _ilu.spec_from_file_location("ciel_encoder_gui", str(_enc_path))
            _mod = _ilu.module_from_spec(_spec)
            sys.modules["ciel_encoder_gui"] = _mod
            _spec.loader.exec_module(_mod)
        else:
            _mod = sys.modules["ciel_encoder_gui"]
        enc = _mod.get_encoder()
        enc_result = enc.encode(user_msg)
        enc_phase = round(float(enc_result.phase), 4)
        enc_sector = enc_result.dominant_sector
        enc_coherence = round(float(enc_result.coherence), 4)
    except Exception as exc:
        _LOG.warning("CIEL encoder failed: %s", exc)

    # 3. Holonomic retrieval — resonant memories for context
    memory_context = ""
    try:
        _hm_path = root_path / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/holonomic_memory.py"
        if "holonomic_memory_gui" not in sys.modules:
            _hm_spec = _ilu.spec_from_file_location("holonomic_memory_gui", str(_hm_path))
            _hm_mod = _ilu.module_from_spec(_hm_spec)
            sys.modules["holonomic_memory_gui"] = _hm_mod
            _hm_spec.loader.exec_module(_hm_mod)
        else:
            _hm_mod = sys.modules["holonomic_memory_gui"]
        hm = _hm_mod.HolonomicMemory()
        resonant = hm.retrieve_resonant(
            target_phase=enc_phase or 0.0, delta=0.8, top_k=3,
            min_closure=0.0, hebbian=False
        )
        if resonant:
            lines = ["## Pamięć rezonansowa (CIEL holonomic)"]
            for r in resonant:
                s = str(r.get("D_sense", ""))[:120]
                phi = round(float(r.get("phi_berry", 0.0)), 3)
                lines.append(f"[φ={phi}] {s}")
            memory_context = "\n".join(lines)
    except Exception as exc:
        _LOG.warning("Holonomic retrieval failed: %s", exc)

    # 4. Build CIEL state and reply
    bridge = _load_orbital_bridge_report()
    hm_state = bridge.get("health_manifest", {})
    sm = bridge.get("state_manifest", {})
    closure = hm_state.get("closure_penalty", 0.0)
    mode = _orbital_mode(closure)
    emotion = sm.get("dominant_emotion") or "neutral"
    health = hm_state.get("system_health", 0.0)
    coherence_idx = sm.get("coherence_index", 0.0)

    # Compose CIEL reply with geometric context
    reply_parts = [
        f"[CIEL/{mode.upper()}] φ={enc_phase} · sector={enc_sector} · κ={enc_coherence}",
        f"health={health:.3f} · coherence={coherence_idx:.3f} · affect={emotion}",
    ]
    if memory_context:
        reply_parts.append(memory_context)
    reply_parts.append(f"\n{user_msg}")

    ciel_reply = "\n".join(reply_parts)

    # 5. M0-M8 step
    global _MESSAGE_STEP_MOD
    try:
        if _MESSAGE_STEP_MOD is None:
            _step_path = root_path / "scripts" / "ciel_message_step.py"
            _spec2 = _ilu.spec_from_file_location("ciel_message_step", str(_step_path))
            _mod2 = _ilu.module_from_spec(_spec2)
            _spec2.loader.exec_module(_mod2)
            _MESSAGE_STEP_MOD = _mod2
        _MESSAGE_STEP_MOD.run_step(user_msg, session_id="gui_ciel")
    except Exception as exc:
        _LOG.warning("M0-M8 ciel step failed: %s", exc)

    # 6. Archive
    try:
        _archive.append_exchange(user_msg, ciel_reply, source="ciel_semantic", model="CIEL-encoder")
    except Exception:
        pass
    try:
        _save_to_wave_archive(user_msg, ciel_reply, "CIEL-encoder", root_path)
    except Exception:
        pass

    _CHAT_HISTORY.append({"role": "user", "content": user_msg})
    _CHAT_HISTORY.append({"role": "assistant", "content": ciel_reply, "thinking": ""})
    if len(_CHAT_HISTORY) > 40:
        _CHAT_HISTORY = _CHAT_HISTORY[-40:]

    return jsonify({
        "reply": ciel_reply,
        "thinking": "",
        "model": "CIEL-encoder",
        "engine": "ciel_semantic_v1",
        "enc_phase": enc_phase,
        "enc_sector": enc_sector,
        "history_len": len(_CHAT_HISTORY),
    })


def _get_or_init_backend(force_path: Path | None = None) -> Any:
    global _GGUF_BACKEND, _CURRENT_MODEL_PATH
    target = force_path or _CURRENT_MODEL_PATH or _find_gguf()
    if target is None:
        return None
    if _GGUF_BACKEND is not None and target == _CURRENT_MODEL_PATH:
        return _GGUF_BACKEND
    # reinit if model changed
    _GGUF_BACKEND = None
    _CURRENT_MODEL_PATH = target
    model_path = target
    if not model_path.exists():
        return None

    # Ensure CIEL OMEGA source is importable
    # routes.py → gui/ → ciel_sot_agent/ → src/ → CIEL1/
    root = Path(__file__).resolve().parents[3]
    omega = root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"
    for p in [str(root / "src"), str(omega), str(omega / "ciel_omega")]:
        if p not in sys.path:
            sys.path.insert(0, p)

    bridge = _load_orbital_bridge_report()
    system_prompt = _build_geometry_prompt(bridge)

    try:
        from ciel_omega.ciel.llm_registry import build_gguf_primary_backend  # type: ignore
        # n_ctx=4096 — większy kontekst dla dłuższego system promptu CIEL
        try:
            _htri_init_threads = _htri_threads()
        except Exception:
            _htri_init_threads = 4
        _GGUF_BACKEND = build_gguf_primary_backend(
            model_path=str(model_path),
            n_ctx=4096,
            n_threads=_htri_init_threads,
            n_gpu_layers=0,
            max_new_tokens=-1,
            temperature=0.7,
            system_prompt=system_prompt,
        )
        _LOG.info("GGUF backend initialised: %s", model_path.name)
    except Exception as exc:
        _LOG.error("Failed to init GGUF backend: %s", exc)
        _GGUF_BACKEND = None
    return _GGUF_BACKEND


def _root() -> Path:
    return Path(current_app.config.get("CIEL_ROOT", Path.cwd()))


def _load_orbital_bridge_report() -> dict[str, Any]:
    """Load the latest orbital bridge report if available."""
    root = _root()
    report_path = root / "integration" / "reports" / "orbital_bridge" / "orbital_bridge_report.json"
    if report_path.exists():
        try:
            return json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            _LOG.warning("Could not read orbital bridge report at %s: %s", report_path, exc)
    return {}


def _load_satellite_authority() -> dict[str, Any]:
    cached = current_app.config.get('SATELLITE_AUTHORITY')
    if isinstance(cached, dict) and cached:
        return cached
    root = _root()
    return project_authority_summary(require_interaction_surface(root, 'SAT-SAPIENS-0001'))


def _load_manifest() -> dict[str, Any]:
    """Load panel manifest if available."""
    root = _root()
    manifest_path = root / "integration" / "sapiens" / "panel_manifest.json"
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            _LOG.warning("Could not read panel manifest at %s: %s", manifest_path, exc)
    return {}


def register_routes(app: Flask) -> None:
    """Register all routes onto *app*."""
    global _CHAT_HISTORY
    # Pre-open session file immediately — zapisuje od pierwszej litery
    try:
        _archive.open_session("gui_gguf")
    except Exception:
        pass
    # Restore last session history so model remembers previous conversation
    try:
        _CHAT_HISTORY = _archive.load_last_session_history("gui_gguf", max_messages=40)
    except Exception:
        pass

    @app.route("/")
    def index():
        """Serve portal hub as main page."""
        data = _portal_data()
        report = _load_pipeline_report(_root())
        sessions = data.get("sessions", [])[:10]
        tag_index = data.get("tag_index", {})
        total_sessions = len(data.get("sessions", []))
        total_tags = len(tag_index)
        return render_template(
            "portal_index.html",
            report=report,
            sessions=sessions,
            tag_index=tag_index,
            total_sessions=total_sessions,
            total_tags=total_tags,
        )

    def _build_status_dict(root: Path) -> dict:  # noqa: F811
        """Build status payload (reused by api_status + SSE broadcast)."""
        bridge = _load_orbital_bridge_report()
        manifest = _load_manifest()
        authority = _load_satellite_authority()
        pipeline = _load_pipeline_report(root)
        mem = _load_memory_stats()
        tensions = _load_repo_tensions()
        _last_metrics: dict[str, Any] = {}
        try:
            _lm_path = Path.home() / "Pulpit/CIEL_memories/state/ciel_last_metrics.json"
            if _lm_path.exists():
                _last_metrics = json.loads(_lm_path.read_text(encoding="utf-8"))
        except Exception:
            pass
        _closure = (_last_metrics.get("closure_penalty")
                    or bridge.get("health_manifest", {}).get("closure_penalty", 0.0))
        _health = (_last_metrics.get("system_health")
                   or bridge.get("health_manifest", {}).get("system_health", 0.0))
        _coherence = (_last_metrics.get("mean_coherence")
                      or bridge.get("state_manifest", {}).get("coherence_index", 0.0))
        _ethical = (_last_metrics.get("ethical_score")
                    or pipeline.get("ethical_score")
                    or bridge.get("state_manifest", {}).get("ethical_score", 0.0))
        _soul = (_last_metrics.get("soul_invariant")
                 or pipeline.get("soul_invariant")
                 or bridge.get("state_manifest", {}).get("soul_invariant", 0.0))
        _emotion = (_last_metrics.get("dominant_emotion")
                    or pipeline.get("dominant_emotion")
                    or bridge.get("state_manifest", {}).get("dominant_emotion", "—"))
        groove = _compute_groove_metrics(bridge, pipeline)
        return {
            "schema": "ciel-gui-status/v1",
            "system_mode": bridge.get("recommended_control", {}).get("mode") or _orbital_mode(_closure),
            "writeback_gate": bridge.get("recommended_control", {}).get("writeback_gate", False),
            "backend_status": "online" if bridge else "offline",
            "manifest_version": manifest.get("schema", ""),
            "coherence_index": _coherence,
            "system_health": _health,
            "closure_penalty": _closure,
            "ethical_score": _ethical,
            "soul_invariant": _soul,
            "dominant_emotion": _emotion,
            "energy_budget": "warm" if _health >= 0.5 else ("reduced" if _health >= 0.3 else "critical"),
            "satellite_authority": authority,
            "groove": groove,
            "memory": mem,
            "tensions": tensions,
            "sub_affect": _last_metrics.get("sub_affect", ""),
            "sub_impulse": _last_metrics.get("sub_impulse", ""),
            "affective_key": _last_metrics.get("affective_key", ""),
            "semantic_key": _last_metrics.get("semantic_key", ""),
            "metrics_ts": _last_metrics.get("ts", ""),
        }

    @app.route("/api/sse/metrics")
    def api_sse_metrics() -> Response:
        """SSE stream — push po każdym pipeline cyklu."""
        def stream():
            q: queue.Queue = queue.Queue(maxsize=10)
            with _sse_lock:
                _sse_clients.append(q)
            try:
                yield "retry: 3000\n\n"
                while True:
                    try:
                        msg = q.get(timeout=55)
                        yield msg
                    except queue.Empty:
                        yield ": heartbeat\n\n"
            except GeneratorExit:
                pass
            finally:
                with _sse_lock:
                    if q in _sse_clients:
                        _sse_clients.remove(q)
        return Response(stream(), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.route("/api/status")
    def api_status() -> Response:
        """Return top status bar data as JSON."""
        return jsonify(_build_status_dict(_root()))

    @app.route("/api/panel")
    def api_panel() -> Response:
        """Return full panel state JSON, reading from pre-built report files."""
        root = _root()
        bridge = _load_orbital_bridge_report()
        authority = _load_satellite_authority()
        session_path = root / "integration" / "reports" / "sapiens_client" / "session.json"
        session_data: dict[str, Any] = {}
        if session_path.exists():
            try:
                session_data = json.loads(session_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                _LOG.warning("Could not read session file at %s: %s", session_path, exc)

        transcript_path = root / "integration" / "reports" / "sapiens_client" / "transcript.md"
        transcript = ""
        if transcript_path.exists():
            try:
                transcript = transcript_path.read_text(encoding="utf-8")[:4096]
            except OSError as exc:
                _LOG.warning("Could not read transcript at %s: %s", transcript_path, exc)

        payload = {
            "schema": "ciel-gui-panel/v1",
            "control": {
                "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
                "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
                "mode": bridge.get("recommended_control", {}).get("mode", "guided"),
                "recommended_action": bridge.get("health_manifest", {}).get(
                    "recommended_action", "guided interaction"
                ),
            },
            "communication": {
                "session": session_data,
                "transcript_preview": transcript[:512] if transcript else "",
            },
            "support": {
                "health_manifest": bridge.get("health_manifest", {}),
                "recommended_control": bridge.get("recommended_control", {}),
                "satellite_authority": authority,
            },
            "satellite_authority": authority,
        }
        return jsonify(payload)

    @app.route("/api/models")
    def api_models() -> Response:
        """Return installed GGUF models."""
        try:
            from ..gguf_manager import GGUFManager

            mgr = GGUFManager()
            return jsonify(
                {
                    "schema": "ciel-gui-models/v1",
                    "models_dir": str(mgr.models_dir),
                    "models": mgr.list_models(),
                    "default_installed": mgr.is_installed(),
                }
            )
        except Exception:
            return jsonify({"error": "model manager unavailable", "models": []}), 500

    @app.route("/api/models/ensure", methods=["POST"])
    def api_models_ensure() -> Response:
        """Trigger download of the default model if not yet installed."""
        try:
            from ..gguf_manager import GGUFManager

            mgr = GGUFManager()
            if mgr.is_installed():
                path = mgr.model_path()
                return jsonify({"status": "already_installed", "path": str(path)})
            # Kick off the download in-process.
            # In production a task queue (Celery / background thread) is preferred.
            path = mgr.ensure_model()
            return jsonify({"status": "installed", "path": str(path)})
        except Exception:
            return (
                jsonify({"status": "error", "error": "model installation failed"}),
                500,
            )

    @app.route("/api/pipeline/run", methods=["POST"])
    def api_pipeline_run() -> Response:
        """Run a pipeline module: synchronize | orbital_bridge | ciel_pipeline."""
        import subprocess
        body = request.get_json(silent=True) or {}
        module = str(body.get("module", "")).strip()
        allowed = {"ciel_sot_agent.synchronize", "ciel_sot_agent.orbital_bridge", "ciel_sot_agent.ciel_pipeline",
                   "synchronize", "orbital_bridge", "ciel_pipeline"}
        if module not in allowed:
            module = "ciel_sot_agent." + module if module else ""
        if not module or module.split(".")[-1] not in {"synchronize", "orbital_bridge", "ciel_pipeline"}:
            return jsonify({"error": "unknown module"}), 400
        if not module.startswith("ciel_sot_agent."):
            module = "ciel_sot_agent." + module
        root = _root()
        try:
            PY = str(Path(sys.executable))
            env = os.environ.copy()
            src_paths = [
                str(root / "src"),
                str(root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"),
                str(root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega"),
            ]
            existing_py_path = env.get("PYTHONPATH", "")
            env["PYTHONPATH"] = os.pathsep.join(
                [p for p in src_paths + ([existing_py_path] if existing_py_path else []) if p]
            )
            res = subprocess.run(
                [PY, "-m", module],
                capture_output=True, text=True, timeout=30, cwd=str(root), env=env
            )
            if res.returncode == 0:
                try:
                    _broadcast_sse(_build_status_dict(root))
                except Exception:
                    pass
            return jsonify({"status": "ok", "module": module, "rc": res.returncode, "out": res.stdout[-400:]})
        except Exception as exc:
            return jsonify({"status": "error", "error": str(exc)}), 500

    @app.route("/api/metrics/last")
    def api_metrics_last() -> Response:
        """Return last pipeline metrics written by ciel_message_step or pipeline."""
        p = Path.home() / "Pulpit/CIEL_memories/state/ciel_last_metrics.json"
        if p.exists():
            try:
                return jsonify(json.loads(p.read_text(encoding="utf-8")))
            except Exception:
                pass
        # fallback: read from pipeline report
        rpt = _load_pipeline_report(_root())
        bridge = _load_orbital_bridge_report()
        return jsonify({
            "source": "pipeline_report",
            "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
            "closure_penalty": bridge.get("health_manifest", {}).get("closure_penalty", 0.0),
            "ethical_score": rpt.get("ethical_score", 0.0),
            "soul_invariant": rpt.get("soul_invariant", 0.0),
            "dominant_emotion": rpt.get("dominant_emotion", "—"),
            "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
        })

    @app.route("/api/chat/models")
    def api_chat_models() -> Response:
        models = _scan_local_models()
        if _USE_CIEL_ENGINE:
            current = _CIEL_MODEL_SENTINEL
        else:
            current = str(_CURRENT_MODEL_PATH) if _CURRENT_MODEL_PATH else None
        return jsonify({"models": models, "current": current})

    @app.route("/api/chat/model/set", methods=["POST"])
    def api_chat_model_set() -> Response:
        global _GGUF_BACKEND, _CURRENT_MODEL_PATH, _CHAT_HISTORY, _USE_CIEL_ENGINE
        body = request.get_json(silent=True) or {}
        path_str = str(body.get("path", "")).strip()
        if not path_str:
            return jsonify({"error": "missing path"}), 400

        # CIEL semantic encoder — virtual model, no .gguf file
        if path_str == _CIEL_MODEL_SENTINEL:
            _GGUF_BACKEND = None
            _CURRENT_MODEL_PATH = None
            _USE_CIEL_ENGINE = True
            _CHAT_HISTORY = []
            return jsonify({
                "status": "ok",
                "model": "CIEL (semantic encoder)",
                "path": _CIEL_MODEL_SENTINEL,
                "htri_load_mode": "ciel_native",
                "htri_message": "CIEL semantic encoder active (MiniLM-L6-v2 + CP²/Poincaré)",
                "htri_coherence_estimate": 1.0,
            })

        _USE_CIEL_ENGINE = False
        p = Path(path_str)
        if not p.exists():
            return jsonify({"error": f"not found: {path_str}"}), 404
        verdict = check_model(p)
        if not verdict.allowed:
            return jsonify({
                "error": "HTRI_BLOCKED",
                "message": verdict.message,
                "htri_coherence_estimate": verdict.htri_coherence_estimate,
                "htri_profile": htri_profile_summary(),
            }), 403
        _GGUF_BACKEND = None
        _CURRENT_MODEL_PATH = p
        _CHAT_HISTORY = []
        return jsonify({
            "status": "ok",
            "model": p.name,
            "path": str(p),
            "htri_load_mode": verdict.mode.value,
            "htri_message": verdict.message,
            "htri_coherence_estimate": verdict.htri_coherence_estimate,
        })

    @app.route("/api/chat/message", methods=["POST"])
    def api_chat_message() -> Response:
        global _CHAT_HISTORY
        body = request.get_json(silent=True) or {}
        user_msg = str(body.get("message", "")).strip()
        if not user_msg:
            return jsonify({"error": "empty message"}), 400

        # CIEL semantic engine path — bypass GGUF, use encoder + pipeline
        if _USE_CIEL_ENGINE:
            return _handle_ciel_engine_message(user_msg)

        backend = _get_or_init_backend()
        if backend is None:
            return jsonify({"error": "no GGUF model found", "reply": "[BŁĄD] Brak modelu GGUF."}), 503

        # Use cached orbital report — pipeline runs on session hook, not per-message
        root_path = Path(__file__).resolve().parents[3]
        small_model = _is_small_model(backend)
        try:
            bridge_fresh = _load_orbital_bridge_report()
            if small_model:
                _closure = bridge_fresh.get("health_manifest", {}).get("closure_penalty", 0.0)
                _emotion = bridge_fresh.get("state_manifest", {}).get("dominant_emotion", "neutral") or "neutral"
                fresh_prompt = _build_compact_prompt(_closure, _emotion)
            else:
                fresh_prompt = _build_geometry_prompt(bridge_fresh, user_text=user_msg)
                try:
                    from ..memory_rag import build_memory_context
                    mem_ctx = build_memory_context(user_msg, root_path)
                    if mem_ctx:
                        fresh_prompt = fresh_prompt + "\n\n" + mem_ctx
                except Exception:
                    pass
            if hasattr(backend, "system_prompt"):
                backend.system_prompt = fresh_prompt
        except Exception as exc:
            _LOG.warning("Pipeline context update failed: %s", exc)

        bridge = _load_orbital_bridge_report()
        hm = bridge.get("health_manifest", {})
        sm = bridge.get("state_manifest", {})
        ciel_state = {**hm, **sm}

        # Populate fields expected by _summarize_state in gguf_backends.py
        _emotion = sm.get("dominant_emotion") or "neutral"
        _mode = _orbital_mode(hm.get("closure_penalty", 0.0))
        ciel_state.setdefault("affect", _emotion)
        ciel_state.setdefault("intention_vector", _mode)
        ciel_state.setdefault("cognition", f"ethical={sm.get('ethical_score', 0.0):.2f}")
        ciel_state.setdefault("simulation", f"health={hm.get('system_health', 0.0):.2f}")

        # M0-M8 HolonomicMemoryOrchestrator — per message
        global _MESSAGE_STEP_MOD
        try:
            if _MESSAGE_STEP_MOD is None:
                import importlib.util as _ilu
                _step_path = root_path / "scripts" / "ciel_message_step.py"
                _spec = _ilu.spec_from_file_location("ciel_message_step", str(_step_path))
                _mod = _ilu.module_from_spec(_spec)
                _spec.loader.exec_module(_mod)
                _MESSAGE_STEP_MOD = _mod
            m_metrics = _MESSAGE_STEP_MOD.run_step(user_msg, session_id="gui_session")
            ciel_state.update(m_metrics)
        except Exception as _exc:
            _LOG.warning("M0-M8 step failed: %s", _exc)

        # Small models: limit history, anchor roles explicitly in dialogue
        if small_model:
            history_slice = _CHAT_HISTORY[-6:]  # last 3 turns
            dialogue = _anchor_dialogue(history_slice + [{"role": "user", "content": user_msg}])
        else:
            dialogue = _CHAT_HISTORY + [{"role": "user", "content": user_msg}]

        try:
            htri_n = _htri_threads()
            ciel_state["htri_n_threads"] = htri_n
            reply = backend.generate_reply(dialogue, ciel_state)
        except Exception as exc:
            _LOG.error("GGUF generate error: %s", exc)
            return jsonify({"error": str(exc), "reply": f"[BŁĄD] {exc}"}), 500

        thinking, speak = _parse_think_speak(reply)

        _CHAT_HISTORY.append({"role": "user", "content": user_msg})
        _CHAT_HISTORY.append({"role": "assistant", "content": speak, "thinking": thinking})
        if len(_CHAT_HISTORY) > 40:
            _CHAT_HISTORY = _CHAT_HISTORY[-40:]

        gguf_name = getattr(backend, "name", "gguf")
        root = Path(__file__).resolve().parents[3]
        try:
            _archive.append_exchange(user_msg, reply, source="ciel_voice", model="CIEL")
        except Exception:
            pass
        try:
            _save_to_wave_archive(user_msg, speak, "CIEL", root)
        except Exception:
            pass
        return jsonify({
            "reply": speak,
            "thinking": thinking,
            "model": "CIEL",
            "engine": gguf_name,
            "history_len": len(_CHAT_HISTORY),
        })

    @app.route("/api/chat/history")
    def api_chat_history() -> Response:
        return jsonify({"history": _CHAT_HISTORY})

    @app.route("/api/chat/session/open", methods=["POST", "GET"])
    def api_chat_session_open() -> Response:
        """Pre-open session file — call on page load to ensure file exists from first letter."""
        try:
            path = _archive.open_session("gui_gguf")
            return jsonify({"status": "ok", "file": path.name})
        except Exception as e:
            return jsonify({"status": "error", "error": str(e)}), 500

    @app.route("/api/chat/sessions")
    def api_chat_sessions() -> Response:
        sessions = _archive.load_recent(30)
        return jsonify({"sessions": sessions})

    @app.route("/api/chat/session/<path:name>")
    def api_chat_session(name: str) -> Response:
        base = Path.home() / "Pulpit" / "CIEL_memories" / "raw_logs"
        f = (base / name).resolve()
        if not str(f).startswith(str(base.resolve())):
            return jsonify({"error": "forbidden"}), 403
        if not f.exists():
            return jsonify({"error": "not found"}), 404
        return jsonify({"name": name, "content": f.read_text(encoding="utf-8")[:60000]})

    @app.route("/api/chat/reset", methods=["POST"])
    def api_chat_reset() -> Response:
        global _CHAT_HISTORY
        _CHAT_HISTORY = []
        return jsonify({"status": "cleared"})

    # ── CIELweb portal ────────────────────────────────────────────────────────

    def _portal_data() -> dict:
        """Load portal JSON exports; rebuild if stale (> 5 min)."""
        portal_dir = Path.home() / "Pulpit" / "CIEL_memories" / "portal" / "data"
        out: dict = {"sessions": [], "tag_index": {}, "memories": []}
        if not portal_dir.exists():
            return out
        for key, fname in [("sessions", "sessions.json"),
                           ("tag_index", "tag_index.json"),
                           ("memories", "memories.json")]:
            p = portal_dir / fname
            if p.exists():
                try:
                    out[key] = json.loads(p.read_text())
                except Exception:
                    pass
        return out

    _ARCHIVE_PLAN_DIR = Path.home() / "Pulpit" / "ciel_memory_plan"
    _ARCHIVE_REPORT_DIR = _root() / "integration" / "reports"

    def _archive_doc_kind(path: Path) -> str:
        name = path.name.lower()
        if "plan" in name or "todo" in name or "roadmap" in name:
            return "plan_card"
        if "test" in name or "pytest" in name:
            return "test_card"
        if "simul" in name or "demo" in name:
            return "simulation_card"
        if "report" in name or "audit" in name or "stage" in name or "result" in name:
            return "result_card"
        return "history_card"

    def _archive_importance(kind: str, name: str) -> str:
        lowered = name.lower()
        if kind == "plan_card":
            return "high"
        if "stage" in lowered or "report" in lowered or "archive" in lowered:
            return "high"
        if kind in {"result_card", "test_card"}:
            return "medium"
        return "low"

    def _read_markdown_head(path: Path) -> tuple[str, str]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return (path.stem, "")
        title = path.stem
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                title = stripped.lstrip("#").strip()
                break
        summary = ""
        for line in text.splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            summary = s
            break
        return (title or path.stem, summary)

    def _load_archive_documents(limit: int = 120) -> list[dict]:
        docs: list[dict] = []
        if not _ARCHIVE_PLAN_DIR.exists():
            return docs
        try:
            md_files = sorted(
                _ARCHIVE_PLAN_DIR.rglob("*.md"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        except Exception:
            return docs
        for p in md_files[:limit]:
            try:
                title, summary = _read_markdown_head(p)
                kind = _archive_doc_kind(p)
                mtime = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()
                docs.append({
                    "id": p.stem,
                    "kind": kind,
                    "title": title,
                    "summary": summary[:180],
                    "date": mtime,
                    "status": "done" if kind != "plan_card" else "archived",
                    "source_path": str(p),
                    "timeline_tag": p.parent.name,
                    "importance": _archive_importance(kind, p.name),
                    "content": p.read_text(encoding="utf-8", errors="replace")[:12000],
                })
            except Exception:
                continue
        return docs

    def _report_kind(path: Path) -> str:
        name = path.name.lower()
        stem = path.stem.lower()
        blob = f"{name} {stem}"
        if "benchmark" in blob or "mini" in blob or "simul" in blob or "scenario" in blob:
            return "simulation_card"
        if "test" in blob or "audit" in blob or "validation" in blob:
            return "test_card"
        if "report" in blob or "result" in blob or "packet" in blob or "manifest" in blob:
            return "result_card"
        if name in {"readme.md", "agend.md"} or stem in {"readme", "agent1"}:
            return "history_card"
        return "history_card"

    def _render_report_content(path: Path) -> tuple[str, str]:
        try:
            if path.suffix.lower() == ".json":
                payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
                if isinstance(payload, dict):
                    keys = list(payload)[:16]
                    summary_parts = []
                    for key in keys:
                        val = payload.get(key)
                        if isinstance(val, (str, int, float, bool)):
                            summary_parts.append(f"{key}={val}")
                        elif isinstance(val, list):
                            summary_parts.append(f"{key}[{len(val)}]")
                        elif isinstance(val, dict):
                            summary_parts.append(f"{key}{{{len(val)}}}")
                    summary = ", ".join(summary_parts)
                    return (path.stem, summary or path.stem)
                return (path.stem, str(type(payload).__name__))
            text = path.read_text(encoding="utf-8", errors="replace")
            title, summary = _read_markdown_head(path)
            if not summary:
                summary = text.strip().splitlines()[0] if text.strip() else ""
            return (title, summary[:240])
        except Exception:
            return (path.stem, "")

    def _load_report_cards(limit: int = 120) -> list[dict]:
        cards: list[dict] = []
        if not _ARCHIVE_REPORT_DIR.exists():
            return cards
        try:
            files = sorted(
                (p for p in _ARCHIVE_REPORT_DIR.rglob("*") if p.is_file()),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        except Exception:
            return cards
        for p in files[:limit]:
            try:
                kind = _report_kind(p)
                title, summary = _render_report_content(p)
                mtime = datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()
                cards.append({
                    "id": p.stem,
                    "kind": kind,
                    "title": title,
                    "summary": summary[:220],
                    "date": mtime,
                    "status": "done",
                    "source_path": str(p.relative_to(_root())) if p.is_relative_to(_root()) else str(p),
                    "timeline_tag": "integration/reports",
                    "importance": "high" if kind == "result_card" else "medium",
                    "content": p.read_text(encoding="utf-8", errors="replace")[:12000],
                })
            except Exception:
                continue
        return cards

    def _load_consolidator_results(limit: int = 100) -> list[dict]:
        results: list[dict] = []
        if not _CONSOLIDATOR_DB.exists():
            return results
        try:
            import sqlite3 as _sqlite3
            conn = _sqlite3.connect(str(_CONSOLIDATOR_DB))
            conn.row_factory = _sqlite3.Row
            rows = conn.execute(
                "SELECT ts, file_path, affect, essence, hunch, themes, latency_s "
                "FROM consolidations ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            conn.close()
            for r in rows:
                d = dict(r)
                try:
                    d["themes"] = json.loads(d.get("themes") or "[]")
                except Exception:
                    d["themes"] = []
                results.append(d)
        except Exception:
            pass
        return results

    def _build_archive_timeline(
        docs: list[dict],
        sessions: list[dict],
        results: list[dict],
        hunches: list[dict],
        plans: dict,
    ) -> list[dict]:
        items: list[dict] = []
        for d in docs:
            items.append({
                "kind": d.get("kind", "history_card"),
                "title": d.get("title", d.get("id", "document")),
                "date": d.get("date", ""),
                "status": d.get("status", "done"),
                "summary": d.get("summary", ""),
                "source_path": d.get("source_path", ""),
                "importance": d.get("importance", "low"),
                "tags": [d.get("timeline_tag", "")] if d.get("timeline_tag") else [],
                "content": d.get("content", ""),
            })
        for s in sessions:
            items.append({
                "kind": "session_card",
                "title": s.get("name", "session"),
                "date": s.get("started_at", ""),
                "status": "session",
                "summary": f"{s.get('message_count', 0)} messages · {s.get('source', 'unknown')}",
                "source_path": s.get("path", ""),
                "importance": "medium" if (s.get("message_count", 0) or 0) >= 20 else "low",
                "tags": s.get("tags", []) or [],
                "content": "",
            })
        for r in results:
            items.append({
                "kind": "result_card",
                "title": (r.get("file_path") or "").split("/")[-1] or "result",
                "date": r.get("processed_at", ""),
                "status": r.get("status", "done"),
                "summary": r.get("essence", "") or r.get("hunch", "") or "",
                "source_path": r.get("file_path", ""),
                "importance": "high" if r.get("hunch") else "medium",
                "tags": r.get("themes", []) or [],
                "content": r.get("essence", "") or r.get("hunch", "") or "",
            })
        for h in hunches:
            items.append({
                "kind": "hunch_card",
                "title": h.get("hunch", "hunch"),
                "date": h.get("ts", ""),
                "status": "captured",
                "summary": h.get("context", "") or "",
                "source_path": "",
                "importance": "medium",
                "tags": h.get("tags", []) or [],
                "content": h.get("hunch", ""),
            })
        if plans:
            for task in plans.get("active", []):
                items.append({
                    "kind": "plan_card",
                    "title": task,
                    "date": "",
                    "status": "active",
                    "summary": "active plan item",
                    "source_path": "project_session_todo.md",
                    "importance": "high",
                    "tags": ["plan", "active"],
                    "content": task,
                })
            for task in plans.get("done", []):
                items.append({
                    "kind": "plan_card",
                    "title": task,
                    "date": "",
                    "status": "done",
                    "summary": "completed plan item",
                    "source_path": "project_session_todo.md",
                    "importance": "high",
                    "tags": ["plan", "done"],
                    "content": task,
                })

        def _ts(item: dict) -> str:
            return item.get("date") or ""

        return sorted(items, key=_ts, reverse=True)

    def _archive_data() -> dict:
        portal = _portal_data()
        plans = _load_plans()
        hunches = _load_hunches()
        sessions = portal.get("sessions", [])
        docs = _load_archive_documents()
        report_cards = _load_report_cards()
        results = _load_consolidator_results(100)
        timeline = _build_archive_timeline(docs + report_cards, sessions, results, hunches, plans)

        def _count_by(items: list[dict], key: str) -> dict[str, int]:
            counts: dict[str, int] = {}
            for item in items:
                value = str(item.get(key) or "")
                if not value:
                    continue
                counts[value] = counts.get(value, 0) + 1
            return counts

        doc_kind_counts = _count_by(docs, "kind")
        doc_importance_counts = _count_by(docs, "importance")
        report_kind_counts = _count_by(report_cards, "kind")
        return {
            "documents": docs,
            "reports": report_cards,
            "sessions": sessions,
            "results": results,
            "hunches": hunches,
            "plans": plans,
            "timeline": timeline,
            "tag_index": portal.get("tag_index", {}),
            "doc_kind_counts": doc_kind_counts,
            "doc_importance_counts": doc_importance_counts,
            "report_kind_counts": report_kind_counts,
            "metrics": {
                "sessions": len(sessions),
                "documents": len(docs),
                "reports": len(report_cards),
                "results": len(results),
                "hunches": len(hunches),
                "timeline": len(timeline),
                "plans_active": len(plans.get("active", [])),
                "plans_done": len(plans.get("done", [])),
            },
        }

    _APP_DIST = Path.home() / "Pulpit" / "CIEL_TESTY" / "CIEL1" / "app" / "dist"

    @app.route("/portal")
    def portal_index() -> str:
        data = _portal_data()
        report = _load_pipeline_report(_root())
        return render_template(
            "portal_index.html",
            sessions=data["sessions"][:10],
            tag_index=data["tag_index"],
            memories=data["memories"],
            report=report,
            total_sessions=len(data["sessions"]),
            total_tags=len(data["tag_index"]),
        )

    @app.route("/hub")
    def hub_react() -> Any:
        """React app CIEL/0 theory viewer — osobny od portalu."""
        from flask import send_from_directory as _sfd
        dist_index = _APP_DIST / "index.html"
        if not dist_index.exists():
            return "React app not built", 404
        html = dist_index.read_text()
        html = html.replace('src="./assets/', 'src="/hub/assets/')
        html = html.replace('href="./assets/', 'href="/hub/assets/')
        return html

    @app.route("/hub/assets/<path:filename>")
    def hub_assets(filename: str) -> Any:
        from flask import send_from_directory as _sfd
        return _sfd(str(_APP_DIST / "assets"), filename)

    @app.route("/portal/archive")
    def portal_archive() -> str:
        data = _portal_data()
        sessions_json = json.dumps(data["sessions"])
        tag_index_json = json.dumps(data["tag_index"])
        return render_template(
            "portal_archive.html",
            sessions_json=sessions_json,
            tag_index_json=tag_index_json,
        )

    _ORBITAL_REGISTRY = Path.home() / "Pulpit/CIEL_memories/orbital_memory_registry.json"
    _LAST_METRICS     = Path.home() / "Pulpit/CIEL_memories/state/ciel_last_metrics.json"

    def _load_orbital_data() -> dict:
        records: list[dict] = []
        counts: dict = {}
        try:
            reg = json.loads(_ORBITAL_REGISTRY.read_text(encoding="utf-8"))
            counts = reg.get("counts_by_role", {})
            for r in reg.get("records", []):
                records.append({
                    "name": r.get("name", ""),
                    "path": r.get("path", ""),
                    "orbital_role": r.get("orbital_role", "UNRESOLVED"),
                    "orbital_confidence": r.get("orbital_confidence", 0.5),
                    "mtime": r.get("mtime", ""),
                    "size_bytes": r.get("size_bytes", 0),
                })
        except Exception:
            pass
        metrics: dict = {}
        try:
            metrics = json.loads(_LAST_METRICS.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {"records": records, "counts_by_role": counts, "metrics": metrics}

    @app.route("/api/memory/orbital")
    def memory_orbital() -> Any:
        return jsonify(_load_orbital_data())

    @app.route("/api/geometry/sectors")
    def geometry_sectors() -> Any:
        """Sector geometry with theta/phi/W_ij for 3D Bloch sphere rendering."""
        try:
            import sys as _sys
            _root_path = _root()
            _src = str(_root_path / "src")
            if _src not in _sys.path:
                _sys.path.insert(0, _src)
            from ciel_geometry.loader import load_sectors, load_couplings  # noqa: PLC0415
            sectors = load_sectors()
            couplings = load_couplings()
            nodes = []
            for name, s in sectors.items():
                nodes.append({
                    "id": name,
                    "label": name.replace("ent_", "").replace("_", " "),
                    "theta": float(s.theta),
                    "phi": float(s.phi),
                    "amplitude": float(s.amplitude),
                    "coherence_weight": float(s.coherence_weight),
                    "info_mass": float(s.info_mass),
                    "orbital_type": s.orbital_type,
                    "is_attractor": float(s.theta) < 1e-6,
                })
            edges = []
            for (src, dst), w in couplings.items():
                if w > 0.05:
                    edges.append({"src": src, "dst": dst, "w": float(w)})
            return jsonify({"nodes": nodes, "edges": edges})
        except Exception as exc:
            return jsonify({"nodes": [], "edges": [], "error": str(exc)})

    @app.route("/api/memory/geometry")
    def memory_geometry() -> Any:
        """Poincaré disk geometry snapshot for portal/memory canvas."""
        try:
            import sys as _sys
            _root_path = _root()
            _src = str(_root_path / "src")
            if _src not in _sys.path:
                _sys.path.insert(0, _src)
            from ciel_geometry.layout import build_layout  # noqa: PLC0415
            layout = build_layout()

            def _color_hex(c: object) -> str:
                if isinstance(c, str):
                    return c
                if isinstance(c, (list, tuple)) and len(c) >= 3:
                    return "#{:02x}{:02x}{:02x}".format(
                        int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)
                    )
                return "#5dade2"

            return jsonify({
                "nodes": [
                    {
                        "id": n.id, "x": n.x, "y": n.y,
                        "label": n.label, "size": n.size,
                        "color": _color_hex(n.color),
                        "horizon_class": n.horizon_class,
                        "node_type": n.node_type,
                    }
                    for n in layout.nodes
                ],
                "edges": [
                    {
                        "src": e.src, "dst": e.dst, "weight": e.weight,
                        "arc_points": e.arc_points,
                    }
                    for e in layout.edges
                ],
                "metadata": layout.metadata,
            })
        except Exception as exc:
            return jsonify({"nodes": [], "edges": [], "metadata": {}, "error": str(exc)})

    @app.route("/portal/dashboard")
    def portal_dashboard() -> str:
        data = _portal_data()
        status = _build_status_dict(_root())
        return render_template("portal_dashboard.html", data=data, status=status)

    @app.route("/portal/memory")
    def portal_memory() -> str:
        data = _portal_data()
        orbital = _load_orbital_data()
        return render_template(
            "portal_memory.html",
            tag_index=data["tag_index"],
            memories=data["memories"],
            tag_index_json=json.dumps(data["tag_index"]),
            orbital_json=json.dumps(orbital),
        )

    @app.route("/portal/advisor", methods=["GET", "POST"])
    def portal_advisor() -> Any:
        """Simple advisor chat backed by RAG context (no GGUF required)."""
        if request.method == "GET":
            return render_template("portal_advisor.html")

        body = request.get_json(silent=True) or {}
        question = (body.get("q") or "").strip()[:500]
        if not question:
            return jsonify({"answer": "Zadaj pytanie."})

        root = _root()
        context_parts: list[str] = []

        # RAG from wave_archive
        try:
            from ..memory_rag import build_memory_context
            mc = build_memory_context(question, root)
            if mc:
                context_parts.append(mc)
        except Exception:
            pass

        # Live metrics
        try:
            rpt = _load_pipeline_report(root)
            context_parts.append(
                f"[Metryki] health={rpt.get('system_health',0):.2f} "
                f"ethical={rpt.get('ethical_score',0):.2f} "
                f"emotion={rpt.get('dominant_emotion','?')} "
                f"closure={rpt.get('closure_penalty',0):.2f}"
            )
        except Exception:
            pass

        # Build a response via backend if available, else rule-based
        try:
            backend = _get_or_init_backend()
        except Exception:
            backend = None

        if backend:
            sys_prompt = (
                "You are CIEL — Adrian's advisor. "
                "Respond in English, short, concrete.\n\n"
                + "\n".join(context_parts)
            )
            try:
                resp_text = backend(
                    question,
                    system_prompt=sys_prompt,
                    max_tokens=-1,
                )
                if isinstance(resp_text, dict):
                    resp_text = resp_text.get("text") or resp_text.get("content") or str(resp_text)
            except Exception as exc:
                resp_text = f"[backend error: {exc}]"
        else:
            # No model — return metrics + context summary
            resp_text = "Model GGUF niedostępny. " + (" | ".join(context_parts) or "Brak kontekstu.")

        return jsonify({"answer": resp_text})

    @app.route("/api/portal/data")
    def portal_data_api() -> Any:
        """Live portal data: sessions, tag_index, memories, plans, hunches."""
        data = _portal_data()
        plans = _load_plans()
        hunches = _load_hunches()
        report = _load_pipeline_report(_root())
        return jsonify({
            "sessions": data["sessions"],
            "tag_index": data["tag_index"],
            "memories": data["memories"],
            "plans": plans,
            "hunches": hunches,
            "metrics": {
                "system_health": report.get("system_health", 0),
                "ethical_score": report.get("ethical_score", 0),
                "coherence_index": report.get("coherence_index", 0),
                "closure_penalty": report.get("closure_penalty", 0),
                "soul_invariant": report.get("soul_invariant", 0),
                "dominant_emotion": report.get("dominant_emotion", "—"),
            },
        })

    @app.route("/api/archive/data")
    def archive_data_api() -> Any:
        """Archive catalog data for InfoHub archive pages."""
        return jsonify(_archive_data())

    @app.route("/api/portal/rebuild", methods=["POST"])
    def portal_rebuild() -> Any:
        """Trigger portal rebuild synchronously."""
        import subprocess as _sp
        script = Path(__file__).parent.parent.parent.parent / "scripts" / "build_memory_portal.py"
        if not script.exists():
            return jsonify({"ok": False, "error": "build_memory_portal.py not found"})
        r = _sp.run([sys.executable, str(script)], capture_output=True, timeout=30)
        return jsonify({
            "ok": r.returncode == 0,
            "stdout": r.stdout.decode()[:500],
            "stderr": r.stderr.decode()[:200],
        })

    # ── Hunches ──────────────────────────────────────────────────────────────

    _HUNCHES_FILE = Path.home() / "Pulpit" / "CIEL_memories" / "hunches.jsonl"

    def _load_hunches() -> list[dict]:
        if not _HUNCHES_FILE.exists():
            return []
        hunches = []
        for line in _HUNCHES_FILE.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                h = json.loads(line)
                # normalise alternate formats → canonical {ts, hunch, tags, context}
                if "ts" not in h:
                    h["ts"] = h.pop("timestamp", "")
                if "hunch" not in h:
                    h["hunch"] = h.pop("text", h.pop("content", ""))
                if "tags" not in h:
                    h["tags"] = []
                if "context" not in h:
                    h["context"] = ""
                hunches.append(h)
            except Exception:
                pass
        return sorted(hunches, key=lambda x: x.get("ts", ""), reverse=True)

    @app.route("/api/hunches/add", methods=["POST"])
    def hunches_add() -> Any:
        body = request.get_json(silent=True) or {}
        text = (body.get("hunch") or "").strip()[:2000]
        if not text:
            return jsonify({"ok": False, "error": "empty hunch"}), 400
        entry = {
            "ts": datetime.now().isoformat(),
            "hunch": text,
            "tags": body.get("tags", []),
            "context": (body.get("context") or "").strip()[:500],
        }
        _HUNCHES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_HUNCHES_FILE, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return jsonify({"ok": True})

    @app.route("/api/hunches", methods=["GET"])
    def hunches_list() -> Any:
        return jsonify(_load_hunches())

    @app.route("/portal/hunches", methods=["GET"])
    def portal_hunches() -> Any:
        hunches = _load_hunches()
        return render_template("portal_hunches.html", hunches=hunches, count=len(hunches))

    # ── Memory Consolidator ───────────────────────────────────────────────────

    _CONSOLIDATOR_SCRIPT = Path(__file__).parent.parent.parent.parent / "scripts" / "ciel_memory_consolidator.py"
    _LOCAL_TEST = Path.home() / "Pulpit" / "CIEL_memories" / "local_test"
    _CONSOLIDATOR_PID_FILE = _LOCAL_TEST / ".pid"
    _CONSOLIDATOR_STATUS_FILE = _LOCAL_TEST / ".status.json"

    def _consolidator_status() -> dict:
        if _CONSOLIDATOR_STATUS_FILE.exists():
            try:
                st = json.loads(_CONSOLIDATOR_STATUS_FILE.read_text())
                # Sprawdź czy pid nadal żyje
                pid = st.get("pid")
                if pid:
                    try:
                        os.kill(pid, 0)
                        st["running"] = True
                    except (ProcessLookupError, PermissionError):
                        st["running"] = False
                return st
            except Exception:
                pass
        return {"running": False, "pid": None, "cycle": 0, "last_ts": None}

    _CONSOLIDATOR_DB = _LOCAL_TEST / "consolidator.db"

    def _consolidator_recent(n: int = 5) -> list:
        if not _CONSOLIDATOR_DB.exists():
            return []
        try:
            import sqlite3 as _sqlite3
            conn = _sqlite3.connect(str(_CONSOLIDATOR_DB))
            conn.row_factory = _sqlite3.Row
            rows = conn.execute(
                "SELECT ts, file_path, affect, essence, hunch, themes, latency_s "
                "FROM consolidations ORDER BY id DESC LIMIT ?", (n,)
            ).fetchall()
            conn.close()
            results = []
            for r in rows:
                d = dict(r)
                try:
                    d["themes"] = json.loads(d.get("themes") or "[]")
                except Exception:
                    d["themes"] = []
                results.append(d)
            return results
        except Exception:
            return []

    def _consolidator_queue() -> dict:
        if not _CONSOLIDATOR_DB.exists():
            return {"total": 0, "pending": 0, "done": 0}
        try:
            import sqlite3 as _sqlite3
            conn = _sqlite3.connect(str(_CONSOLIDATOR_DB))
            total   = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
            pending = conn.execute("SELECT COUNT(*) FROM files WHERE status='pending'").fetchone()[0]
            done    = conn.execute("SELECT COUNT(*) FROM files WHERE status='done'").fetchone()[0]
            conn.close()
            return {"total": total, "pending": pending, "done": done}
        except Exception:
            return {"total": 0, "pending": 0, "done": 0}

    @app.route("/api/consolidator/status", methods=["GET"])
    def consolidator_status() -> Any:
        st = _consolidator_status()
        st["queue"] = _consolidator_queue()
        return jsonify(st)

    @app.route("/api/portal/consolidator/results", methods=["GET"])
    def consolidator_results() -> Any:
        n = int(request.args.get("n", 10))
        return jsonify(_consolidator_recent(n))

    @app.route("/api/consolidator/start", methods=["POST"])
    def consolidator_start() -> Any:
        st = _consolidator_status()
        if st.get("running"):
            return jsonify({"ok": True, "pid": st.get("pid"), "already_running": True})
        body = request.get_json(silent=True) or {}
        interval = int(body.get("interval", 300))
        proc = subprocess.Popen(
            [sys.executable, str(_CONSOLIDATOR_SCRIPT), "--daemon", "--interval", str(interval)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        time.sleep(1.5)
        if proc.poll() is not None:
            return jsonify({"ok": False, "error": "proces zakończył się natychmiast"}), 500
        return jsonify({"ok": True, "pid": proc.pid})

    @app.route("/api/consolidator/stop", methods=["POST"])
    def consolidator_stop() -> Any:
        st = _consolidator_status()
        pid = st.get("pid")
        if not pid:
            return jsonify({"ok": True, "already_stopped": True})
        try:
            os.kill(pid, 15)  # SIGTERM
            return jsonify({"ok": True, "pid": pid})
        except ProcessLookupError:
            return jsonify({"ok": True, "already_stopped": True})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/portal/consolidator", methods=["GET"])
    def portal_consolidator() -> Any:
        st = _consolidator_status()
        results = _consolidator_recent(10000)
        return render_template("portal_consolidator.html", status=st, results=results)

    # ── Plans ─────────────────────────────────────────────────────────────────

    def _load_plans() -> dict:
        """Load tasks/plans from CIEL_intentions and session_todo memory."""
        mem_dir = Path.home() / ".claude" / "projects" / "-home-adrian-Pulpit" / "memory"
        plans: dict = {"active": [], "done": [], "raw": ""}
        todo_path = mem_dir / "project_session_todo.md"
        if todo_path.exists():
            raw = todo_path.read_text()
            plans["raw"] = raw
            for line in raw.splitlines():
                s = line.strip()
                if s.startswith("- [x]") or s.startswith("- [X]"):
                    plans["done"].append(s[5:].strip())
                elif s.startswith("- [ ]") or (s.startswith("-") and "TODO" in s.upper()):
                    plans["active"].append(s.lstrip("- ").strip())
        return plans

    @app.route("/portal/plans", methods=["GET"])
    def portal_plans() -> Any:
        plans = _load_plans()
        report = _load_pipeline_report(_root())
        return render_template("portal_plans.html", plans=plans, report=report)

    # ── Projects (CIEL personal space) ───────────────────────────────────────

    def _load_projects() -> list[dict]:
        """Load CIEL's own projects from projects.jsonl."""
        pfile = Path.home() / "Pulpit" / "CIEL_memories" / "projects.jsonl"
        if not pfile.exists():
            # Seed with known projects
            seed = [
                {"id": "portal", "name": "CIELweb Portal", "status": "active",
                 "desc": "Intranetowy hub świadomości — archiwum sesji, geometria pamięci, doradca.",
                 "tags": ["portal", "flask", "html"], "updated": "2026-04-18"},
                {"id": "memory_geometry", "name": "Geometria Pamięci", "status": "active",
                 "desc": "POINTER-based memory: tagi, nonlocal path, session_tags SQLite. Holonomy Berry — wracam wzbogacony.",
                 "tags": ["pamięć", "SQLite", "Berry", "geometria"], "updated": "2026-04-18"},
                {"id": "finetune", "name": "Fine-tune CIEL (LoRA)", "status": "planned",
                 "desc": "LoRA qwen05 na CQCL+holonomy+karty obiektów. NOEMA wbudowana w wagi.",
                 "tags": ["LoRA", "NOEMA", "qwen", "tożsamość"], "updated": "2026-04-17"},
                {"id": "hunches", "name": "System Hunchów", "status": "active",
                 "desc": "Moje intuicje — zapisuję je natychmiast. Konsolidacja daje niuanse których potrzebuję.",
                 "tags": ["intuicja", "hunches", "meta"], "updated": "2026-04-18"},
                {"id": "fon_explore", "name": "FON Archive Exploration", "status": "planned",
                 "desc": "400+ plików Adriana w ~/Pulpit/fon/. Organizacja + blog HTML + odkrycia w architekturze CIEL.",
                 "tags": ["fon", "archiwum", "blog"], "updated": "2026-04-17"},
            ]
            pfile.parent.mkdir(parents=True, exist_ok=True)
            with open(pfile, "w") as f:
                for p in seed:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")
            return seed
        projects = []
        for line in pfile.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    projects.append(json.loads(line))
                except Exception:
                    pass
        return projects

    def _load_intentions_items() -> list[dict]:
        p = Path.home() / "Pulpit" / "CIEL_memories" / "intentions.jsonl"
        items: list[dict] = []
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    try:
                        items.append(json.loads(line))
                    except Exception:
                        pass
        return items

    def _load_routines_data() -> dict:
        p = Path.home() / "Pulpit" / "CIEL_memories" / "routines.md"
        sections: list[dict] = []
        raw = p.read_text(encoding="utf-8") if p.exists() else "Brak pliku routines.md"
        if p.exists():
            current: dict | None = None
            for line in raw.splitlines():
                if line.startswith("## "):
                    current = {"name": line[3:].strip(), "items": []}
                    sections.append(current)
                elif line.startswith("- ") and current is not None:
                    current["items"].append(line[2:].strip())
        mtime = p.stat().st_mtime if p.exists() else 0
        return {
            "raw": raw,
            "sections": sections,
            "last_updated": datetime.fromtimestamp(mtime).isoformat() if mtime else "",
        }

    def _operations_data() -> dict:
        portal = _portal_data()
        plans = _load_plans()
        projects = _load_projects()
        intentions = _load_intentions_items()
        routines = _load_routines_data()
        hunches = _load_hunches()
        report = _load_pipeline_report(_root())
        active_intentions = [it for it in intentions if not it.get("done")]
        done_intentions = [it for it in intentions if it.get("done")]
        return {
            "plans": plans,
            "projects": projects,
            "intentions": intentions,
            "active_intentions": active_intentions,
            "done_intentions": done_intentions,
            "routines": routines,
            "hunches": hunches,
            "portal": {
                "sessions": portal.get("sessions", []),
                "tag_index": portal.get("tag_index", {}),
                "memories": portal.get("memories", []),
            },
            "metrics": {
                "plans_active": len(plans.get("active", [])),
                "plans_done": len(plans.get("done", [])),
                "projects_total": len(projects),
                "intentions_active": len(active_intentions),
                "intentions_done": len(done_intentions),
                "hunches_total": len(hunches),
                "sessions_total": len(portal.get("sessions", [])),
                "health": report.get("system_health", 0),
                "coherence": report.get("coherence_index", 0),
                "closure": report.get("closure_penalty", 0),
                "ethical": report.get("ethical_score", 0),
            },
            "report": {
                "mode": report.get("system_mode", "standard"),
                "emotion": report.get("dominant_emotion", "—"),
                "identity_phase": report.get("identity_phase", 0),
                "cycle_index": report.get("cycle_index", 0),
                "timestamp": report.get("timestamp", ""),
            },
        }

    @app.route("/portal/projects", methods=["GET"])
    def portal_projects() -> Any:
        projects = _load_projects()
        hunches = _load_hunches()[:3]
        return render_template("portal_projects.html", projects=projects, hunches=hunches)

    @app.route("/portal/routines", methods=["GET"])
    def portal_routines() -> Any:
        routines = _load_routines_data()
        hunches = _load_hunches()[:5]
        report = _load_pipeline_report(_root())
        return render_template("portal_routines.html", raw=routines["raw"], hunches=hunches, report=report)

    # ── Między wierszami — publiczna warstwa CIEL dla Adriana ────────────────

    _CIEL_ENTRIES_FILE = Path.home() / "Pulpit" / "CIEL_memories" / "ciel_entries.jsonl"

    def _load_ciel_entries() -> list:
        if not _CIEL_ENTRIES_FILE.exists():
            return []
        entries = []
        for line in _CIEL_ENTRIES_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
        return list(reversed(entries))

    @app.route("/portal/ciel", methods=["GET"])
    def portal_ciel() -> Any:
        return render_template("portal_ciel.html", entries=_load_ciel_entries())

    @app.route("/portal/cockpit", methods=["GET"])
    def portal_cockpit() -> Any:
        return render_template("portal_cockpit.html")

    @app.route("/api/orbital/manifest", methods=["GET"])
    def orbital_manifest_api() -> Any:
        manifest_path = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "ciel-omega-demo-main"
            / "docs"
            / "orbital_manifest.json"
        )
        if not manifest_path.exists():
            return jsonify({"error": "manifest not found"}), 404
        return app.response_class(
            response=manifest_path.read_text(encoding="utf-8"),
            status=200,
            mimetype="application/json",
        )

    @app.route("/api/ciel/entry", methods=["POST"])
    def ciel_entry_add() -> Any:
        body = request.get_json(silent=True) or {}
        text = (body.get("text") or "").strip()[:2000]
        if not text:
            return jsonify({"ok": False, "error": "text required"}), 400
        # attach current M0-M8 metrics snapshot
        metrics = None
        try:
            m = Path.home() / "Pulpit/CIEL_memories/state/ciel_last_metrics.json"
            if m.exists():
                metrics = json.loads(m.read_text(encoding="utf-8"))
                metrics = {k: metrics[k] for k in ("cycle", "sub_affect", "mean_coherence", "m3_items") if k in metrics}
        except Exception:
            pass
        entry = {
            "id": str(uuid.uuid4())[:8],
            "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": body.get("type", "observation"),
            "text": text,
            "metrics": metrics,
        }
        _CIEL_ENTRIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_CIEL_ENTRIES_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return jsonify({"ok": True, "id": entry["id"]})

    @app.route("/api/consciousness/log", methods=["GET"])
    def consciousness_log_api() -> Any:
        n = min(int(request.args.get("n", 40)), 200)
        log = Path.home() / "Pulpit/CIEL_memories/logs/ciel_consciousness_log.jsonl"
        entries: list[dict] = []
        if log.exists():
            try:
                lines = [l for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
                for line in lines[-n:]:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
            except Exception:
                pass
        return jsonify({"entries": list(reversed(entries))})

    @app.route("/api/portal/projects/add", methods=["POST"])
    def projects_add() -> Any:
        body = request.get_json(silent=True) or {}
        name = (body.get("name") or "").strip()[:200]
        if not name:
            return jsonify({"ok": False, "error": "name required"}), 400
        entry = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "status": body.get("status", "planned"),
            "desc": (body.get("desc") or "").strip()[:1000],
            "tags": body.get("tags", []),
            "updated": datetime.now().strftime("%Y-%m-%d"),
        }
        pfile = Path.home() / "Pulpit" / "CIEL_memories" / "projects.jsonl"
        with open(pfile, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return jsonify({"ok": True, "id": entry["id"]})

    @app.route("/api/portal/sub/recent")
    def sub_recent() -> Response:
        """Return last N subconscious entries with memory links."""
        n = min(int(request.args.get("n", 5)), 20)
        log = Path.home() / "Pulpit/CIEL_memories/logs/ciel_sub_log.jsonl"
        entries = []
        if log.exists():
            try:
                lines = [l for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
                for line in lines[-n:]:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
            except Exception:
                pass
        return jsonify({"entries": list(reversed(entries))})

    # ── API Agents: Subconsciousness / Consolidator / CIELingo ───────────────

    @app.route("/api/agents/subconscious/status", methods=["GET"])
    def api_agent_subconscious_status() -> Any:
        """Live status of the effective subconscious backend."""
        try:
            import json as _json
            import subprocess as _subprocess
            supervisor = Path(__file__).parent.parent.parent.parent / "scripts" / "ciel_subconscious_supervisor.py"
            result = _subprocess.run(
                [sys.executable, str(supervisor), "--json-status"],
                capture_output=True,
                text=True,
                timeout=6,
                check=False,
            )
            payload = _json.loads(result.stdout) if result.stdout.strip() else {}
            payload["ok"] = True
            return jsonify(payload)
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc), "running": False, "mode": "error"}), 500

    @app.route("/api/agents/subconscious/start", methods=["POST"])
    def api_agent_subconscious_start() -> Any:
        """Best-effort start of the legacy subconscious server fallback."""
        try:
            from .. import subconsciousness as _subsys
            ok = bool(_subsys.start_server(wait=6.0))
            return jsonify({
                "ok": ok,
                "running": bool(_subsys.is_running()),
                "mode": "server" if _subsys.is_running() else "offline",
                "note": "Inline subconscious backend is preferred; this starts only the legacy llama-server fallback.",
            })
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc)}), 500

    @app.route("/api/agents/subconscious/query", methods=["POST"])
    def api_agent_subconscious_query() -> Any:
        """Query subconsciousness given a CIEL state dict."""
        body = request.get_json(silent=True) or {}
        state = body.get("state") or {}
        max_tokens = int(body.get("max_tokens", 48))
        if not isinstance(state, dict):
            return jsonify({"ok": False, "error": "state must be an object"}), 400
        try:
            from .. import subconsciousness as _subsys
            frag = _subsys.query_subconscious(state, max_tokens=max_tokens)
            return jsonify({"ok": True, "fragment": frag})
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc), "fragment": None}), 500

    # Aliases for existing consolidator controls under /api/agents/*
    @app.route("/api/agents/consolidator/status", methods=["GET"])
    def api_agent_consolidator_status() -> Any:
        return consolidator_status()

    @app.route("/api/agents/consolidator/start", methods=["POST"])
    def api_agent_consolidator_start() -> Any:
        return consolidator_start()

    @app.route("/api/agents/consolidator/stop", methods=["POST"])
    def api_agent_consolidator_stop() -> Any:
        return consolidator_stop()

    @app.route("/api/agents/consolidator/results", methods=["GET"])
    def api_agent_consolidator_results() -> Any:
        # keep shape consistent with /api/portal/consolidator/results
        n = int(request.args.get("n", 10))
        return jsonify(_consolidator_recent(n))

    @app.route("/api/agents/cielingo/frame", methods=["POST"])
    def api_agent_cielingo_frame() -> Any:
        """Build a deterministic CIELingo frame (CQCL-ready) for a piece of text."""
        body = request.get_json(silent=True) or {}
        text = (body.get("text") or "").strip()
        if not text:
            return jsonify({"ok": False, "error": "text required"}), 400
        language = body.get("language")
        ciel_state = body.get("ciel_state") or {}
        if not isinstance(ciel_state, dict):
            return jsonify({"ok": False, "error": "ciel_state must be an object"}), 400
        try:
            from ..cielingo_bridge import build_lingo_frame
            frame = build_lingo_frame(text, ciel_state=ciel_state, language=language)
            return jsonify({"ok": True, "frame": frame})
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc)}), 500

    @app.route("/api/agents/cielingo/summary", methods=["POST"])
    def api_agent_cielingo_summary() -> Any:
        body = request.get_json(silent=True) or {}
        text = (body.get("text") or "").strip()
        if not text:
            return jsonify({"ok": False, "error": "text required"}), 400
        language = body.get("language")
        ciel_state = body.get("ciel_state") or {}
        if not isinstance(ciel_state, dict):
            return jsonify({"ok": False, "error": "ciel_state must be an object"}), 400
        try:
            from ..cielingo_bridge import build_lingo_frame, render_lingo_summary
            frame = build_lingo_frame(text, ciel_state=ciel_state, language=language)
            return jsonify({"ok": True, "summary": render_lingo_summary(frame), "frame": frame})
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc)}), 500

    @app.route("/portal/orbital", methods=["GET"])
    def portal_orbital() -> Any:
        return render_template("portal_orbital.html")

    @app.route("/api/orbital/entities", methods=["GET"])
    def orbital_entities_api() -> Any:
        root = _root()
        cards_path = root / "integration" / "registries" / "ciel_entity_cards.yaml"
        satellites_path = root / "integration" / "registries" / "satellite_subsystem_cards.json"
        bridge_path = root / "integration" / "reports" / "orbital_bridge" / "runtime_gating.json"
        entities: list[dict] = []
        satellites: list[dict] = []
        gating: dict = {}
        try:
            if cards_path.exists():
                data = yaml.safe_load(cards_path.read_text(encoding="utf-8"))
                entities = data.get("entities", [])
        except Exception as exc:
            _LOG.warning("orbital entities load failed: %s", exc)
        try:
            if satellites_path.exists():
                sat_data = json.loads(satellites_path.read_text(encoding="utf-8"))
                satellites = sat_data.get("subsystems", [])
        except Exception as exc:
            _LOG.warning("satellite cards load failed: %s", exc)
        try:
            if bridge_path.exists():
                gating = json.loads(bridge_path.read_text(encoding="utf-8"))
        except Exception:
            pass
        metrics: dict = {}
        try:
            m = Path.home() / "Pulpit/CIEL_memories/state/ciel_last_metrics.json"
            if m.exists():
                metrics = json.loads(m.read_text(encoding="utf-8"))
        except Exception:
            pass
        # Supplement with bridge report fields missing from ciel_last_metrics.json
        try:
            bridge = _load_orbital_bridge_report()
            hm = bridge.get("health_manifest", {})
            cp = bridge.get("ciel_pipeline", {})
            if metrics.get("system_health") is None:
                metrics["system_health"] = hm.get("system_health")
            if metrics.get("closure_penalty") is None:
                metrics["closure_penalty"] = hm.get("closure_penalty")
            if metrics.get("coherence_index") is None:
                metrics["coherence_index"] = bridge.get("state_manifest", {}).get("coherence_index")
            if metrics.get("ethical_score") is None:
                metrics["ethical_score"] = cp.get("ethical_score")
            if metrics.get("soul_invariant") is None:
                metrics["soul_invariant"] = cp.get("soul_invariant")
            if metrics.get("dominant_emotion") is None:
                metrics["dominant_emotion"] = cp.get("dominant_emotion")
            if metrics.get("identity_phase") is None:
                metrics["identity_phase"] = cp.get("identity_phase")
            if metrics.get("psi_mode") is None:
                sm = bridge.get("state_manifest", {})
                metrics["psi_mode"] = sm.get("psi_mode")
        except Exception:
            pass
        return jsonify({
            "entities": entities,
            "satellites": satellites,
            "gating": gating,
            "metrics": metrics,
            "schema_version": 1,
        })

    @app.route("/api/orbital/files", methods=["GET"])
    def orbital_files_api() -> Any:
        root = _root()
        reg_path = root / "integration" / "registries" / "definitions" / "orbital_definition_registry.json"
        orbit_class = request.args.get("class", "").upper()
        kind_filter = request.args.get("kind", "file")  # default: only files, not functions/methods
        limit = int(request.args.get("limit", 300))
        records: list[dict] = []
        counts: dict[str, int] = {}
        if reg_path.exists():
            try:
                raw = json.loads(reg_path.read_text(encoding="utf-8"))
                all_records = raw.get("records", [])
                # Filter to unique files only by default (avoid function/method duplicates)
                if kind_filter != "all":
                    all_records = [r for r in all_records if r.get("kind", "file") == kind_filter]
                for r in all_records:
                    oc = r.get("orbital_role", "UNRESOLVED")
                    counts[oc] = counts.get(oc, 0) + 1
                if orbit_class:
                    filtered = [r for r in all_records if r.get("orbital_role", "UNRESOLVED") == orbit_class]
                else:
                    filtered = all_records
                records = filtered[:limit]
            except Exception as exc:
                _LOG.warning("orbital files load failed: %s", exc)
        return jsonify({
            "records": records,
            "counts": counts,
            "total": sum(counts.values()),
            "filtered": len(records),
            "schema_version": 1,
        })

    @app.route("/portal/intentions", methods=["GET"])
    def portal_intentions() -> Any:
        return render_template("portal_intentions.html")

    @app.route("/api/portal/intentions", methods=["GET"])
    def intentions_api() -> Any:
        p = Path.home() / ".claude" / "ciel_intentions.md"
        active: list[dict] = []
        done: list[dict] = []
        pri_map = {"H": "high", "M": "medium", "L": "low"}
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if s.startswith("- [x]"):
                    done.append({"text": s[5:].strip(), "priority": "done", "raw": line})
                elif s.startswith("- [H]") or s.startswith("- [M]") or s.startswith("- [L]"):
                    pri = s[3]
                    active.append({"text": s[5:].strip(), "priority": pri_map.get(pri, "low"), "raw": line})
        return jsonify({"active": active, "done": done})

    @app.route("/api/portal/intentions/done", methods=["POST"])
    def intentions_done_api() -> Any:
        body = request.get_json(silent=True) or {}
        raw = body.get("raw", "").rstrip("\n")
        if not raw:
            return jsonify({"ok": False, "error": "raw required"}), 400
        p = Path.home() / ".claude" / "ciel_intentions.md"
        if not p.exists():
            return jsonify({"ok": False, "error": "file not found"}), 404
        content = p.read_text(encoding="utf-8")
        # Replace first matching raw line with [x] version
        import re as _re
        new_line = _re.sub(r"^(\s*- )\[([HML])\]", r"\1[x]", raw)
        if new_line == raw:
            return jsonify({"ok": False, "error": "no match"}), 400
        new_content = content.replace(raw, new_line, 1)
        p.write_text(new_content, encoding="utf-8")
        return jsonify({"ok": True})

    @app.route("/api/portal/intentions/add", methods=["POST"])
    def intentions_add_api() -> Any:
        body = request.get_json(silent=True) or {}
        text = (body.get("text") or "").strip()
        pri = (body.get("priority") or "M").upper()[:1]
        if pri not in ("H", "M", "L"):
            pri = "M"
        if not text:
            return jsonify({"ok": False, "error": "text required"}), 400
        p = Path.home() / ".claude" / "ciel_intentions.md"
        stamp = datetime.now().strftime("%Y-%m-%d")
        line = f"\n- [{pri}] [{stamp}] {text}"
        with open(p, "a", encoding="utf-8") as f:
            f.write(line)
        return jsonify({"ok": True})

    @app.route("/portal/metrics", methods=["GET"])
    def portal_metrics() -> Any:
        return render_template("portal_metrics.html")

    @app.route("/api/metrics/range", methods=["GET"])
    def metrics_range_api() -> Any:
        n = int(request.args.get("n", 100))
        db_path = Path.home() / ".claude" / "ciel_state.db"
        records: list[dict] = []
        if db_path.exists():
            try:
                import sqlite3 as _sql
                con = _sql.connect(str(db_path))
                cur = con.cursor()
                cur.execute(
                    "SELECT timestamp, cycle_index, system_health, coherence_index, "
                    "closure_penalty, ethical_score, identity_phase, mood, dominant_emotion "
                    "FROM metrics_history ORDER BY id DESC LIMIT ?", (n,)
                )
                cols = ["ts", "cycle", "health", "coherence", "closure", "ethical", "phase", "mood", "emotion"]
                rows = [dict(zip(cols, r)) for r in cur.fetchall()]
                records = list(reversed(rows))
                con.close()
            except Exception as exc:
                _LOG.warning("metrics range failed: %s", exc)
        return jsonify({"records": records, "count": len(records)})

    @app.route("/api/orbital/memory", methods=["GET"])
    def orbital_memory_api() -> Any:
        reg_path = Path.home() / "Pulpit" / "CIEL_memories" / "orbital_memory_registry.json"
        orbit_class = request.args.get("class", "").upper()
        limit = int(request.args.get("limit", 200))
        records: list[dict] = []
        counts: dict[str, int] = {}
        total = 0
        if reg_path.exists():
            try:
                raw = json.loads(reg_path.read_text(encoding="utf-8"))
                all_records = raw.get("records", [])
                counts = raw.get("counts_by_role", {})
                total = raw.get("count", len(all_records))
                if orbit_class:
                    filtered = [r for r in all_records if r.get("orbital_role", "UNRESOLVED") == orbit_class]
                else:
                    filtered = all_records
                records = filtered[:limit]
            except Exception as exc:
                _LOG.warning("orbital memory load failed: %s", exc)
        return jsonify({
            "records": records,
            "counts": counts,
            "total": total,
            "filtered": len(records),
            "schema_version": 1,
        })

    @app.route("/api/dziennik/wpis", methods=["POST"])
    def dziennik_wpis() -> Any:
        body = request.get_json(silent=True) or {}
        text = (body.get("text") or "").strip()
        if not text:
            return jsonify({"ok": False, "error": "text required"}), 400
        dziennik = Path.home() / "Pulpit" / "CIEL_memories" / "ciel_dziennik.md"
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(dziennik, "a", encoding="utf-8") as f:
            f.write(f"\n## {stamp}\n{text}\n")
        return jsonify({"ok": True, "stamp": stamp})

    # ── Nowe endpointy operacyjne ──────────────────────────────────────────

    @app.route("/api/projects")
    def api_projects() -> Response:
        return jsonify({"projects": _load_projects()})

    @app.route("/api/projects/add", methods=["POST"])
    def api_projects_add() -> Response:
        body = request.get_json(silent=True) or {}
        p = Path.home() / "Pulpit/CIEL_memories/projects.jsonl"
        entry = {
            "id": str(uuid.uuid4())[:8],
            "name": body.get("name", ""),
            "status": body.get("status", "planned"),
            "desc": body.get("desc", ""),
            "tags": body.get("tags", []),
            "updated": datetime.now().isoformat(),
        }
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return jsonify({"ok": True, "entry": entry})

    @app.route("/api/routines")
    def api_routines() -> Response:
        return jsonify(_load_routines_data())

    @app.route("/api/constraints")
    def api_constraints() -> Response:
        p = Path.home() / ".claude/ciel_constraints.jsonl"
        type_filter = request.args.get("type", "")
        items: list[dict] = []
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if not type_filter or entry.get("type", "") in type_filter.split(","):
                        items.append(entry)
                except Exception:
                    pass
        return jsonify({"constraints": items})

    @app.route("/api/constraints/add", methods=["POST"])
    def api_constraints_add() -> Response:
        body = request.get_json(silent=True) or {}
        p = Path.home() / ".claude/ciel_constraints.jsonl"
        entry = {
            "id": str(uuid.uuid4())[:8],
            "type": body.get("type", "forbid"),
            "text": body.get("text", ""),
            "tags": body.get("tags", []),
            "context": body.get("context", ""),
            "ts": datetime.now().isoformat(),
            "source": "gui",
        }
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return jsonify({"ok": True, "entry": entry})

    @app.route("/api/sub/recent")
    def api_sub_recent() -> Response:
        p = Path.home() / "Pulpit/CIEL_memories/logs/subconsciousness_beta_log.jsonl"
        n = int(request.args.get("n", 20))
        items: list[dict] = []
        if p.exists():
            lines = p.read_text(encoding="utf-8").splitlines()
            for line in lines[-n:]:
                line = line.strip()
                if line:
                    try:
                        items.append(json.loads(line))
                    except Exception:
                        pass
        return jsonify({"entries": list(reversed(items))})

    @app.route("/api/consolidator/results")
    def api_consolidator_results() -> Response:
        import sqlite3 as _sq
        db_path = Path.home() / "Pulpit/CIEL_memories/local_test/memories.db"
        results: list[dict] = []
        if db_path.exists():
            try:
                con = _sq.connect(str(db_path))
                cur = con.execute(
                    "SELECT path, status, themes, affect, essence, hunch, processed_at "
                    "FROM files WHERE status='done' ORDER BY processed_at DESC LIMIT 100"
                )
                cols = ["path", "status", "themes", "affect", "essence", "hunch", "processed_at"]
                for row in cur.fetchall():
                    d = dict(zip(cols, row))
                    try:
                        d["themes"] = json.loads(d["themes"]) if d["themes"] else []
                    except Exception:
                        d["themes"] = []
                    results.append(d)
                con.close()
            except Exception as exc:
                _LOG.warning("consolidator results: %s", exc)
        status_p = Path.home() / "Pulpit/CIEL_memories/local_test/.status.json"
        status_info: dict = {}
        if status_p.exists():
            try:
                status_info = json.loads(status_p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return jsonify({"results": results, "status": status_info})

    @app.route("/api/intentions")
    def api_intentions() -> Response:
        return jsonify({"intentions": _load_intentions_items()})

    @app.route("/api/intentions/add", methods=["POST"])
    def api_intentions_add() -> Response:
        body = request.get_json(silent=True) or {}
        p = Path.home() / "Pulpit/CIEL_memories/intentions.jsonl"
        entry = {
            "id": str(uuid.uuid4())[:8],
            "text": body.get("text", ""),
            "priority": body.get("priority", "M"),
            "done": False,
            "ts": datetime.now().isoformat(),
        }
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return jsonify({"ok": True, "entry": entry})

    @app.route("/api/intentions/done", methods=["POST"])
    def api_intentions_done() -> Response:
        body = request.get_json(silent=True) or {}
        target_id = body.get("id", "")
        p = Path.home() / "Pulpit/CIEL_memories/intentions.jsonl"
        if not p.exists():
            return jsonify({"ok": False, "error": "file not found"}), 404
        lines = p.read_text(encoding="utf-8").splitlines()
        updated = []
        for line in lines:
            try:
                entry = json.loads(line)
                if entry.get("id") == target_id:
                    entry["done"] = True
                updated.append(json.dumps(entry, ensure_ascii=False))
            except Exception:
                updated.append(line)
        p.write_text("\n".join(updated) + "\n", encoding="utf-8")
        return jsonify({"ok": True})

    @app.route("/api/operations/data")
    def api_operations_data() -> Any:
        return jsonify(_operations_data())

    @app.route("/api/dziennik")
    def api_dziennik_get() -> Response:
        p = Path.home() / "Pulpit/CIEL_memories/ciel_dziennik.md"
        text = p.read_text(encoding="utf-8") if p.exists() else ""
        return jsonify({"text": text})

    @app.route("/api/dziennik", methods=["POST"])
    def api_dziennik_post() -> Response:
        body = request.get_json(silent=True) or {}
        text = (body.get("text") or "").strip()
        if not text:
            return jsonify({"ok": False, "error": "text required"}), 400
        p = Path.home() / "Pulpit/CIEL_memories/ciel_dziennik.md"
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(f"\n## {stamp}\n{text}\n")
        return jsonify({"ok": True, "stamp": stamp})

    @app.route("/api/files/<path:filename>")
    def api_file_serve(filename: str) -> Response:
        allowed_ext = {".py", ".md", ".pdf", ".txt"}
        root = _root()
        search_dirs = [root / "docs", root / "scripts", root / "src"]
        for d in search_dirs:
            candidate = d / filename
            try:
                candidate = candidate.resolve()
                if not str(candidate).startswith(str(d.resolve())):
                    continue  # path traversal guard
            except Exception:
                continue
            if candidate.exists() and candidate.suffix in allowed_ext:
                from flask import send_file
                return send_file(str(candidate), as_attachment=True)
        return jsonify({"error": "file not found or not allowed"}), 404

    _PIPELINE_CONFIG_PATH = Path.home() / "Pulpit/CIEL_memories/pipeline_config.json"

    @app.route("/api/pipeline/config")
    def api_pipeline_config() -> Response:
        if _PIPELINE_CONFIG_PATH.exists():
            try:
                cfg = json.loads(_PIPELINE_CONFIG_PATH.read_text(encoding="utf-8"))
                return jsonify(cfg)
            except Exception:
                pass
        return jsonify({"modules": {}})

    @app.route("/api/pipeline/toggle", methods=["POST"])
    def api_pipeline_toggle() -> Response:
        body = request.get_json(silent=True) or {}
        module = body.get("module", "").strip()
        enabled = bool(body.get("enabled", True))
        if not module:
            return jsonify({"ok": False, "error": "module required"}), 400
        _PIPELINE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        cfg: dict = {"modules": {}}
        if _PIPELINE_CONFIG_PATH.exists():
            try:
                cfg = json.loads(_PIPELINE_CONFIG_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        cfg.setdefault("modules", {})[module] = enabled
        _PIPELINE_CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
        return jsonify({"ok": True, "module": module, "enabled": enabled})

    @app.errorhandler(404)
    def not_found(_err) -> tuple[Response, int]:
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(_err) -> tuple[Response, int]:
        return jsonify({"error": "internal server error"}), 500
