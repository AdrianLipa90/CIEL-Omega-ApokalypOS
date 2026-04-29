"""W_ij coupling optimizer for the CIEL orbital system.

Minimizes closure_penalty over the scalar coupling matrix W_ij in
integration/Orbital/main/manifests/couplings_global.json using
scipy L-BFGS-B with bounds W_ij ∈ [0.01, 1.0].

Objective:
    closure_penalty = Σ_i |Σ_j A_ij(W) * τ_j - e^{iφ_i}|²  +  ζ_tetra_weight * ζ_tetra

Usage:
    python scripts/optimize_wij.py [--write] [--steps N] [--max-iter N]
"""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

# --- path setup ---
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "integration"))

from integration.Orbital.main.global_pass import DEFAULT_PARAMS, build, snapshot
from integration.Orbital.main.metrics import (
    closure_penalty,
    global_coherence,
)
from integration.Orbital.main.registry import load_system
from integration.Orbital.main.dynamics import step as orbital_step
from integration.Orbital.main.phase_control import (
    build_health_manifest,
    build_state_manifest,
    coherence_index_from_snapshot,
    recommend_control,
)

ci_fn = coherence_index_from_snapshot


def _build_system(coupling_dict: dict, params: dict):
    """Build an OrbitalSystem from a coupling dict and DEFAULT_PARAMS."""
    repo_root = ROOT / "integration" / "Orbital" / "main"
    config_dir = repo_root / "manifests"
    # We rebuild the system from existing sector manifests + override couplings
    system = load_system(
        config_dir / "sectors_global.json",
        config_dir / "couplings_global.json",
        params=params,
    )
    # Override couplings with provided dict
    system.couplings = deepcopy(coupling_dict)
    return system


def _coupling_pairs(base_couplings: dict) -> list[tuple[str, str]]:
    """Extract ordered list of (src, dst) coupling pairs."""
    pairs = []
    seen = set()
    for src, targets in base_couplings.items():
        for dst in targets:
            if (src, dst) not in seen:
                pairs.append((src, dst))
                seen.add((src, dst))
    return pairs


def _vec_to_couplings(x: np.ndarray, pairs: list[tuple[str, str]], base: dict) -> dict:
    """Convert flat parameter vector back to nested coupling dict."""
    c = deepcopy(base)
    for val, (src, dst) in zip(x, pairs):
        c[src][dst] = float(val)
    return c


def _run_steps(system, n_steps: int, params: dict):
    """Advance the orbital system n_steps and return final snapshot."""
    dt = params.get("dt", 0.0205)
    tau_eta = params.get("tau_eta", 0.0085)
    tau_reg = params.get("tau_reg", 0.0024)
    for _ in range(n_steps):
        system = orbital_step(system, dt=dt, tau_eta=tau_eta, tau_reg=tau_reg)
    return system


def make_objective(pairs, base_couplings, params, warm_steps, eba_data: dict):
    """Return composite objective over flat W vector.

    L = closure_penalty
        + 5.0 * max(0, 0.76 - ci)^2      ← push ci above safe-mode boundary
        + 2.0 * max(0, pen - 5.20)^2     ← push closure below standard threshold
        + 0.1  * Σ (W_ij - W0_ij)^2      ← regularize: stay close to baseline
    """
    call_count = [0]
    x0 = np.array([base_couplings[src][dst] for src, dst in pairs])

    def _ci_full(snap: dict) -> float:
        """Coherence index with EBA data injected from last bridge report."""
        raw = max(0.0, min(1.0, 1.0 - snap.get("R_H", 1.0)))
        coherent_fraction = eba_data.get("nonlocal_coherent_fraction", 0.0)
        eba_defect = eba_data.get("eba_defect_mean", 0.0)
        closure_score = eba_data.get("bridge_closure_score", 0.0)
        return 0.55 * raw + 0.20 * coherent_fraction + 0.15 * (1.0 - eba_defect) + 0.10 * closure_score

    def objective(x: np.ndarray) -> float:
        c = _vec_to_couplings(np.clip(x, 0.01, 1.0), pairs, base_couplings)
        system = _build_system(c, params)
        if warm_steps > 0:
            system = _run_steps(system, warm_steps, params)
        snap = snapshot(system)
        pen = closure_penalty(system)
        ci = _ci_full(snap)
        rh = snap.get("R_H", 1.0)

        L = pen
        L += 5.0 * max(0.0, 0.76 - ci) ** 2
        L += 2.0 * max(0.0, pen - 5.20) ** 2
        L += 0.1 * float(np.sum((np.clip(x, 0.01, 1.0) - x0) ** 2))

        call_count[0] += 1
        if call_count[0] % 20 == 0:
            print(f"  iter {call_count[0]:4d}  closure={pen:.4f}  ci={ci:.4f}  R_H={rh:.5f}  L={L:.4f}")
        return L

    return objective, _ci_full


