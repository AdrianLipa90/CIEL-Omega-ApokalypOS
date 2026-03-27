from __future__ import annotations

import math
from copy import deepcopy

from .metrics import (
    A_ij,
    closure_residuals,
    effective_phase_zeta,
    effective_tau_zeta,
    holonomy_defect,
    poincare_radius,
    theta_from_rho,
    zeta_tetra_defect,
)
from .model import OrbitalSystem

TARGET_THETA = {1: math.pi / 6.0, 2: math.pi / 3.0, 4: 2.0 * math.pi / 3.0}
TARGET_AMP = {1: 0.35, 2: 0.65, 4: 1.00}


def _param(system: OrbitalSystem, key: str, default: float) -> float:
    return float(system.params.get(key, default))


def tau_gradient(system: OrbitalSystem) -> dict[str, float]:
    names = system.names()
    tau_z = effective_tau_zeta(system)
    grads: dict[str, float] = {name: 0.0 for name in names}
    for i in names:
        lhs = 0.0j
        for j in names:
            lhs += A_ij(system, i, j) * system.sectors[j].tau
        if system.zeta_pole is not None:
            lhs += complex(tau_z, 0.0)
        rhs = complex(
            math.cos(system.sectors[i].phi + system.sectors[i].berry_phase),
            math.sin(system.sectors[i].phi + system.sectors[i].berry_phase),
        )
        resid = lhs - rhs
        for j in names:
            grads[j] += 2.0 * (resid.conjugate() * A_ij(system, i, j)).real
    return grads


def step(system: OrbitalSystem, dt: float = 0.025, tau_eta: float = 0.01, tau_reg: float = 0.0) -> OrbitalSystem:
    i0 = _param(system, 'I0', 0.00917)
    nxt = deepcopy(system)
    names = system.names()
    closure = abs(holonomy_defect(system)) / max(1, len(names))
    residuals = closure_residuals(system)
    tau_base = {name: s.tau for name, s in system.sectors.items()}

    for name in names:
        s = system.sectors[name]
        ns = nxt.sectors[name]
        phase_force = 0.0
        theta_force = 0.0
        amp_force = 0.0
        pair_tension = 0.0
        eff_phi = s.phi + s.berry_phase

        for other in names:
            if other == name:
                continue
            so = system.sectors[other]
            eff_other = so.phi + so.berry_phase
            aab = A_ij(system, name, other)
            amp = abs(aab)
            phase = math.atan2(aab.imag, aab.real) if aab != 0 else 0.0
            phase_force += amp * math.sin((eff_other - eff_phi) + phase)
            theta_force += amp * (so.theta - s.theta)
            amp_force += amp * (so.amplitude - s.amplitude)
            pair_tension += amp * abs(eff_other - eff_phi)

        theta_target = TARGET_THETA.get(s.q_target, s.theta)
        amp_target = TARGET_AMP.get(s.q_target, s.amplitude)
        closure_local = residuals.get(name, 0.0)

        ns.amplitude = min(
            1.35,
            max(
                0.05,
                s.amplitude
                + dt * (0.42 * (amp_target - s.amplitude) + 0.07 * amp_force - 0.18 * s.defect - 0.10 * closure_local),
            ),
        )
        ns.theta = min(
            math.pi - 1e-3,
            max(
                1e-3,
                s.theta + dt * (0.30 * (theta_target - s.theta) + 0.06 * theta_force - 0.14 * s.defect - 0.05 * closure_local),
            ),
        )
        ns.rho = poincare_radius(ns.theta)
        old_phi = s.phi
        ns.phi = s.phi + dt * (0.36 * s.rhythm_ratio + 0.22 * phase_force + i0 * s.preference - 0.16 * s.defect - 0.12 * closure_local)
        dphi = (ns.phi - old_phi + math.pi) % (2.0 * math.pi) - math.pi
        avg_theta = 0.5 * (s.theta + ns.theta)
        ns.berry_phase = s.berry_phase + 0.5 * (1.0 - math.cos(avg_theta)) * dphi
        ns.defect = max(0.0, s.defect + dt * (-0.42 * s.defect + 0.03 * pair_tension + 0.08 * closure + 0.18 * closure_local))
        ns.spin = math.tanh(phase_force)

    grads = tau_gradient(system)
    for name in names:
        s = system.sectors[name]
        ns = nxt.sectors[name]
        ns.tau = min(0.8, max(0.12, s.tau - tau_eta * grads[name] - tau_reg * dt * (s.tau - tau_base[name])))
        ns.rho = max(0.0, min(0.999999, ns.rho))
        ns.theta = theta_from_rho(ns.rho)

    if nxt.zeta_pole is not None:
        nxt.zeta_pole.spin = math.tanh(sum(s.spin for s in nxt.sectors.values()) / max(1, len(nxt.sectors)))
        nxt.zeta_pole.rho = max(0.0, min(0.999999, 0.45 + 0.05 * nxt.zeta_pole.spin - 0.02 * zeta_tetra_defect(nxt)))
        phase_shift = effective_phase_zeta(nxt)
        for vertex in nxt.zeta_pole.vertices:
            vertex.phi = vertex.phi + dt * 0.05 * phase_shift

    return nxt
