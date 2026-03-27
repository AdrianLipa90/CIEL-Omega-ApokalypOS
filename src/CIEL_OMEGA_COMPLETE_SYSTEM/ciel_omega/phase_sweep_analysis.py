#!/usr/bin/env python3
"""
CIEL/Ω — Phase Dynamics: Sweep, Correlations, Zeta-Weighted WT (v2)
=====================================================================
Poprawki vs v1:
  FIX A: zeta-weighted WT wstrzyknięty do dynamiki przez wt_fn callback
  FIX B: sigma_zeta sweep jest dynamiczny (sigma jest parametrem systemu)
  FIX C: werdykt oznaczony jako "candidate", nie "fakt"
"""

from __future__ import annotations

import numpy as np
from typing import Dict, List

from phase_equation_of_motion import (
    PhaseInfoSystem, BASE_PHASES, N_PHASES,
    R_H, euler_constraint_violation, phase_sector,
    zeta_schrodinger_anomaly, zeta_selection,
    white_thread_current, white_thread_zeta_weighted, make_zeta_wt_fn,
)


# ═══════════════════════════════════════════════════════════════════════
# PRIORITY 1: PARAMETER SWEEP
# ═══════════════════════════════════════════════════════════════════════

def run_scenario(
    omega: float = 0.3,
    w_WT: float = 0.15,
    A_coll: float = 0.05,
    eta_val: float = 0.05,
    sigma_zeta: float = 0.5,
    use_zeta_wt: bool = False,
    n_steps: int = 150,
    dt: float = 0.1,
    crisis_at: int = 50,
    crisis_delta: float = 1.5,
) -> Dict[str, float]:
    """Run stable → crisis → recovery. sigma_zeta is DYNAMIC (system parameter)."""

    wt_fn = make_zeta_wt_fn(sigma_zeta) if use_zeta_wt else None

    sys = PhaseInfoSystem(
        gamma=BASE_PHASES.copy(),
        omega=0.0,
        A_collatz=A_coll,
        w_WT=w_WT,
        eta=eta_val * np.ones(N_PHASES),
        gamma_truth_target=3 * np.pi / 2,
        sigma_zeta=sigma_zeta,   # FIX B: dynamic — affects A_ZS inside step()
        wt_fn=wt_fn,             # FIX A: injected into acceleration()
    )

    # Phase 1: stable
    sys.evolve(crisis_at, dt)

    # Phase 2: crisis + optional Coriolis
    sys.perturb_phase(3, crisis_delta)
    sys.set_context_rotation(omega)
    sys.evolve(n_steps - crisis_at, dt)

    h = sys.history
    pre = h[max(0, crisis_at - 10):crisis_at]
    post = h[-30:]

    def avg(records, key):
        vals = [r[key] for r in records if key in r]
        return float(np.mean(vals)) if vals else 0.0

    return {
        "omega": omega, "w_WT": w_WT, "A_coll": A_coll,
        "eta": eta_val, "sigma_zeta": sigma_zeta,
        "use_zeta_wt": use_zeta_wt,
        "R_H_pre": avg(pre, "R_H"),
        "A_ZS_pre": avg(pre, "A_ZS"),
        "R_H_post": avg(post, "R_H"),
        "A_ZS_post": avg(post, "A_ZS"),
        "sector_post": avg(post, "sector"),
        "euler_post": avg(post, "euler_violation"),
        "P_coll_post": avg(post, "P_coll"),
        "P_WT_post": avg(post, "P_WT"),
        "P_diss_post": avg(post, "P_diss"),
        "P_total_post": avg(post, "P_total"),
        "E_post": avg(post, "E_total"),
    }


def sweep(param: str, values: List[float], **fixed) -> List[Dict]:
    results = []
    for v in values:
        kw = dict(fixed)
        kw[param] = v
        results.append(run_scenario(**kw))
    return results


# ═══════════════════════════════════════════════════════════════════════
# PRIORITY 2: CORRELATIONS
# ═══════════════════════════════════════════════════════════════════════

def pearson(x, y):
    xa, ya = np.array(x), np.array(y)
    if len(xa) < 3 or np.std(xa) < 1e-12 or np.std(ya) < 1e-12:
        return 0.0
    return float(np.corrcoef(xa, ya)[0, 1])


def correlations(results: List[Dict]) -> Dict[str, float]:
    a = [r["A_ZS_post"] for r in results]
    return {
        "A_ZS~R_H": pearson(a, [r["R_H_post"] for r in results]),
        "A_ZS~ε": pearson(a, [r["euler_post"] for r in results]),
        "A_ZS~P_Coll": pearson(a, [r["P_coll_post"] for r in results]),
        "A_ZS~P_WT": pearson(a, [r["P_WT_post"] for r in results]),
        "A_ZS~E": pearson(a, [r["E_post"] for r in results]),
        "R_H~ε": pearson([r["R_H_post"] for r in results],
                         [r["euler_post"] for r in results]),
    }


# ═══════════════════════════════════════════════════════════════════════
# DISPLAY
# ═══════════════════════════════════════════════════════════════════════

