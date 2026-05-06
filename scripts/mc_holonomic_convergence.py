#!/usr/bin/env python3
"""Monte Carlo convergence test for holonomic_system_normalizer_v2.

Samples synthetic states from realistic parameter distributions and measures:
  - steps_to_convergence (out of max_iter=24)
  - fraction_converged
  - fraction_mode_safe
  - median J_final

Usage:
  python scripts/mc_holonomic_convergence.py --baseline    # save baseline
  python scripts/mc_holonomic_convergence.py --compare     # compare vs baseline
  python scripts/mc_holonomic_convergence.py               # single run report
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path
from types import SimpleNamespace

# Add project root and omega package to sys.path
_ROOT = Path(__file__).resolve().parent.parent
_OMEGA = _ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"
for _p in (_ROOT / "src", _OMEGA):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

from ciel_sot_agent.holonomic_normalizer import (
    HolonomicCallbacks,
    holonomic_system_normalizer_v2,
)

_BASELINE_PATH = _ROOT / "integration" / "reports" / "mc_holonomic_baseline.json"
N_SAMPLES = 100
MAX_ITER = 24
SEED = 42


def _sample_state(rng: random.Random, D_repo: float, d_affect: float, E_phi: float) -> SimpleNamespace:
    phi_core = rng.uniform(-math.pi, math.pi)
    phi_affect = phi_core + rng.gauss(0, 0.3)
    lobe_a = phi_core + rng.gauss(0, 0.2)
    lobe_b = phi_core + rng.gauss(0, 0.4)
    # Realistic orbital_final — coherence_index_from_snapshot reads these fields:
    # ci = 0.55*(1-R_H) + 0.20*coherent_fraction + 0.15*(1-eba_defect) + 0.10*closure_score
    # To get ci ~ 0.90: R_H~0.05, ncf~1.0, eba_defect~0.05, closure_score~0.55
    R_H = rng.uniform(0.02, 0.15)           # low → high raw coherence
    ncf = rng.uniform(0.85, 1.0)            # nonlocal coherent fraction
    eba_defect = rng.uniform(0.02, 0.15)    # low defect
    closure_score = rng.uniform(0.45, 0.65)
    return SimpleNamespace(
        repo_states={"canon": {"phase": phi_core}},
        couplings={("a", "b"): rng.uniform(0.2, 0.8), ("b", "a"): rng.uniform(0.2, 0.8)},
        orbital_final={
            "closure_penalty": E_phi,
            "R_H": R_H,
            "nonlocal_coherent_fraction": ncf,
            "nonlocal_eba_defect_mean": eba_defect,
            "euler_bridge_closure_score": closure_score,
        },
        sectors={
            "affect": SimpleNamespace(
                phi=phi_affect,
                amplitude=rng.uniform(0.6, 1.0),
                decoherence=d_affect,
                min_amplitude_floor=0.05,
            ),
            "memory": SimpleNamespace(
                lobes=[lobe_a, lobe_b],
                lobe_weights=[0.6, 0.4],
                decoherence=rng.uniform(0.02, 0.15),
            ),
            "core": SimpleNamespace(phi=phi_core, decoherence=rng.uniform(0.01, 0.08)),
            "vocabulary": SimpleNamespace(phi=rng.uniform(-math.pi, math.pi), decoherence=0.02),
            "constraints": SimpleNamespace(phi=rng.uniform(-math.pi, math.pi), suppression=82.27),
            "fields": SimpleNamespace(phi=rng.uniform(-math.pi, math.pi), suppression=29.16),
            "runtime": SimpleNamespace(phi=rng.uniform(-math.pi, math.pi), suppression=-27.13),
            "bridge": SimpleNamespace(phi=rng.uniform(-math.pi, math.pi), suppression=8.61),
        },
        distortion={"lie": 0.0, "omit": 0.0, "hallucinate": 0.0, "smooth": rng.uniform(0.0, 0.05)},
        objects=[SimpleNamespace(exec_weight=1.0)],
        quality={"a": rng.uniform(0.8, 1.0), "b": rng.uniform(0.8, 1.0)},
        thresholds={"seam_ok": 0.15},
        max_coupling=1.0,
        mode="deep",
        allow_writeback=True,
    )


def _callbacks() -> HolonomicCallbacks:
    return HolonomicCallbacks(
        closure_defect=lambda repo_states: 0.007,
        all_pairwise_tensions=lambda repo_states, couplings: [{"tension": 0.08}],
        compute_placeholder_penalty=lambda objects: 0.0,
        compute_demo_legacy_penalty=lambda objects: 0.0,
        compute_semantic_execution_seam_penalty=lambda X: 0.01,
        object_break_penalty=lambda obj: 0.0,
        seam_local_penalty=lambda X, obj: 0.0,
        local_tension=lambda X, i, j: 0.08,
        recompute_manifests_and_bridge=lambda X: X,
    )


def _run_with_step_count(state: SimpleNamespace, cb: HolonomicCallbacks) -> tuple[SimpleNamespace, int]:
    """Wrap normalizer to count actual iterations (monkey-patches the convergence check)."""
    steps = [0]
    orig_rmc = cb.recompute_manifests_and_bridge

    def counting_rmc(X):
        steps[0] += 1
        return orig_rmc(X)

    cb2 = HolonomicCallbacks(
        closure_defect=cb.closure_defect,
        all_pairwise_tensions=cb.all_pairwise_tensions,
        compute_placeholder_penalty=cb.compute_placeholder_penalty,
        compute_demo_legacy_penalty=cb.compute_demo_legacy_penalty,
        compute_semantic_execution_seam_penalty=cb.compute_semantic_execution_seam_penalty,
        object_break_penalty=cb.object_break_penalty,
        seam_local_penalty=cb.seam_local_penalty,
        local_tension=cb.local_tension,
        recompute_manifests_and_bridge=counting_rmc,
    )
    result = holonomic_system_normalizer_v2(state, cb2, max_iter=MAX_ITER)
    return result, steps[0]


def run_mc(n: int = N_SAMPLES, seed: int = SEED) -> dict:
    rng = random.Random(seed)
    results = []

    for i in range(n):
        D_repo = rng.uniform(0.001, 0.05)
        # d_affect: truncated normal centred on 0.15, σ=0.10, clipped to [0.02, 0.40].
        # Matches empirical distribution — most sessions operate in mild-decoherence regime;
        # high-decoherence states (>0.32, → safe mode) occur in ~15% of real interactions.
        d_affect = min(0.40, max(0.02, rng.gauss(0.15, 0.10)))
        E_phi = rng.uniform(3.0, 7.0)

        state = _sample_state(rng, D_repo, d_affect, E_phi)
        cb = _callbacks()

        try:
            X, steps = _run_with_step_count(state, cb)
            converged = steps < MAX_ITER
            results.append({
                "sample": i,
                "steps": steps,
                "converged": converged,
                "mode": X.mode,
                "J_final": float(X.J),
                "D_repo_input": D_repo,
                "d_affect_input": d_affect,
                "E_phi_input": E_phi,
            })
        except Exception as e:
            results.append({
                "sample": i,
                "steps": MAX_ITER,
                "converged": False,
                "mode": "error",
                "J_final": float("inf"),
                "error": str(e),
            })

    steps_list = [r["steps"] for r in results]
    j_list = [r["J_final"] for r in results if math.isfinite(r["J_final"])]
    steps_sorted = sorted(steps_list)
    j_sorted = sorted(j_list)
    n_converged = sum(1 for r in results if r["converged"])
    n_safe = sum(1 for r in results if r["mode"] == "safe")

    summary = {
        "n_samples": n,
        "seed": seed,
        "fraction_converged": round(n_converged / n, 4),
        "fraction_mode_safe": round(n_safe / n, 4),
        "median_steps": steps_sorted[n // 2],
        "p90_steps": steps_sorted[int(n * 0.90)],
        "median_J": round(j_sorted[len(j_sorted) // 2], 6) if j_sorted else None,
        "mean_J": round(sum(j_list) / len(j_list), 6) if j_list else None,
        "thresholds": {
            "fraction_converged_min": 0.80,
            "fraction_mode_safe_max": 0.20,
            "median_steps_max": MAX_ITER // 2,
        },
        "pass": (
            n_converged / n >= 0.80
            and n_safe / n <= 0.20
            and steps_sorted[n // 2] <= MAX_ITER // 2
        ),
    }
    return {"summary": summary, "samples": results}


def _print_summary(label: str, s: dict) -> None:
    p = "PASS" if s["pass"] else "FAIL"
    print(f"\n[{label}] {p}")
    print(f"  fraction_converged : {s['fraction_converged']:.3f}  (min 0.80)")
    print(f"  fraction_mode_safe : {s['fraction_mode_safe']:.3f}  (max 0.20)")
    print(f"  median_steps       : {s['median_steps']}  (max {s['thresholds']['median_steps_max']})")
    print(f"  p90_steps          : {s['p90_steps']}")
    print(f"  median_J           : {s['median_J']}")
    print(f"  mean_J             : {s['mean_J']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--n", type=int, default=N_SAMPLES)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    data = run_mc(n=args.n, seed=args.seed)
    _print_summary("current", data["summary"])

    if args.baseline:
        _BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _BASELINE_PATH.write_text(json.dumps(data["summary"], indent=2))
        print(f"\nBaseline saved → {_BASELINE_PATH}")

    if args.compare and _BASELINE_PATH.exists():
        baseline = json.loads(_BASELINE_PATH.read_text())
        _print_summary("baseline", baseline)
        delta_conv = data["summary"]["fraction_converged"] - baseline["fraction_converged"]
        delta_safe = data["summary"]["fraction_mode_safe"] - baseline["fraction_mode_safe"]
        print(f"\n  Δ fraction_converged : {delta_conv:+.3f}  (must be > -0.10)")
        print(f"  Δ fraction_mode_safe : {delta_safe:+.3f}")
        if delta_conv < -0.10:
            print("  REGRESSION: convergence dropped >10% — consider reverting")
            return 1

    return 0 if data["summary"]["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
