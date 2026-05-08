"""Kepler emergence simulation under CIEL dynamics.

Tests whether Bloch-sphere phase orbits with M_sem inertia reproduce
Kepler's laws when closure_penalty acts as gravitational potential V(r) ~ -k/r.

Physics model:
  - Position: phase angle φ on Bloch sphere → projected to Poincaré disk radius ρ
  - Potential: V(ρ) = -k / ρ  (closure_penalty as effective gravity)
  - Inertia: m_eff = M_sem (semantic mass)
  - EOM: m_eff * d²φ/dt² = -dV/dφ - η * dφ/dt  (damped Kepler)

Kepler emergence check:
  1. T² ∝ a³           (Third law)
  2. A = const         (Second law: equal areas → conserved angular momentum)
  3. Orbit closure < ε (First law: ellipse closes — no precession)

Output: table + orbit closure score per sector
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import NamedTuple

import numpy as np

_HERE = Path(__file__).resolve().parent
_SRC  = _HERE.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
if str(_SRC / "CIEL_OMEGA_COMPLETE_SYSTEM") not in sys.path:
    sys.path.insert(0, str(_SRC / "CIEL_OMEGA_COMPLETE_SYSTEM"))

from ciel_geometry.semantic_mass import build_mass_table, SemanticMassRecord


# ── Poincaré disk geometry ────────────────────────────────────────────────────

def poincare_from_bloch(theta: float) -> float:
    """Map Bloch polar angle θ ∈ [0,π] → Poincaré disk radius ρ ∈ [0,1)."""
    return math.tan(theta / 2.0) / (1.0 + 1e-9)   # stereographic


def bloch_from_poincare(rho: float) -> float:
    """Inverse: ρ → θ."""
    rho = min(rho, 0.9999)
    return 2.0 * math.atan(rho)


# ── Gravitational potential ───────────────────────────────────────────────────

def V(rho: float, k: float = 1.0) -> float:
    """Keplerian potential on Poincaré disk: V(ρ) = -k/ρ."""
    return -k / max(rho, 1e-6)


def dV_drho(rho: float, k: float = 1.0) -> float:
    """dV/dρ = k/ρ²."""
    return k / max(rho, 1e-6)**2


# ── Orbit integrator (Störmer–Verlet) ────────────────────────────────────────

class OrbitState(NamedTuple):
    phi: float     # azimuthal phase [0, 2π)
    rho: float     # Poincaré radius
    dphi: float    # angular velocity
    drho: float    # radial velocity


def _integrate_orbit(
    rho0: float,
    M_sem: float,
    k: float = 1.0,
    eta: float = 0.02,
    dt: float = 0.01,
    steps: int = 2000,
) -> list[OrbitState]:
    """Integrate orbit under V=-k/ρ with damping η.

    Initial conditions: circular orbit v_circ = sqrt(k / (M_sem * rho0)).
    """
    v_circ = math.sqrt(k / max(M_sem * rho0, 1e-9))
    phi  = 0.0
    rho  = rho0
    dphi = v_circ / max(rho0, 1e-6)   # angular velocity for circular start
    drho = 0.0                          # start radial velocity = 0

    trajectory = [OrbitState(phi, rho, dphi, drho)]

    for _ in range(steps):
        # Radial EOM: m*ρ̈ = m*ρ*φ̇² + F_grav + F_damp_r
        #   F_grav = -dV/dρ / M_sem = -k/(M_sem*ρ²)  (inward, negative)
        #   centrifugal = ρ*φ̇²  (outward, positive)
        # Angular EOM: d/dt(ρ²*φ̇) = torque ≈ -η*ρ²*φ̇  (only damping)
        F_grav   = -(k / max(rho, 1e-6)**2) / M_sem   # inward
        F_centri = rho * dphi**2                        # outward
        a_rho    = F_grav + F_centri - eta * drho

        # Angular: conserve L = ρ²φ̇, damped slowly
        L = rho**2 * dphi
        L_damped = L - eta * L * dt
        dphi_new = L_damped / max(rho, 1e-6)**2

        # Verlet step for radial
        drho_new = drho + a_rho * dt
        rho_new  = max(0.001, rho  + 0.5 * (drho + drho_new) * dt)
        phi_new  = (phi + 0.5 * (dphi + dphi_new) * dt) % (2 * math.pi)

        rho  = rho_new
        phi  = phi_new
        drho = drho_new
        dphi = dphi_new   # already updated above

        trajectory.append(OrbitState(phi, rho, dphi, drho))

    return trajectory


# ── Kepler diagnostics ────────────────────────────────────────────────────────

def kepler_period(trajectory: list[OrbitState]) -> float:
    """Estimate orbital period: time for φ to advance by 2π."""
    phi0 = trajectory[0].phi
    dt_step = 0.01
    for i, s in enumerate(trajectory[1:], 1):
        if s.phi < trajectory[i-1].phi - math.pi:   # wrapped
            elapsed = i * dt_step
            return elapsed
    # fallback: count full cycles by angular displacement
    total_dphi = sum(abs(trajectory[i].phi - trajectory[i-1].phi)
                     for i in range(1, len(trajectory)))
    if total_dphi > 2 * math.pi:
        fraction = (2 * math.pi) / total_dphi
        return len(trajectory) * 0.01 * fraction
    return float('nan')


def areal_velocity(trajectory: list[OrbitState], dt: float = 0.01) -> tuple[float, float]:
    """Compute mean and std of areal velocity dA/dt = 0.5 * ρ² * dφ/dt."""
    areas = [0.5 * s.rho**2 * abs(s.dphi) for s in trajectory]
    return float(np.mean(areas)), float(np.std(areas))


def orbit_closure(trajectory: list[OrbitState]) -> float:
    """Measure orbit closure: distance between start and end point in (ρ,φ) plane.

    Returns value in [0,1] where 1 = perfect closure (ellipse closes).
    """
    start = trajectory[0]
    # find crossing back near φ=0 after first full revolution
    wrapped_idx = None
    for i in range(1, len(trajectory)):
        if trajectory[i-1].phi > math.pi and trajectory[i].phi < math.pi:
            wrapped_idx = i
            break
    if wrapped_idx is None:
        return 0.0
    end = trajectory[wrapped_idx]
    delta_rho = abs(end.rho - start.rho) / max(start.rho, 1e-6)
    return float(max(0.0, 1.0 - delta_rho))


# ── Main simulation ───────────────────────────────────────────────────────────

def run_simulation(
    k: float = 1.0,
    eta: float = 0.02,
    dt: float = 0.01,
    steps: int = 2000,
    include_repos: bool = False,
) -> list[dict]:
    records = build_mass_table(include_repos=include_repos)
    results = []

    for rec in records:
        rho0 = rec.orbit_radius
        if rho0 < 0.01 or rho0 >= 1.0:
            continue

        traj = _integrate_orbit(rho0, rec.M_sem, k=k, eta=eta, dt=dt, steps=steps)
        T_sim   = kepler_period(traj)
        A_mean, A_std = areal_velocity(traj)
        closure = orbit_closure(traj)

        # Kepler III check: T²/a³ = const (should be ~1/M_sem by construction)
        kepler_ratio = (T_sim**2 / rho0**3) if not math.isnan(T_sim) else float('nan')

        results.append({
            'id':           rec.id,
            'M_sem':        rec.M_sem,
            'a':            round(rho0, 4),
            'T_sim':        round(T_sim, 4) if not math.isnan(T_sim) else None,
            'T_kepler':     round(rec.orbit_period, 4),
            'kepler_ratio': round(kepler_ratio, 4) if not math.isnan(kepler_ratio) else None,
            'A_mean':       round(A_mean, 5),
            'A_std':        round(A_std, 5),
            'A_conservation': round(1.0 - A_std / max(A_mean, 1e-9), 4),
            'closure':      round(closure, 4),
        })

    return results


def print_report(results: list[dict]) -> None:
    print(f"\n{'─'*100}")
    print("  CIEL Kepler Emergence Simulation")
    print(f"  {'ID':<40} {'M_sem':>6} {'a':>6} {'T_sim':>7} {'T_kep':>7} {'ratio':>7} {'A_cons':>7} {'closure':>8}")
    print(f"{'─'*100}")

    kepler_ratios = [r['kepler_ratio'] for r in results if r['kepler_ratio'] is not None]

    for r in results:
        kep_flag = ''
        if r['kepler_ratio'] is not None and kepler_ratios:
            mean_ratio = np.mean(kepler_ratios)
            dev = abs(r['kepler_ratio'] - mean_ratio) / max(mean_ratio, 1e-9)
            kep_flag = ' ✓' if dev < 0.15 else ' !'
        T_sim_s  = f"{r['T_sim']:>7.4f}" if r['T_sim'] is not None else f"{'???':>7}"
        kep_s    = f"{r['kepler_ratio']:>7.4f}" if r['kepler_ratio'] is not None else f"{'???':>7}"
        print(f"  {r['id']:<40} {r['M_sem']:>6.4f} {r['a']:>6.4f} {T_sim_s} {r['T_kepler']:>7.4f} {kep_s}{kep_flag} {r['A_conservation']:>7.4f} {r['closure']:>8.4f}")

    print(f"{'─'*100}")

    # Kepler III: variance of T²/a³ should be small relative to 1/M_sem
    if len(kepler_ratios) > 2:
        ratio_std = float(np.std(kepler_ratios))
        ratio_mean = float(np.mean(kepler_ratios))
        print(f"\n  Kepler III consistency:  T²/a³ mean={ratio_mean:.4f}  std={ratio_std:.4f}  CV={ratio_std/max(ratio_mean,1e-9):.3f}")
        print(f"  → {'EMERGENT ✓' if ratio_std/max(ratio_mean,1e-9) < 0.2 else 'NOT emergent ✗'}")

    closures = [r['closure'] for r in results]
    print(f"\n  Orbit closure:  mean={np.mean(closures):.4f}  min={min(closures):.4f}  max={max(closures):.4f}")
    a_cons = [r['A_conservation'] for r in results]
    print(f"  Areal velocity: mean conservation={np.mean(a_cons):.4f}  (1=perfect, Kepler II)")
    print()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='CIEL Kepler Emergence Simulation')
    parser.add_argument('--k',     type=float, default=1.0,  help='Gravitational constant k')
    parser.add_argument('--eta',   type=float, default=0.02, help='Damping coefficient')
    parser.add_argument('--steps', type=int,   default=2000, help='Integration steps')
    parser.add_argument('--repos', action='store_true',      help='Include repository nodes')
    args = parser.parse_args()

    results = run_simulation(k=args.k, eta=args.eta, steps=args.steps, include_repos=args.repos)
    print_report(results)
