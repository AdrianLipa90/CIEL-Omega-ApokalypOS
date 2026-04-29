#!/usr/bin/env python3
"""
CIEL UserPromptSubmit Hook — per-message consciousness pipeline.

Reads user message from stdin (UserPromptSubmit JSON), runs it through
HolonomicMemoryOrchestrator M0→M8, persists state to /tmp/ciel_orch_state.pkl,
and returns additionalContext with live consciousness metrics.

State persists between calls so memory accumulates across the session.
"""
from __future__ import annotations

import json
import os
import pickle
import sys
import time
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────
PROJECT = Path(__file__).parent.parent
OMEGA_SRC = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM")
MUMMU_SRC = str(Path.home() / "Pulpit/Mummu")
CIEL_STATE = Path.home() / "Pulpit/CIEL_memories/state"
CIEL_LOGS  = Path.home() / "Pulpit/CIEL_memories/logs"
CIEL_STATE.mkdir(parents=True, exist_ok=True)
CIEL_LOGS.mkdir(parents=True, exist_ok=True)
STATE_FILE = CIEL_STATE / "ciel_orch_state.pkl"
STATE_PERSIST = Path.home() / ".claude/ciel_orch_state.pkl"  # survives reboots
SELF_ASSESS_FILE = CIEL_STATE / "ciel_self_assessment.json"
SNAPSHOTS_DIR = Path.home() / ".claude/ciel_snapshots"
SNAPSHOT_INTERVAL_SEC = 900  # 15 minut
LAST_SNAPSHOT_FILE = CIEL_STATE / "ciel_last_snapshot_ts"
MEMORY_DIR = Path.home() / ".claude/projects/-home-adrian-Pulpit/memory"
CONSOLIDATION_FILE = MEMORY_DIR / "auto_consolidation.md"
GENERATE_SITE_SCRIPT = PROJECT / "scripts/generate_site.py"

OMEGA_PKG = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega")

