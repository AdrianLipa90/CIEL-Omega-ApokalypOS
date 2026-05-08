"""Euler Constraint — Perturbation Recovery Test.

Scenariusz:
  1. Baseline — rejestruj closure_score bez zaburzenia
  2. Perturbacja — wstrzyknij klaster anty-fazowy (przesunięcie o π) w wybranych sektorach
  3. Recovery — N kroków orbital feedback, mierz closure_score per krok
  4. Klasyfikacja — gładki powrót / oscylacje / quasi-atraktor / dryf

Użycie:
    python3 scripts/test_euler_perturbation.py [--steps N] [--eta ETA] [--sectors memory,affect]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np

# -- path setup ---------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
_CIEL1 = _HERE.parent
for _p in [
    str(_CIEL1 / 'src'),
    str(_CIEL1 / 'src' / 'CIEL_OMEGA_COMPLETE_SYSTEM'),
]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ciel_omega.constraints.euler_constraint import (   # noqa: E402
    evaluate_unified_euler_constraint,
    apply_active_euler_feedback,
    EulerConstraintReport,
)

# -- mock objects -------------------------------------------------------------

def _make_memory(n_channels: int = 8, seed: int = 42) -> SimpleNamespace:
    """Lightweight memory mock — state.phases + identity_field.phase."""
    rng = np.random.default_rng(seed)
    phases = list(rng.uniform(0, 2 * math.pi, n_channels))
    state = SimpleNamespace(phases=phases)
    identity_field = SimpleNamespace(phase=float(np.mean(phases)))
    return SimpleNamespace(state=state, identity_field=identity_field)


def _make_core(n: int = 4, seed: int = 7) -> SimpleNamespace:
    """Lightweight core mock — I_field, S_field, tau_field, Lambda0_field."""
    rng = np.random.default_rng(seed)
    amp = rng.uniform(0.5, 1.5, n)
    phi = rng.uniform(0, 2 * math.pi, n)
    I_field = amp * np.exp(1j * phi)
    S_field = amp[::-1] * np.exp(1j * (phi + 0.3))
    tau_field = rng.uniform(0.2, 0.8, n)
    Lambda0_field = rng.uniform(-0.5, 0.5, n)
    return SimpleNamespace(
        I_field=I_field,
        S_field=S_field,
        tau_field=tau_field,
        Lambda0_field=Lambda0_field,
    )


def _empty_eba(memory: Any) -> dict:
    phases = np.asarray(memory.state.phases, dtype=float)
    return {
        f'm{i}': {'defect_magnitude': float(abs(math.atan2(math.sin(p), math.cos(p)))),
                  'is_coherent': True}
        for i, p in enumerate(phases)
    }


# -- perturbation -------------------------------------------------------------

def inject_antiphase(memory: Any, core: Any, sectors: list[str]) -> None:
    """Shift phases of requested sectors by π — maximum perturbation."""
    if 'memory' in sectors:
        memory.state.phases = [(p + math.pi) % (2 * math.pi) for p in memory.state.phases]
        if hasattr(memory.identity_field, 'phase'):
            memory.identity_field.phase = (memory.identity_field.phase + math.pi) % (2 * math.pi)
    if 'core' in sectors:
        for field_name in ('I_field', 'S_field'):
            f = np.asarray(getattr(core, field_name))
            setattr(core, field_name, f * (-1))          # multiply by -1 = shift phase by π
    if 'affect' in sectors:
        pass   # affect is rebuilt from metadata each step — perturbation is implicit
    if 'vocabulary' in sectors:
        pass   # vocabulary is rebuilt from records each step


# -- one step of feedback -----------------------------------------------------

def feedback_step(memory: Any, core: Any,
                  prev_mem_phases: np.ndarray | None,
                  prev_core_phases: dict | None,
                  eta: float) -> tuple[EulerConstraintReport, EulerConstraintReport, bool]:
    """Evaluate + apply feedback. Returns (before, after, rolled_back)."""
    eba = _empty_eba(memory)
    before = evaluate_unified_euler_constraint(memory, core, eba)
    after, rolled_back = apply_active_euler_feedback(
        memory, core, before,
        prev_memory_phases=prev_mem_phases,
        prev_core_phases=prev_core_phases,
        eta=eta,
    )
    return before, after, rolled_back


# -- classification -----------------------------------------------------------

def classify_response(history: list[dict]) -> str:
    """Return: smooth_recovery / oscillating / quasi_attractor / drift."""
    scores = [h['closure_score'] for h in history]
    if not scores:
        return 'no_data'

    baseline = scores[0]
    final = scores[-1]
    mid = scores[len(scores) // 2]

    improvement = final - baseline
    oscillation = float(np.std(np.diff(scores)))

    if improvement > 0.15 and oscillation < 0.03:
        return 'smooth_recovery'
    elif oscillation > 0.05:
        return 'oscillating'
    elif abs(final - mid) < 0.02 and abs(final - baseline) > 0.05:
        return 'quasi_attractor'
    elif improvement < -0.05:
        return 'drift'
    else:
        return 'partial_recovery'


# -- W_ij axis distance -------------------------------------------------------

def wij_axis_distance(identity_phase: float, w_ij_poles: tuple[float, float] = (0.0, math.pi)) -> float:
    """Distance from identity_phase to the W_ij geodesic (axis on Bloch sphere).

    W_ij projects the two identity poles (i=0, j=π by default) onto the
    Poincaré disk. The geodesic between them is the real axis.
    Distance = |sin(φ_I − midpoint)| where midpoint = mean of the two poles.
    """
    midpoint = (w_ij_poles[0] + w_ij_poles[1]) / 2.0
    return float(abs(math.sin(identity_phase - midpoint)))


# -- main run -----------------------------------------------------------------

def run_test(steps: int = 20, eta: float = 0.08, perturb_sectors: list[str] | None = None,
             seed: int = 42) -> dict:
    if perturb_sectors is None:
        perturb_sectors = ['memory', 'affect']

    memory = _make_memory(seed=seed)
    core = _make_core(seed=seed)

    history: list[dict] = []
    prev_mem_phases: np.ndarray | None = None
    prev_core_phases: dict | None = None

    # -- baseline (step 0, no perturbation) ---
    eba = _empty_eba(memory)
    report0 = evaluate_unified_euler_constraint(memory, core, eba)
    history.append({
        'step': 0,
        'phase': 'baseline',
        'closure_score': round(report0.closure_score, 5),
        'unified_euler_violation': round(report0.unified_euler_violation, 5),
        'identity_phase': round(getattr(memory.identity_field, 'phase', 0.0), 5),
        'wij_distance': round(wij_axis_distance(getattr(memory.identity_field, 'phase', 0.0)), 5),
        'rolled_back': False,
    })

    # -- inject perturbation ---
    inject_antiphase(memory, core, perturb_sectors)
    eba = _empty_eba(memory)
    report_p = evaluate_unified_euler_constraint(memory, core, eba)
    history.append({
        'step': 0,
        'phase': 'post_perturbation',
        'closure_score': round(report_p.closure_score, 5),
        'unified_euler_violation': round(report_p.unified_euler_violation, 5),
        'identity_phase': round(getattr(memory.identity_field, 'phase', 0.0), 5),
        'wij_distance': round(wij_axis_distance(getattr(memory.identity_field, 'phase', 0.0)), 5),
        'rolled_back': False,
    })

    # -- recovery steps ---
    for step in range(1, steps + 1):
        mem_before = np.asarray(memory.state.phases, dtype=float).copy()
        core_before = {
            'I_field': np.angle(np.asarray(core.I_field)),
            'S_field': np.angle(np.asarray(core.S_field)),
        }

        before, after, rolled_back = feedback_step(
            memory, core, prev_mem_phases, prev_core_phases, eta=eta
        )

        prev_mem_phases = mem_before
        prev_core_phases = core_before

        history.append({
            'step': step,
            'phase': 'recovery',
            'closure_score': round(after.closure_score, 5),
            'unified_euler_violation': round(after.unified_euler_violation, 5),
            'identity_phase': round(getattr(memory.identity_field, 'phase', 0.0), 5),
            'wij_distance': round(wij_axis_distance(getattr(memory.identity_field, 'phase', 0.0)), 5),
            'rolled_back': rolled_back,
            'regulation_strength': round(after.regulation_strength, 5),
        })

    classification = classify_response([h for h in history if h['phase'] == 'recovery'])
    delta_closure = history[-1]['closure_score'] - history[1]['closure_score']

    return {
        'config': {
            'steps': steps,
            'eta': eta,
            'perturb_sectors': perturb_sectors,
            'seed': seed,
        },
        'baseline_closure': history[0]['closure_score'],
        'post_perturbation_closure': history[1]['closure_score'],
        'final_closure': history[-1]['closure_score'],
        'delta_closure': round(delta_closure, 5),
        'classification': classification,
        'history': history,
    }


def print_summary(result: dict) -> None:
    cfg = result['config']
    print(f"\n{'─'*60}")
    print(f"  Euler Perturbation Test  |  eta={cfg['eta']}  steps={cfg['steps']}")
    print(f"  Perturbed sectors: {cfg['perturb_sectors']}")
    print(f"{'─'*60}")
    print(f"  Baseline closure:          {result['baseline_closure']:.5f}")
    print(f"  Post-perturbation closure: {result['post_perturbation_closure']:.5f}  (drop: {result['post_perturbation_closure']-result['baseline_closure']:+.5f})")
    print(f"  Final closure:             {result['final_closure']:.5f}  (Δ from perturb: {result['delta_closure']:+.5f})")
    print(f"  Classification:            {result['classification'].upper()}")
    print(f"{'─'*60}")
    print(f"  {'step':>4}  {'closure':>8}  {'violation':>9}  {'wij_dist':>8}  {'rollback':>8}")
    for h in result['history']:
        tag = '← PERTURB' if h['phase'] == 'post_perturbation' else ''
        rb = 'YES' if h.get('rolled_back') else ''
        print(f"  {h['step']:>4}  {h['closure_score']:>8.5f}  {h['unified_euler_violation']:>9.5f}  {h['wij_distance']:>8.5f}  {rb:>8}  {tag}")
    print()


def _print_diagnostic_note(result: dict) -> None:
    rollbacks = sum(1 for h in result['history'] if h.get('rolled_back'))
    total_recovery = sum(1 for h in result['history'] if h['phase'] == 'recovery')
    if rollbacks == total_recovery and total_recovery > 0:
        print("⚠  DIAGNOSTIC: Every recovery step was rolled back.")
        print("   Cause: euler_constraint_violation = |Σφ mod 2π| / 2π (sum-based).")
        print("   _apply_phase_pull targets circular_mean — a DIFFERENT metric.")
        print("   The pull increases violation even when improving coherence.")
        print("   → Mismatch between feedback target (circular mean)")
        print("     and rollback criterion (phase sum mod 2π).")
        print("   This is the structural gap identified in the analysis.")
        print()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Euler Perturbation Recovery Test')
    parser.add_argument('--steps', type=int, default=20, help='Recovery steps (default: 20)')
    parser.add_argument('--eta', type=float, default=0.08, help='Damping coefficient (default: 0.08)')
    parser.add_argument('--sectors', type=str, default='memory,affect',
                        help='Sectors to perturb, comma-separated (default: memory,affect)')
    parser.add_argument('--seed', type=int, default=42, help='RNG seed')
    parser.add_argument('--json', action='store_true', help='Output raw JSON instead of table')
    parser.add_argument('--compare-eta', action='store_true',
                        help='Run with eta=0 vs eta=0.08 and compare')
    args = parser.parse_args()

    sectors = [s.strip() for s in args.sectors.split(',')]

    if args.compare_eta:
        result_nodamp = run_test(steps=args.steps, eta=0.0, perturb_sectors=sectors, seed=args.seed)
        result_damp   = run_test(steps=args.steps, eta=args.eta, perturb_sectors=sectors, seed=args.seed)
        print("\n=== NO DAMPING (eta=0.0) ===")
        print_summary(result_nodamp)
        print("=== WITH DAMPING (eta={:.2f}) ===".format(args.eta))
        print_summary(result_damp)
        _print_diagnostic_note(result_nodamp)
        if args.json:
            print(json.dumps({'no_damp': result_nodamp, 'damp': result_damp}, indent=2))
    else:
        result = run_test(steps=args.steps, eta=args.eta, perturb_sectors=sectors, seed=args.seed)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print_summary(result)
            _print_diagnostic_note(result)


# (defined above main block)
def _print_diagnostic_note_stub() -> None:  # noqa — real def is above if __name__
    rollbacks = sum(1 for h in result['history'] if h.get('rolled_back'))
    total_recovery = sum(1 for h in result['history'] if h['phase'] == 'recovery')
    if rollbacks == total_recovery and total_recovery > 0:
        print("⚠  DIAGNOSTIC: Every recovery step was rolled back.")
        print("   Cause: euler_constraint_violation = |Σφ mod 2π| / 2π (sum-based).")
        print("   _apply_phase_pull targets circular_mean — a DIFFERENT metric.")
        print("   The pull increases violation even when improving coherence.")
        print("   → Mismatch between feedback target (circular mean)")
        print("     and rollback criterion (phase sum mod 2π).")
        print("   This is the structural gap identified in the analysis.")
        print()
