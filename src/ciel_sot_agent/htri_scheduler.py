"""HTRI Scheduler — dense matrix phase dynamics na i7-8750H.

Używa DensePhaseNetwork (htri_matrix) zamiast scalar mean-field Kuramoto.
Eksportuje: coherence r → n_threads_optimal dla llama.cpp.
Zapis do ~/Pulpit/CIEL_memories/state/htri_state.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_STATE_PATH = Path.home() / "Pulpit/CIEL_memories/state/htri_state.json"
CPU_THREADS = 12


def run(n: int = CPU_THREADS) -> dict:
    """Uruchom CPUHtri (DensePhaseNetwork). Zwróć stan."""
    try:
        import importlib, pathlib
        _htri_path = pathlib.Path(__file__).parent.parent / "CIEL_OMEGA_COMPLETE_SYSTEM"
        if str(_htri_path) not in sys.path:
            sys.path.insert(0, str(_htri_path))
        from ciel_omega.htri.htri_local import CPUHtri
        cpu = CPUHtri()
        m = cpu.run(steps=300)
        coherence = float(m.get("coherence", 0.85))
        soul = float(m.get("soul_invariant", 0.0))
        spectral = float(m.get("spectral_radius", 0.0))
        potential = float(m.get("potential", 0.0))
    except Exception as e:
        print(f"[HTRI] DensePhaseNetwork unavailable: {e}", file=sys.stderr)
        coherence, soul, spectral, potential = 0.85, 0.0, 0.0, 0.0

    n_threads_optimal = max(1, round(coherence * CPU_THREADS))

    state = {
        "coherence": coherence,
        "soul_invariant": soul,
        "spectral_radius": spectral,
        "potential": potential,
        "n_oscillators": CPU_THREADS,
        "n_threads_optimal": n_threads_optimal,
        "substrate": "CPU_i7-8750H_dense",
        "timestamp": time.time(),
    }

    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STATE_PATH.write_text(json.dumps(state))

    try:
        from .spreadsheet_db import append_htri_metrics
        append_htri_metrics(state)
    except Exception as e:
        print(f"[HTRI] DB write failed: {e}", file=sys.stderr)

    return state


def get_state() -> dict:
    """Wczytaj ostatni stan HTRI. Jeśli nieaktualny (>60s) — przelicz."""
    if _STATE_PATH.exists():
        try:
            s = json.loads(_STATE_PATH.read_text())
            if time.time() - s.get("timestamp", 0) < 60:
                return s
        except Exception:
            pass
    return run()


def get_optimal_threads() -> int:
    return get_state()["n_threads_optimal"]


if __name__ == "__main__":
    s = run()
    print(f"HTRI Scheduler — {s['n_oscillators']} CPU oscylatorów (dense matrix)")
    print(f"  coherence r      = {s['coherence']:.4f}")
    print(f"  soul_invariant   = {s['soul_invariant']:.4f}")
    print(f"  spectral_radius  = {s['spectral_radius']:.4f}")
    print(f"  n_threads_opt    = {s['n_threads_optimal']} / {CPU_THREADS}")
    print(f"  → {_STATE_PATH} zapisany")
