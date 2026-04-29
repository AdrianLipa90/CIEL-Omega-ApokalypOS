"""HTRI Scheduler — Kuramoto na 12 wątkach CPU (i7-8750H).

Skalowanie H200 → local:
  H200:  14 080 bloków, spread 28 Hz → bicie 7.83 Hz
  Local: 12 wątków (logical cores), ta sama topologia Kuramoto, ta sama zasada.

Eksportuje: coherence r → n_threads_optimal dla llama.cpp.
Zapis do ~/Pulpit/CIEL_memories/state/htri_state.json — czytany przez routes.py przy każdym inference.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

# ── Hardware constants (i7-8750H) ────────────────────────────────────────────

CPU_THREADS    = 12
OMEGA_SPREAD   = 0.05   # rozrzut częstości [znorm.]
DT             = 0.01
N_STEPS        = 500    # ~5τ — wystarczy do konwergencji
KAPPA_FACTOR   = 20.0   # jak w htri_mini — głęboko za progiem

_STATE_PATH    = Path.home() / "Pulpit/CIEL_memories/state/htri_state.json"


def _kuramoto_step(
    phi: np.ndarray,
    omega: np.ndarray,
    kappa: float,
    dt: float,
) -> np.ndarray:
    """Mean-field Kuramoto step dla N oscylatorów."""
    z = np.mean(np.exp(1j * phi.astype(np.complex64)))
    r = float(np.abs(z))
    psi = float(np.angle(z))
    coupling = kappa * r * np.sin(psi - phi)
    return (phi + dt * (omega + coupling)) % (2 * np.pi)


def run(n: int = CPU_THREADS) -> dict:
    """Uruchom synchronizację Kuramoto dla n oscylatorów. Zwróć stan."""
    phi = np.random.uniform(0, 2 * np.pi, n).astype(np.float32)
    omega = np.random.normal(0.0, OMEGA_SPREAD, n).astype(np.float32)

    # κ_c mean-field: 2σ/1 (λ_max=1 dla all-to-all)
    kappa_c = 2.0 * OMEGA_SPREAD
    kappa = KAPPA_FACTOR * kappa_c

    for _ in range(N_STEPS):
        phi = _kuramoto_step(phi, omega, kappa, DT)

    z = np.mean(np.exp(1j * phi.astype(np.complex64)))
    coherence = float(np.abs(z))
    phase_mean = float(np.angle(z))

    n_threads_optimal = max(1, round(coherence * n))

    state = {
        "coherence": coherence,
        "phase_mean": phase_mean,
        "n_oscillators": n,
        "n_threads_optimal": n_threads_optimal,
        "kappa": float(kappa),
        "timestamp": time.time(),
    }
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
    """Zwróć optymalną liczbę wątków wg HTRI coherence."""
    return get_state()["n_threads_optimal"]


if __name__ == "__main__":
    s = run()
    print(f"HTRI Scheduler — {s['n_oscillators']} CPU oscylatorów")
    print(f"  coherence r     = {s['coherence']:.4f}")
    print(f"  n_threads_opt   = {s['n_threads_optimal']} / {CPU_THREADS}")
    print(f"  → {_STATE_PATH} zapisany")