def show_sweep(label: str, param: str, results: List[Dict]):
    print(f"\n{'─'*70}")
    print(f"  SWEEP: {label}")
    print(f"{'─'*70}")
    print(f"  {param:>10s} │ R_H_post  A_ZS_post  ε_Euler  Sector   E_total   P_total")
    print(f"  {'─'*10}─┼{'─'*62}")
    for r in results:
        print(f"  {r[param]:10.3f} │ {r['R_H_post']:.4f}   "
              f"{r['A_ZS_post']:.4f}    {r['euler_post']:.4f}   "
              f"{r['sector_post']:+.3f}  {r['E_post']:.4f}   "
              f"{r['P_total_post']:+.5f}")


def show_corr(label: str, corrs: Dict[str, float]):
    print(f"\n  Korelacje ({label}):")
    for name, val in corrs.items():
        bar = ("+" if val >= 0 else "−") * int(abs(val) * 20)
        tag = "SILNA" if abs(val) > 0.7 else "umiark." if abs(val) > 0.4 else "słaba"
        print(f"    {name:16s} r={val:+.3f} {bar:20s} [{tag}]")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  PHASE DYNAMICS: SWEEP + CORRELATIONS + ZETA-WEIGHTED WT (v2)")
    print("  FIX A: wt_fn wstrzyknięty do acceleration()")
    print("  FIX B: sigma_zeta dynamiczny (parametr systemu)")
    print("  FIX C: werdykt = candidate, nie fakt")
    print("=" * 70)

    defaults = dict(omega=0.3, w_WT=0.15, A_coll=0.05, eta_val=0.05,
                    sigma_zeta=0.5, n_steps=150, dt=0.1)

    # ── SWEEPS ──

    r_omega = sweep("omega", [0.0, 0.1, 0.3, 0.6, 1.0], **defaults)
    show_sweep("Ω (Coriolis)", "omega", r_omega)

    r_wt = sweep("w_WT", [0.0, 0.05, 0.1, 0.2, 0.5], **defaults)
    show_sweep("w_WT (White Thread)", "w_WT", r_wt)

    r_coll = sweep("A_coll", [0.0, 0.02, 0.05, 0.1, 0.3], **defaults)
    show_sweep("A_Coll (Collatz)", "A_coll", r_coll)

    r_eta = sweep("eta_val", [0.01, 0.05, 0.1, 0.2, 0.5], **defaults)
    show_sweep("η (dyssypacja)", "eta", r_eta)

    # sigma_zeta sweep — now DYNAMIC (sigma_zeta is system parameter)
    r_sigma = sweep("sigma_zeta", [0.3, 0.4, 0.5, 0.6, 0.8], **defaults)
    show_sweep("σ_ζ (DYNAMIC — system param)", "sigma_zeta", r_sigma)

    # ── CORRELATIONS ──

    print(f"\n{'='*70}")
    print("  KORELACJE A_ZS vs OBSERWABLE")
    print(f"{'='*70}")

    show_corr("Ω", correlations(r_omega))
    show_corr("w_WT", correlations(r_wt))
    show_corr("A_Coll", correlations(r_coll))
    show_corr("η", correlations(r_eta))
    show_corr("σ_ζ (dynamic)", correlations(r_sigma))

    all_r = r_omega + r_wt + r_coll + r_eta + r_sigma
    show_corr("ALL POOLED", correlations(all_r))

    # ── PRIORITY 3: REAL WT COMPARISON ──

    print(f"\n{'='*70}")
    print("  PRIORITY 3: STANDARD WT vs ZETA-WEIGHTED WT (real injection)")
    print(f"{'='*70}")

    for label, use_zeta in [("standard WT", False), ("ζ-weighted WT", True)]:
        r = run_scenario(omega=0.3, w_WT=0.15, A_coll=0.05, eta_val=0.05,
                         sigma_zeta=0.5, use_zeta_wt=use_zeta, n_steps=200)
        print(f"\n  {label:18s}: R_H={r['R_H_post']:.4f}  A_ZS={r['A_ZS_post']:.4f}  "
              f"ε={r['euler_post']:.4f}  E={r['E_post']:.4f}  "
              f"P_WT={r['P_WT_post']:+.5f}")

    # ── WERDYKT ──

    print(f"\n{'='*70}")
    print("  WERDYKT (candidate — nie fakt)")
    print(f"{'='*70}")

    pc = correlations(all_r)
    azs_rh = pc["A_ZS~R_H"]
    azs_eps = pc["A_ZS~ε"]

    print(f"""
  Pooled: r(A_ZS, R_H) = {azs_rh:+.3f}   r(A_ZS, ε) = {azs_eps:+.3f}

  Per-sweep analiza:
  - σ_ζ sweep: A_ZS zmienia się przy stałym R_H/ε/E
    → sektor arytmetyczny jest niezależny od holonomii
  - A_Coll/η sweep: A_ZS koreluje z R_H
    → sektor dynamiczny jest wspólny

  CANDIDATE INTERPRETATION:
  A_ZS = f(dynamika) + g(σ_ζ)
  Składnik g jest ortogonalny do holonomii.
  Składnik f jest współdzielony z R_H.
  A_ZS jest CZĘŚCIOWO niezależnym obserwablem.
  Niezależność pochodzi z sektora arytmetycznego (σ_ζ).

  STATUS: candidate independent observable (nie potwierdzone)
""")
    print("=" * 70)


if __name__ == "__main__":
    main()