def main() -> int:
    parser = argparse.ArgumentParser(description="Optimize W_ij coupling matrix to minimize closure_penalty.")
    parser.add_argument("--write", action="store_true", help="Write optimized couplings to couplings_global.json")
    parser.add_argument("--steps", type=int, default=3, help="Warm-up orbital steps before each evaluation (default: 3)")
    parser.add_argument("--max-iter", type=int, default=200, help="Max optimizer iterations (default: 200)")
    parser.add_argument("--tol", type=float, default=1e-4, help="Optimizer tolerance (default: 1e-4)")
    args = parser.parse_args()

    repo_root = ROOT / "integration" / "Orbital" / "main"
    config_dir = repo_root / "manifests"

    # Load baseline
    params = dict(DEFAULT_PARAMS)
    system0 = load_system(config_dir / "sectors_global.json", config_dir / "couplings_global.json", params=params)
    base_couplings = deepcopy(system0.couplings)

    snap0 = snapshot(system0, repo_root=repo_root)
    pen0 = closure_penalty(system0)
    rh0 = snap0["R_H"]
    ci0 = ci_fn(snap0)

    # Load EBA data from last bridge report for full ci computation
    bridge_report = ROOT / "integration" / "reports" / "orbital_bridge" / "orbital_bridge_report.json"
    eba_data: dict = {}
    if bridge_report.exists():
        try:
            br = json.loads(bridge_report.read_text())
            cp = br.get("ciel_pipeline", {}) or {}
            eba_data = {
                "nonlocal_coherent_fraction": float(cp.get("nonlocal_coherent_fraction", 0.0)),
                "eba_defect_mean": float(cp.get("eba_defect_mean", 0.0)),
                "bridge_closure_score": float(cp.get("bridge_closure_score", 0.0)),
            }
        except Exception:
            pass

    print("=" * 60)
    print("CIEL W_ij Optimizer — composite objective")
    print("=" * 60)
    print(f"Baseline  closure_penalty = {pen0:.4f}")
    print(f"Baseline  R_H             = {rh0:.6f}")
    print(f"Baseline  coherence_index = {ci0:.4f}")
    print(f"EBA data  coherent_frac   = {eba_data.get('nonlocal_coherent_fraction', 0):.4f}")
    print(f"EBA data  eba_defect_mean = {eba_data.get('eba_defect_mean', 0):.4f}")
    print(f"EBA data  closure_score   = {eba_data.get('bridge_closure_score', 0):.4f}")
    print(f"Target    closure_penalty < 5.20  AND  ci > 0.76  (exit safe mode)")
    print()

    pairs = _coupling_pairs(base_couplings)
    x0 = np.array([base_couplings[src][dst] for src, dst in pairs])
    bounds = [(0.01, 1.0)] * len(x0)

    print(f"Optimizing {len(pairs)} coupling parameters over {args.max_iter} iterations")
    print(f"Warm-up steps per evaluation: {args.steps}")
    print()

    obj, ci_full = make_objective(pairs, base_couplings, params, args.steps, eba_data)

    result = minimize(
        obj,
        x0,
        method="L-BFGS-B",
        bounds=bounds,
        options={"maxiter": args.max_iter, "ftol": args.tol, "gtol": 1e-5},
    )

    x_opt = np.clip(result.x, 0.01, 1.0)
    opt_couplings = _vec_to_couplings(x_opt, pairs, base_couplings)
    system_opt = _build_system(opt_couplings, params)
    snap_opt = snapshot(system_opt, repo_root=repo_root)
    pen_opt = closure_penalty(system_opt)
    rh_opt = snap_opt["R_H"]
    ci_opt = ci_full(snap_opt)

    control = recommend_control(snap_opt)
    health = build_health_manifest(snap_opt)
    state = build_state_manifest(snap_opt)

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Optimized closure_penalty = {pen_opt:.4f}  (was {pen0:.4f},  Δ={pen_opt-pen0:+.4f})")
    print(f"Optimized R_H             = {rh_opt:.6f}  (was {rh0:.6f})")
    print(f"Optimized coherence_index = {ci_opt:.4f}  (was {ci0:.4f})")
    print(f"Recommended mode          = {control['mode']}")
    print(f"System health             = {health['system_health']:.4f}")
    print(f"Optimizer success         = {result.success}  ({result.message})")
    print()

    print("Delta W_ij (changed couplings):")
    for (src, dst), x_new, x_old in zip(pairs, x_opt, x0):
        delta = x_new - x_old
        if abs(delta) > 1e-4:
            print(f"  {src:15s} → {dst:15s}  {x_old:.4f} → {x_new:.4f}  ({delta:+.4f})")

    print()
    print("Optimized W_ij matrix:")
    all_names = sorted({s for s, _ in pairs} | {d for _, d in pairs})
    header = f"{'':15s}" + "".join(f"{n:12s}" for n in all_names)
    print(header)
    for src in all_names:
        row = f"{src:15s}"
        for dst in all_names:
            val = opt_couplings.get(src, {}).get(dst, 0.0)
            row += f"{val:12.4f}"
        print(row)

    if args.write:
        # Save to couplings_wij_optimized.json — picked up by run_global_pass
        # as a post-build override that survives geometry re-extraction.
        override = {
            "schema": "ciel/wij-coupling-override/v0.1",
            "couplings": opt_couplings,
            "_optimizer_metadata": {
                "baseline_closure_penalty": pen0,
                "optimized_closure_penalty": pen_opt,
                "delta": round(pen_opt - pen0, 4),
                "optimizer": "L-BFGS-B",
                "warm_steps": args.steps,
                "recommended_mode": control["mode"],
                "system_health": health["system_health"],
            },
        }
        override_path = config_dir / "couplings_wij_optimized.json"
        override_path.write_text(json.dumps(override, indent=2, ensure_ascii=False))
        print(f"\nWrote W_ij override to {override_path}")
        print("(run_global_pass will merge these couplings after each geometry build)")
    else:
        print("\n(Dry run — pass --write to save couplings)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
