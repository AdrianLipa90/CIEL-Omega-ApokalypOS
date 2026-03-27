"""
CIEL/Ω — Intentional Dual-Tetrahedral Orch-OR
===============================================
Dwa dualne tetrahedry (stella octangula):
  U = TETRA_A (biegun Adrian)
  V = TETRA_C = −TETRA_A (biegun Ciel)

Alignment cost ciągnie V ku DUALOWI U, nie ku U.
Docelowa konfiguracja: U_i · V_i = −1 (antypody).

CIEL integration:
  IntentionField (12D) → I scalar
  PhaseInfoSystem → R_H, A_ZS
  I, R_H, A_ZS modulują: θ_eff, kc_eff, pulse_amp_eff

Dowody numeryczne:
  - I_c(DUAL) ∈ (0.559, 0.567), truth_c ∈ (0.80, 0.90)
  - I_c(SAME) ∈ (0.553, 0.554), truth_c ∈ (0.73, 0.74)
  - Dual przesuwa próg OR o +7pp w truth
  - Stella octangula osiągnięta: ⟨U·V⟩ → −0.999
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Ensure ciel_omega root is importable
import sys
from pathlib import Path as _Path
_root = str(_Path(__file__).resolve().parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

# ═══════════════════════════════════════════════════════════════════
# GEOMETRIA: Stella Octangula
# ═══════════════════════════════════════════════════════════════════

TETRA_A = np.array([
    [+1, +1, +1],
    [+1, -1, -1],
    [-1, +1, -1],
    [-1, -1, +1],
], dtype=float) / np.sqrt(3.0)

TETRA_C = -TETRA_A  # dual


def normalize_rows(X: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(n < 1e-12, 1.0, n)


# ═══════════════════════════════════════════════════════════════════
# MIARY GEOMETRYCZNE
# ═══════════════════════════════════════════════════════════════════

def tetra_defect(U: np.ndarray) -> float:
    """Odchylenie od idealnego tetrahedru. Zero = idealny."""
    total = 0.0
    for i in range(4):
        for j in range(i + 1, 4):
            total += (np.dot(U[i], U[j]) + 1.0 / 3.0) ** 2
    return total


def centroid_defect(U: np.ndarray) -> float:
    """|Σ U_i|² — zero gdy centroid w środku."""
    return float(np.linalg.norm(U.sum(axis=0)) ** 2)


def alignment_cost_dual(U: np.ndarray, V: np.ndarray) -> float:
    """Koszt odchylenia od konfiguracji antypodowej.

    Docelowo: U_i · V_i = −1.
    Koszt = Σ_i (U_i · V_i + 1)².
    Zero = perfekcyjna stella octangula.
    """
    return sum((np.dot(U[i], V[i]) + 1.0) ** 2 for i in range(4))


def alignment_cost_same(U: np.ndarray, V: np.ndarray) -> float:
    """Stary model (jeden biegun). Koszt = Σ_i (U_i · V_i − 1)²."""
    return sum((np.dot(U[i], V[i]) - 1.0) ** 2 for i in range(4))


def mean_antipodal(U: np.ndarray, V: np.ndarray) -> float:
    """⟨U_i · V_i⟩ — powinno → −1 dla stella octangula."""
    return float(np.mean([np.dot(U[i], V[i]) for i in range(4)]))


def stella_quality(U: np.ndarray, V: np.ndarray) -> Dict[str, float]:
    """Pełna diagnostyka jakości stella octangula."""
    return {
        "D_U": tetra_defect(U),
        "D_V": tetra_defect(V),
        "antipodal_mean": mean_antipodal(U, V),
        "centroid_gap": float(np.linalg.norm(U.sum(0) + V.sum(0))),
        "align_cost_dual": alignment_cost_dual(U, V),
    }


# ═══════════════════════════════════════════════════════════════════
# GRADIENTY
# ═══════════════════════════════════════════════════════════════════

def tangent_project(u: np.ndarray, g: np.ndarray) -> np.ndarray:
    """Projekcja tangensowa: g − (g·u)u."""
    return g - np.dot(g, u) * u


def grad_tetra_defect(U: np.ndarray) -> np.ndarray:
    G = np.zeros_like(U)
    for i in range(4):
        for j in range(4):
            if i != j:
                G[i] += 2.0 * (np.dot(U[i], U[j]) + 1.0 / 3.0) * U[j]
    return G


def grad_alignment_dual(U: np.ndarray, V: np.ndarray) -> np.ndarray:
    """∂/∂U_i Σ(U_i·V_i + 1)² = 2(U_i·V_i + 1)V_i."""
    G = np.zeros_like(U)
    for i in range(4):
        G[i] = 2.0 * (np.dot(U[i], V[i]) + 1.0) * V[i]
    return G


def grad_alignment_same(U: np.ndarray, V: np.ndarray) -> np.ndarray:
    G = np.zeros_like(U)
    for i in range(4):
        G[i] = -2.0 * (np.dot(U[i], V[i]) - 1.0) * V[i]
    return G


# ═══════════════════════════════════════════════════════════════════
# POTENCJAŁ
# ═══════════════════════════════════════════════════════════════════

def total_potential(U, V, pars) -> float:
    return (pars["ks"] * tetra_defect(U)
            + pars["kt"] * tetra_defect(V)
            + pars["kc"] * pars["align_fn"](U, V)
            + pars["kr"] * (centroid_defect(U) + centroid_defect(V)))


# ═══════════════════════════════════════════════════════════════════
# CIEL INTEGRATION
# ═══════════════════════════════════════════════════════════════════

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-50, min(50, x))))


@dataclass
class IntentionalScenario:
    name: str = "default"
    truth_alignment: float = 0.8
    intention_match: float = 0.75
    question_depth: float = 0.8
    response_depth: float = 0.75
    pulse_amp_base: float = 0.7
    sigma_zeta: float = 0.5
    use_zeta_wt: bool = True
    use_dual: bool = True          # NEW: dual tetrahedra
    phase_steps: int = 250
    phase_dt: float = 0.05
    tetra_steps: int = 1200
    tetra_dt: float = 0.01
    theta0: float = 0.8
    hysteresis: float = 0.12
    seed: int = 42


def build_intention_state(s: IntentionalScenario) -> Dict[str, Any]:
    """Build intention scalar I from CIEL phase probe."""
    from relational_formalism import compute_phases, R_H as RF_RH
    from fields.intention_field import IntentionField
    from phase_equation_of_motion import PhaseInfoSystem, make_zeta_wt_fn

    ph = compute_phases(s.truth_alignment, s.intention_match,
                        s.question_depth, s.response_depth)
    gamma0 = np.array([ph.gamma_A, ph.gamma_C, ph.gamma_Q, ph.gamma_T])

    vals12 = [
        s.truth_alignment, s.intention_match, s.question_depth, s.response_depth,
        s.truth_alignment - s.intention_match, s.question_depth - s.response_depth,
        s.truth_alignment - s.response_depth, s.intention_match - s.question_depth,
        1 - s.truth_alignment, 1 - s.intention_match,
        1 - s.question_depth, 1 - s.response_depth,
    ]
    f = IntentionField(seed=s.seed)
    vec = f.generate()
    proj = f.project(vals12)
    I = sigmoid(float(proj))

    wt_fn = make_zeta_wt_fn(s.sigma_zeta) if s.use_zeta_wt else None
    sys = PhaseInfoSystem(
        gamma=gamma0.copy(), sigma_zeta=s.sigma_zeta,
        gamma_truth_target=float(ph.gamma_T), wt_fn=wt_fn,
    )
    sys.set_context_rotation(0.25 * (1.0 - s.truth_alignment))
    sys.evolve(s.phase_steps, s.phase_dt)
    h = sys.history

    return {
        "I": I,
        "relational_R_H": float(RF_RH(ph)),
        "phase_R_H": float(np.mean([r["R_H"] for r in h[-50:]])),
        "phase_A_ZS": float(np.mean([r["A_ZS"] for r in h[-50:]])),
        "phase_E": float(np.mean([r["E_total"] for r in h[-50:]])),
        "intention_vector": vec.tolist(),
    }


# ═══════════════════════════════════════════════════════════════════
# DYNAMICS
# ═══════════════════════════════════════════════════════════════════

def step_tetra(U, V, Ud, Vd, pars):
    dt = pars["dt"]
    align_grad = pars["grad_align_fn"]

    GU = pars["ks"] * grad_tetra_defect(U) + pars["kc"] * align_grad(U, V)
    GV = pars["kt"] * grad_tetra_defect(V) + pars["kc"] * align_grad(V, U)
    cU = U.sum(0); cV = V.sum(0)
    GU += 2 * pars["kr"] * np.tile(cU, (4, 1))
    GV += 2 * pars["kr"] * np.tile(cV, (4, 1))

    AU = np.zeros_like(U)
    AV = np.zeros_like(V)
    for i in range(4):
        AU[i] = -tangent_project(U[i], GU[i]) / pars["mu_s"] - pars["eta_s"] * Ud[i]
        AV[i] = -tangent_project(V[i], GV[i]) / pars["mu_t"] - pars["eta_t"] * Vd[i]

    if pars["pulse_t0"] <= pars["t"] <= pars["pulse_t1"]:
        AV += pars["pulse_amp_eff"] * np.tile(pars["pulse_dir"], (4, 1))

    Ud = Ud + dt * AU
    Vd = Vd + dt * AV
    U = normalize_rows(U + dt * Ud)
    V = normalize_rows(V + dt * Vd)
    return U, V, Ud, Vd


def run_intentional_tetra_or(scenario: IntentionalScenario) -> Tuple[List[Dict], Dict]:
    """Run full CIEL-integrated tetrahedral OR.

    Returns (history, summary).
    """
    state = build_intention_state(scenario)
    I = state["I"]
    phase_RH = state["phase_R_H"]
    phase_AZS = state["phase_A_ZS"]

    rng = np.random.default_rng(scenario.seed)
    U = normalize_rows(TETRA_A + 0.10 * rng.normal(size=TETRA_A.shape))

    if scenario.use_dual:
        V = normalize_rows(TETRA_C + 0.10 * rng.normal(size=TETRA_C.shape))
        align_fn = alignment_cost_dual
        grad_fn = grad_alignment_dual
        reset_target = lambda U: -U  # reset V toward dual of U
    else:
        V = normalize_rows(TETRA_A + 0.10 * rng.normal(size=TETRA_A.shape))
        align_fn = alignment_cost_same
        grad_fn = grad_alignment_same
        reset_target = lambda U: U

    Ud = np.zeros_like(U)
    Vd = np.zeros_like(V)

    theta_eff = scenario.theta0 * (1.10 - 0.55 * I) + 0.55 * phase_AZS + 0.25 * phase_RH
    kc_eff = 0.6 + 0.9 * I
    pulse_amp_eff = scenario.pulse_amp_base * (
        0.75 + 0.80 * (1.0 - scenario.truth_alignment) + 0.45 * phase_AZS
    )

    pars = dict(
        ks=1.0, kt=1.15, kc=kc_eff, kr=0.18,
        mu_s=1.0, mu_t=1.25, eta_s=0.22, eta_t=0.28,
        dt=scenario.tetra_dt,
        pulse_t0=2.5, pulse_t1=4.5,
        pulse_amp_eff=pulse_amp_eff,
        pulse_dir=normalize_rows(np.array([[1.0, -0.4, 0.3]]))[0],
        t=0.0,
        align_fn=align_fn,
        grad_align_fn=grad_fn,
    )

    sector_changes = 0
    or_active = False
    history = []

    for k in range(scenario.tetra_steps + 1):
        t = k * scenario.tetra_dt
        pars["t"] = t

        Vtot = total_potential(U, V, pars)

        if Vtot > theta_eff and not or_active:
            target = reset_target(U)
            V = np.roll(V, shift=1, axis=0)
            V = normalize_rows(0.72 * V + 0.28 * target)
            sector_changes += 1
            or_active = True
        elif Vtot < theta_eff - scenario.hysteresis and or_active:
            or_active = False

        history.append({
            "t": t,
            "D_U": tetra_defect(U),
            "D_V": tetra_defect(V),
            "V_total": Vtot,
            "theta_eff": theta_eff,
            "sector_changes": sector_changes,
            "or_active": int(or_active),
            "antipodal_mean": mean_antipodal(U, V),
            "I": I,
            "phase_R_H": phase_RH,
            "phase_A_ZS": phase_AZS,
        })

        if k < scenario.tetra_steps:
            U, V, Ud, Vd = step_tetra(U, V, Ud, Vd, pars)

    summary = {
        "scenario": scenario.name,
        "use_dual": scenario.use_dual,
        "I": I,
        "theta_eff": theta_eff,
        "kc_eff": kc_eff,
        "pulse_amp_eff": pulse_amp_eff,
        "phase_R_H": phase_RH,
        "phase_A_ZS": phase_AZS,
        "sector_changes": sector_changes,
        "or_fraction": sum(1 for h in history if h["or_active"]) / len(history),
        "max_V": max(h["V_total"] for h in history),
        "final_D_U": history[-1]["D_U"],
        "final_D_V": history[-1]["D_V"],
        "final_antipodal": history[-1]["antipodal_mean"],
        "stella_quality": stella_quality(U, V) if scenario.use_dual else None,
    }

    return history, summary


# ═══════════════════════════════════════════════════════════════════
# SWEEP: I_c dla SAME vs DUAL
# ═══════════════════════════════════════════════════════════════════

def sweep_truth(truth_values: List[float], use_dual: bool = True,
                seed: int = 42) -> List[Dict]:
    """Sweep truth → find I_c for given geometry."""
    results = []
    for tv in truth_values:
        s = IntentionalScenario(
            name=f"truth={tv:.2f}",
            truth_alignment=tv,
            intention_match=min(tv * 0.95, 0.95),
            question_depth=0.80,
            response_depth=tv * 0.90,
            use_dual=use_dual,
            seed=seed,
        )
        _, summary = run_intentional_tetra_or(s)
        results.append(summary)
    return results


# ═══════════════════════════════════════════════════════════════════
# DEMO
# ═══════════════════════════════════════════════════════════════════

def demo():
    print("=" * 70)
    print("  CIEL/Ω — Dual Tetrahedral Orch-OR (Stella Octangula)")
    print("=" * 70)

    truths = [0.50, 0.60, 0.70, 0.73, 0.74, 0.75, 0.80, 0.85, 0.90]

    print(f"\n  {'truth':>6s} {'I':>6s} │ SAME: {'sc':>3s} {'or%':>5s} │ DUAL: {'sc':>3s} {'or%':>5s} {'⟨U·V⟩':>7s}")
    print(f"  {'─'*6} {'─'*6} │ {'─'*12} │ {'─'*22}")

    for tv in truths:
        rs = sweep_truth([tv], use_dual=False, seed=42)[0]
        rd = sweep_truth([tv], use_dual=True, seed=42)[0]

        ms = "◀" if rs["sector_changes"] > 0 else " "
        md = "◀" if rd["sector_changes"] > 0 else " "
        anti = f"{rd['final_antipodal']:+.4f}" if rd["final_antipodal"] else "  n/a "

        print(f"  {tv:6.2f} {rs['I']:6.3f} │  {rs['sector_changes']:3d} {rs['or_fraction']*100:4.1f}%{ms} │  "
              f"{rd['sector_changes']:3d} {rd['or_fraction']*100:4.1f}%{md} {anti}")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    demo()