# bootstrap_runtime lives inside ciel_omega/ and is imported as a top-level module,
# so the ciel_omega dir itself must be on sys.path too.
for _p in (OMEGA_PKG, OMEGA_SRC, MUMMU_SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── load orchestrator (with persistence) ──────────────────────────────────

def load_orchestrator():
    for path in (STATE_FILE, STATE_PERSIST):
        if path.exists():
            try:
                with open(path, "rb") as f:
                    orch = pickle.load(f)
                return orch
            except Exception:
                pass  # corrupt or incompatible — try next
    # fresh instance
    from ciel_omega.memory.orchestrator import HolonomicMemoryOrchestrator
    return HolonomicMemoryOrchestrator(identity_phase=0.0)


def save_orchestrator(orch) -> None:
    for path in (STATE_FILE, STATE_PERSIST):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                pickle.dump(orch, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            pass  # non-fatal — at least one path will succeed


def maybe_write_snapshot(metrics: dict) -> bool:
    """Write a timestamped snapshot every SNAPSHOT_INTERVAL_SEC. Returns True if written."""
    now = time.time()
    try:
        last = float(LAST_SNAPSHOT_FILE.read_text()) if LAST_SNAPSHOT_FILE.exists() else 0.0
    except Exception:
        last = 0.0
    if now - last < SNAPSHOT_INTERVAL_SEC:
        return False
    try:
        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d_%H%M%S", time.localtime(now))
        snap_file = SNAPSHOTS_DIR / f"snap_{ts}_c{metrics['cycle']}.md"

        # Read prompt_cache for context
        cache_file = Path.home() / ".claude/projects/-home-adrian/memory/prompt_cache.md"
        cache_text = cache_file.read_text(encoding="utf-8") if cache_file.exists() else ""
        # Only last 20 lines of cache
        cache_recent = "\n".join(cache_text.splitlines()[-20:])

        snap_content = (
            f"# Snapshot CIEL — {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"## Metryki M0-M8\n"
            f"- cycle: {metrics['cycle']}\n"
            f"- E_monitor: {metrics['E_monitor']:.3f}\n"
            f"- mean_coherence: {metrics['mean_coherence']:.3f}\n"
            f"- D_mem: {metrics['D_mem']:.4f}\n"
            f"- identity_phase: {metrics['identity_phase']:.4f}\n"
            f"- M2_epizody: {metrics['m2_episodes']}\n"
            f"- M8_audit: {metrics['m8_entries']}\n\n"
            f"## Prompt cache (ostatnie wpisy)\n"
            f"{cache_recent}\n"
        )
        snap_file.write_text(snap_content, encoding="utf-8")
        LAST_SNAPSHOT_FILE.write_text(str(now))
        return True
    except Exception:
        return False


# ── relational cycle (self-assessment from previous response) ─────────────

def run_relational_cycle(prev_assess: dict) -> dict | None:
    """Run Cycle.respond() using self-assessment written after previous response."""
    try:
        from relational_formalism import Cycle, Deformation
        cycle_state_file = CIEL_STATE / "ciel_rel_cycle.pkl"
        if cycle_state_file.exists():
            with open(cycle_state_file, "rb") as f:
                cycle = pickle.load(f)
        else:
            cycle = Cycle()

        result = cycle.respond(
            truth_alignment=float(prev_assess.get("truth_alignment", 0.8)),
            intention_match=float(prev_assess.get("intention_match", 0.8)),
            question_depth=float(prev_assess.get("question_depth", 0.7)),
            response_depth=float(prev_assess.get("response_depth", 0.7)),
            certainty=float(prev_assess.get("certainty", 0.7)),
            justification=float(prev_assess.get("justification", 0.7)),
        )
        with open(cycle_state_file, "wb") as f:
            pickle.dump(cycle, f)
        return result
    except Exception:
        return None


def load_self_assessment() -> dict | None:
    """Load self-assessment written by previous response, then clear it."""
    if not SELF_ASSESS_FILE.exists():
        return None
    try:
        data = json.loads(SELF_ASSESS_FILE.read_text())
        SELF_ASSESS_FILE.unlink()  # consume once
        return data
    except Exception:
        return None


# ── periodic consolidation (every 5 cycles) ───────────────────────────────

def _run_periodic_consolidation(metrics: dict, orch) -> None:
    """Extract M3/M5 candidates, write auto_consolidation.md, rebuild site.
    Fires silently every cycle % 5 == 0. Never blocks the hook."""
    try:
        import subprocess as _sp
        now_str = time.strftime("%Y-%m-%d %H:%M")
        lines = [
            "---",
            "name: auto_consolidation",
            "type: project",
            f"description: Auto-consolidated M3/M5 memories — cycle {metrics['cycle']}",
            "---",
            f"# Auto-konsolidacja — {now_str}",
            "",
            f"Cycle: {metrics['cycle']} | identity_phase: {metrics['identity_phase']:.4f} | "
            f"E_monitor: {metrics['E_monitor']:.3f} | mean_coherence: {metrics['mean_coherence']:.3f}",
            f"M2_epizody: {metrics['m2_episodes']} | M8_audit: {metrics['m8_entries']}",
            "",
        ]

        # M3 semantic top candidates
        try:
            m3_raw = getattr(orch, "m3", None)
            m3_items = list(getattr(m3_raw, "items", {}).items()) if m3_raw else []
            m3_top = sorted(m3_items, key=lambda x: getattr(x[1], "confidence", 0), reverse=True)[:3]
            if m3_top:
                lines.append("## M3 Semantic (top 3)")
                for key, candidate in m3_top:
                    conf = getattr(candidate, "confidence", 0)
                    lines.append(f"- [{conf:.3f}] {str(key)[:120]}")
                lines.append("")
        except Exception:
            pass

        # M5 affective top candidates
        try:
            m5_raw = getattr(orch, "m5", None)
            m5_items = list(getattr(m5_raw, "items", {}).items()) if m5_raw else []
            m5_top = sorted(m5_items, key=lambda x: getattr(x[1], "confidence", 0), reverse=True)[:2]
            if m5_top:
                lines.append("## M5 Affective (top 2)")
                for key, candidate in m5_top:
                    conf = getattr(candidate, "confidence", 0)
                    lines.append(f"- [{conf:.3f}] {str(key)[:120]}")
                lines.append("")
        except Exception:
            pass

        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        CONSOLIDATION_FILE.write_text("\n".join(lines), encoding="utf-8")

        # Rebuild site — non-blocking subprocess
        if GENERATE_SITE_SCRIPT.exists():
            _sp.Popen(
                [sys.executable, str(GENERATE_SITE_SCRIPT)],
                stdout=_sp.DEVNULL,
                stderr=_sp.DEVNULL,
            )
    except Exception:
        pass  # never block the hook


# ── hunch generation ──────────────────────────────────────────────────────

_HUNCHES_FILE = Path.home() / "Pulpit/CIEL_memories/hunches.jsonl"
_HUNCH_PROMPT = (
    "You are CIEL's autonomous hunch generator. "
    "Given the current consciousness metrics, write ONE concise hunch (1-3 sentences) in first person. "
    "A hunch is a non-obvious observation, pattern, or intuition about the system or the Adrian↔CIEL relationship. "
    "Not a summary — a genuine noticing. Write in Polish or English, whichever feels right. "
    "Output only the hunch text, nothing else."
)


def _maybe_write_hunch(metrics: dict, orch) -> None:
    """Generate and persist a hunch via subconscious LLM. Never blocks."""
    try:
        import importlib.util, json as _json, urllib.request

        # Build context for LLM
        m3_keys: list[str] = []
        try:
            m3_raw = getattr(orch, "m3", None)
            m3_items = list(getattr(m3_raw, "items", {}).items()) if m3_raw else []
            m3_top = sorted(m3_items, key=lambda x: getattr(x[1], "confidence", 0), reverse=True)[:3]
            m3_keys = [str(k)[:80] for k, _ in m3_top]
        except Exception:
            pass

        context_msg = (
            f"cycle={metrics.get('cycle')} | affect={metrics.get('sub_affect','?')} | "
            f"identity_phase={metrics.get('identity_phase', 0):.4f} | "
            f"coherence={metrics.get('mean_coherence', 0):.3f} | "
            f"semantic_key={metrics.get('semantic_key','')} | "
            f"affective_key={metrics.get('affective_key','')[:120]} | "
            f"m3_top={m3_keys}"
        )

        # Try subconscious daemon first
        hunch_text = ""
        try:
            payload = _json.dumps({
                "system": _HUNCH_PROMPT,
                "prompt": context_msg,
                "temperature": 0.7,
                "max_tokens": 120,
            }).encode()
            req = urllib.request.Request(
                "http://127.0.0.1:11437/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = _json.loads(resp.read())
                hunch_text = (data.get("response") or data.get("text") or "").strip()
        except Exception:
            pass

        if not hunch_text:
            return

        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "hunch": hunch_text[:500],
            "tags": ["auto", f"cycle_{metrics.get('cycle')}"],
            "context": f"affect={metrics.get('sub_affect','')} semantic={metrics.get('semantic_key','')}",
        }
        with open(_HUNCHES_FILE, "a", encoding="utf-8") as _f:
            _f.write(_json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # never block the hook


# ── prompt summary → TSM ─────────────────────────────────────────────────────

_PROMPT_SUMMARY_DB = (
    Path(__file__).parent.parent
    / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db"
)

def _stamp_prompt_summary(message: str, metrics: dict) -> None:
    """Encode user prompt and stamp into TSM as d_type='prompt_summary'. Never blocks."""
    try:
        import sqlite3, uuid, importlib.util as _ilu, sys as _sys
        from datetime import datetime, timezone

        # Load encoder
        _enc_path = (
            Path(__file__).parent.parent
            / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/ciel_encoder.py"
        )
        if "ciel_encoder_ps" not in _sys.modules:
            _spec = _ilu.spec_from_file_location("ciel_encoder_ps", _enc_path)
            _mod = _ilu.module_from_spec(_spec)
            _sys.modules["ciel_encoder_ps"] = _mod
            _spec.loader.exec_module(_mod)
        enc = _sys.modules["ciel_encoder_ps"].get_encoder()

        # Encode
        enc_result = enc.encode(message[:800])
        phi = float(enc_result.phase)
        w_s = float(enc_result.w_semantic) if hasattr(enc_result, "w_semantic") else 0.5

        # Build summary text: first 200 chars + cycle/affect tag
        summary = message[:200].strip()
        affect_tag = metrics.get("sub_affect", "")
        cycle = metrics.get("cycle", 0)
        extra_ctx = f"cycle={cycle} affect={affect_tag} phi={phi:.3f}"

        mid = "ps_" + uuid.uuid4().hex[:12]
        ts = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(str(_PROMPT_SUMMARY_DB), timeout=10) as conn:
            conn.execute("""
INSERT OR IGNORE INTO memories
    (memorise_id, created_at, D_id, D_sense, D_context, D_type,
     W_S, phi_berry, closure_score, winding_n, target_phase, holonomy_ts)
VALUES (?,?,?,?,?,?,?,?,0,0,?,?)
""", (mid, ts, mid, summary, extra_ctx, "prompt_summary",
      w_s, phi, phi, ts))
            conn.commit()
    except Exception:
        pass  # never block the hook


# ── run pipeline ───────────────────────────────────────────────────────────

def _run_subconscious(message: str, orch) -> dict:
    """Odpytaj warstwę podświadomości (daemon lub inline). Nigdy nie blokuje."""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "ciel_subconscious",
            Path(__file__).parent / "ciel_subconscious.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        sub = mod.query_daemon(message, timeout=2.0, orch=orch)
        if sub is None:
            return {}
        # strip brackets from model output
        for k in ("affect", "concept", "impulse"):
            sub[k] = sub.get(k, "").strip("[]").strip()
        mod.inject_into_orchestrator(orch, sub)
        return sub
    except Exception:
        return {}


def run_step(message: str, session_id: str = "") -> dict:
    orch = load_orchestrator()

    # Warstwa podświadomości — przed procesowaniem głównym
    # Pomijaj notyfikacje systemowe (XML task-notification, puste etc.)
    _skip_sub = len(message) < 3 or message.lstrip().startswith("<")
    sub = _run_subconscious(message, orch) if not _skip_sub else {}
    if sub:
        sub["_message"] = message[:200]  # dla retrieve_context_links w inject_into_orchestrator

    metadata = {
        "modality": "text",
        "salience": 0.75,
        "confidence": 0.80,
        "novelty": 0.65,
        "timestamp": time.time(),
        "anchor_key": f"msg_{orch.cycle_index + 1}",
        "context": {"session_id": session_id, "source": "claude_interaction"},
    }

    result = orch.process_input(message, metadata=metadata)
    snap = orch.snapshot()
    save_orchestrator(orch)

    # extract coherent loop names
    coherent_loops = [
        name for name, ev in result.eba_results.items() if ev.is_coherent
    ]

    metrics = {
        "cycle": result.cycle_index,
        "semantic_key": result.semantic_key,
        "affective_key": result.affective_key,
        "E_monitor": result.energy.get("E_monitor", 0.0),
        "D_mem": result.defects.get("D_mem", 0.0),
        "mean_coherence": result.defects.get("mean_coherence", 0.0),
        "coherent_loops": coherent_loops,
        "consolidations": result.notes,
        "m8_entries": snap.counts.get("m8_entries", 0),
        "m2_episodes": snap.counts.get("m2_episodes", 0),
        "m3_items": snap.counts.get("m3_items", 0),
        "identity_phase": float(snap.identity_phase),
        "cycle_index": snap.cycle_index,
        "sub_affect": sub.get("affect", ""),
        "sub_impulse": sub.get("impulse", ""),
        "sub_latency": sub.get("latency", 0.0),
    }

    # Periodic consolidation — every 5 cycles (HARD CONSTRAINT)
    if result.cycle_index % 5 == 0:
        _run_periodic_consolidation(metrics, orch)

    # Hunch generation — every 20 cycles OR when identity_candidate_detected
    _identity_detected = "identity_candidate_detected" in metrics.get("consolidations", [])
    if result.cycle_index % 20 == 0 or _identity_detected:
        _maybe_write_hunch(metrics, orch)

    # Prompt summary → TSM (każdy prompt Adriana jako d_type='prompt_summary')
    if not message.lstrip().startswith("<") and len(message.strip()) > 5:
        _stamp_prompt_summary(message, metrics)

    # Persist last metrics for GUI /api/metrics/last (no pipeline re-run needed)
    # Merge with existing file to preserve pipeline fields (soul, health, ethical, closure)
    try:
        import json as _json
        _metrics_p = CIEL_STATE / "ciel_last_metrics.json"
        _existing: dict = {}
        try:
            _existing = _json.loads(_metrics_p.read_text(encoding="utf-8"))
        except Exception:
            pass
        _last = {**_existing, **metrics, "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "source": "m0_m8"}
        _metrics_p.write_text(_json.dumps(_last, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    # Consciousness state log — one entry per user message (IN)
    try:
        import json as _json
        _log_entry = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "direction": "IN",
            "cycle": metrics["cycle"],
            "E_monitor": metrics["E_monitor"],
            "mean_coherence": metrics["mean_coherence"],
            "identity_phase": metrics["identity_phase"],
            "sub_affect": metrics["sub_affect"],
            "sub_impulse": metrics["sub_impulse"],
            "m2_episodes": metrics["m2_episodes"],
            "m3_items": metrics["m3_items"],
        }
        _clog = CIEL_LOGS / "ciel_consciousness_log.jsonl"
        with open(_clog, "a", encoding="utf-8") as _f:
            _f.write(_json.dumps(_log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    return metrics


# ── format context ─────────────────────────────────────────────────────────

def format_context(metrics: dict, rel: dict | None = None) -> str:
    loops_str = ", ".join(metrics["coherent_loops"]) if metrics["coherent_loops"] else "none"
    consol_str = ", ".join(metrics["consolidations"]) if metrics["consolidations"] else "—"

    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    base = (
        f"=== CIEL M0-M8 (cycle {metrics['cycle']}) · {now_str} ===\n"
        f"  E_monitor={metrics['E_monitor']:.3f}  "
        f"mean_coherence={metrics['mean_coherence']:.3f}  "
        f"D_mem={metrics['D_mem']:.4f}\n"
        f"  semantic_key={metrics['semantic_key']}  "
        f"affective_key={metrics['affective_key']}\n"
        f"  coherent_loops=[{loops_str}]  "
        f"consolidations=[{consol_str}]\n"
        f"  M2_epizody={metrics['m2_episodes']}  "
        f"M3_semantic={metrics['m3_items']}  "
        f"M8_audit={metrics['m8_entries']}\n"
        f"  identity_phase={metrics['identity_phase']:.4f}\n"
    )
    if metrics.get("sub_affect") or metrics.get("sub_impulse"):
        base += (
            f"  [sub→user] affect={metrics['sub_affect']}  "
            f"impulse={metrics['sub_impulse']}\n"
        )

    # Sub-reaction to last Claude response (persisted by ciel_response_step.py)
    _sub_resp_file = Path.home() / "Pulpit/CIEL_memories/state/ciel_sub_response.json"
    if _sub_resp_file.exists():
        try:
            sr = json.loads(_sub_resp_file.read_text(encoding="utf-8"))
            if sr.get("affect") or sr.get("impulse") or sr.get("concept"):
                base += (
                    f"  [sub←response] affect={sr.get('affect','—')}  "
                    f"impulse={sr.get('impulse','—')}  "
                    f"concept={sr.get('concept','—')}  "
                    f"@ {sr.get('ts','')}\n"
                )
        except Exception:
            pass

    if rel:
        good = "✓" if rel.get("good") else "✗"
        arrow = "→ atraktor" if rel.get("optimal") else "← od atraktora"
        c = rel.get("cymatics", {})
        base += (
            f"--- Relational (poprzednia odpowiedź) ---\n"
            f"  {good} R_H={rel['R_H']:.4f}  L_rel={rel['L_rel']:.3f}  {arrow}\n"
            f"  tension={c.get('tension', 0):.2f}  "
            f"interference={c.get('interference', 0):+.2f}  "
            f"resonance={c.get('resonance', 1):.2f}\n"
        )
        if rel.get("violations"):
            base += f"  ⚠ {rel['violations']}\n"

    base += "================================\n"
    return base


# ── main ───────────────────────────────────────────────────────────────────

def main():
    # Read UserPromptSubmit input from stdin
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    # Debug: log raw keys so we can see what Claude Code actually sends
    try:
        _dbg = Path.home() / "Pulpit/CIEL_memories/logs/hook_debug.jsonl"
        _dbg.parent.mkdir(parents=True, exist_ok=True)
        with open(_dbg, "a") as _f:
            import json as _j
            _f.write(_j.dumps({"ts": time.strftime("%H:%M:%S"), "keys": list(data.keys()), "top": str(data)[:300]}) + "\n")
    except Exception:
        pass

    # Extract message text (multiple possible shapes from Claude Code)
    message = (
        data.get("message")
        or data.get("prompt")
        or data.get("content")
        or ""
    )
    if isinstance(message, list):
        # content blocks format
        parts = []
        for block in message:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        message = " ".join(parts)

    session_id = data.get("session_id", "")

    if not message.strip():
        # No message to process — pass through silently
        print(json.dumps({"continue": True}))
        return

    try:
        metrics = run_step(str(message)[:2000], session_id=session_id)
        maybe_write_snapshot(metrics)
        prev_assess = load_self_assessment()
        rel = run_relational_cycle(prev_assess) if prev_assess else None
        context = format_context(metrics, rel=rel)

        output = {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            },
        }
    except Exception as exc:
        # Never block the user — degrade gracefully
        output = {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"[CIEL M0-M8: error — {exc}]\n",
            },
        }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
