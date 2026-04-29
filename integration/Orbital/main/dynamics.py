from __future__ import annotations
import math
from copy import copy as _copy
from .model import OrbitalSystem, ZetaPole, ZetaVertex
from .metrics import (
    A_ij,
    closure_residuals,
    effective_attractor_strength,
    holonomy_defect,
    homology_compatibility,
    local_vorticity,
    orbit_radius_mismatch,
    orbit_stability_score,
    orbital_period_estimate,
    phase_slip_readiness,
    target_orbit_rho,
    theta_from_rho,
    total_relational_potential,
    zeta_tetra_defect,
    bloch_vector,
    poincare_radius,
)

TARGET_THETA = {1: math.pi / 6.0, 2: math.pi / 3.0, 4: 2.0 * math.pi / 3.0}
TARGET_AMP = {1: 0.35, 2: 0.65, 4: 1.00}
TWO_PI = 2.0 * math.pi


def _param(system: OrbitalSystem, key: str, default: float) -> float:
    return float(system.params.get(key, default))


def _wrap_crossings(old_phi: float, new_phi: float) -> int:
    return math.floor(new_phi / TWO_PI) - math.floor(old_phi / TWO_PI)


def _copy_with_perturbed_sector(system: OrbitalSystem, name: str) -> OrbitalSystem:
    tmp = OrbitalSystem(
        sectors=dict(system.sectors),
        couplings=system.couplings,
        params=system.params,
        zeta_pole=system.zeta_pole,
    )
    tmp.sectors[name] = _copy(system.sectors[name])
    return tmp


def tau_gradient(system: OrbitalSystem):
    from .metrics import A_i_zeta, effective_tau_zeta
    names = system.names()
    lhs_map = {}
    rhs_map = {}
    tau_z = effective_tau_zeta(system)
    for i in names:
        lhs = 0j
        for j in names:
            lhs += A_ij(system, i, j) * system.sectors[j].tau
        if system.zeta_pole is not None:
            lhs += A_i_zeta(system, i) * tau_z
        lhs_map[i] = lhs
        rhs_map[i] = complex(
            math.cos(system.sectors[i].phi + system.sectors[i].berry_phase),
            math.sin(system.sectors[i].phi + system.sectors[i].berry_phase),
        )
    grads = {j: 0.0 for j in names}
    for j in names:
        g = 0.0
        for i in names:
            resid = lhs_map[i] - rhs_map[i]
            g += 2.0 * (resid.conjugate() * A_ij(system, i, j)).real
        grads[j] = g
    return grads


def _legacy_step(system: OrbitalSystem, dt: float = 0.025, tau_eta: float = 0.01, tau_reg: float = 0.00) -> OrbitalSystem:
    I0 = _param(system, 'I0', 0.00917)
    nxt = _clone_system(system)
    closure = abs(holonomy_defect(system)) / max(1, len(system.sectors))
    residuals = closure_residuals(system)
    tau_base = {name: s.tau for name, s in system.sectors.items()}
    names = system.names()
    for name in names:
        s = system.sectors[name]
        ns = nxt.sectors[name]
        phase_force = 0.0
        theta_force = 0.0
        amp_force = 0.0
        pair_tension = 0.0
        eff_phi = s.phi + s.berry_phase
        va = bloch_vector(s.theta, eff_phi)
        for other in names:
            if other == name:
                continue
            so = system.sectors[other]
            eff_other = so.phi + so.berry_phase
            vb = bloch_vector(so.theta, eff_other)
            Aab = A_ij(system, name, other)
            amp = abs(Aab)
            phase = math.atan2(Aab.imag, Aab.real) if Aab != 0 else 0.0
            phase_force += amp * math.sin((eff_other - eff_phi) + phase)
            theta_force += amp * (so.theta - s.theta)
            amp_force += amp * (so.amplitude - s.amplitude)
            dot = max(-1.0, min(1.0, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2]))
            pair_tension += amp * (1.0 - dot)
        theta_target = TARGET_THETA[s.q_target]
        amp_target = TARGET_AMP[s.q_target]
        closure_local = residuals[name]
        ns.amplitude = min(1.35, max(0.05, s.amplitude + dt * (0.42 * (amp_target - s.amplitude) + 0.07 * amp_force - 0.18 * s.defect - 0.10 * closure_local)))
        ns.theta = min(math.pi - 1e-3, max(1e-3, s.theta + dt * (0.30 * (theta_target - s.theta) + 0.06 * theta_force - 0.14 * s.defect - 0.05 * closure_local)))
        ns.rho = poincare_radius(ns.theta)
        old_phi = s.phi
        ns.phi = s.phi + dt * (0.36 * s.rhythm_ratio + 0.22 * phase_force + I0 * s.preference - 0.16 * s.defect - 0.12 * closure_local)
        dphi = (ns.phi - old_phi + math.pi) % (2.0 * math.pi) - math.pi
        avg_theta = 0.5 * (s.theta + ns.theta)
        ns.berry_phase = s.berry_phase + 0.5 * (1.0 - math.cos(avg_theta)) * dphi
        ns.defect = max(0.0, s.defect + dt * (-0.42 * s.defect + 0.05 * pair_tension + 0.08 * closure + 0.18 * closure_local))
        ns.spin = math.tanh(phase_force)
    grads = tau_gradient(system)
    for name in names:
        s = system.sectors[name]
        ns = nxt.sectors[name]
        ns.tau = min(0.8, max(0.12, s.tau - tau_eta * grads[name] - tau_reg * dt * (s.tau - tau_base[name])))
    if nxt.zeta_pole is not None:
        theta_star = math.acos(-1.0 / 3.0)
        phase0 = _param(nxt, 'zeta_phase0', 0.0)
        target_phis = [phase0, phase0, phase0 + 2.0 * math.pi / 3.0, phase0 + 4.0 * math.pi / 3.0]
        target_thetas = [0.0, theta_star, theta_star, theta_star]
        relax = _param(nxt, 'zeta_relax', 0.08)
        global_rot = _param(nxt, 'zeta_global_rotation', 0.0)
        for idx, vertex in enumerate(nxt.zeta_pole.vertices):
            vertex.theta += dt * relax * (target_thetas[idx] - vertex.theta)
            dphi = (target_phis[idx] - vertex.phi + math.pi) % (2.0 * math.pi) - math.pi
            vertex.phi += dt * (global_rot + relax * dphi)
    nxt.params = dict(system.params)
    return nxt


def _perturbed_potential(system: OrbitalSystem, name: str, *, dphi: float = 0.0, drho: float = 0.0) -> float:
    tmp = _copy_with_perturbed_sector(system, name)
    s = tmp.sectors[name]
    s.phi += dphi
    s.rho = min(0.96, max(0.02, s.rho + drho))
    s.theta = theta_from_rho(s.rho)
    return total_relational_potential(tmp)


def _clone_system(system: OrbitalSystem) -> OrbitalSystem:
    """Shallow-clone OrbitalSystem — sectors and zeta vertices copied, params/couplings shared.

    Equivalent to deepcopy for this structure (all fields are primitives) but
    avoids traversing the large params dict on every step.
    120× per global_pass → significant GC pressure reduction.
    """
    zp = None
    if system.zeta_pole is not None:
        zp = ZetaPole(
            vertices=[_copy(v) for v in system.zeta_pole.vertices],
            kappa_tetra=system.zeta_pole.kappa_tetra,
            spin=system.zeta_pole.spin,
            rho=system.zeta_pole.rho,
        )
    return OrbitalSystem(
        sectors={name: _copy(sec) for name, sec in system.sectors.items()},
        couplings=system.couplings,  # read-only in dynamics — safe to share
        params=system.params,        # read-only in dynamics — safe to share
        zeta_pole=zp,
    )


def _relational_step(system: OrbitalSystem, dt: float = 0.025, tau_eta: float = 0.01, tau_reg: float = 0.00) -> OrbitalSystem:
    nxt = _clone_system(system)
    names = system.names()
    tau_base = {name: s.tau for name, s in system.sectors.items()}
    alpha_s = _param(system, 'alpha_spin', 4.0)
    mu_phi = _param(system, 'mu_phi', 0.18)
    mu_rho = _param(system, 'mu_rho', 0.14)
    eps_h = _param(system, 'epsilon_hom', 0.22)
    vort_gain = _param(system, 'spin_vorticity_gain', 0.20)
    relax_amp = _param(system, 'relax_amp', 0.28)
    closure_res = closure_residuals(system)
    vorts = local_vorticity(system)
    zeta_defect = zeta_tetra_defect(system)
    h = _param(system, 'grad_eps', 1e-3)
    use_euler = bool(system.params.get('use_euler_leak_rotation', True))
    d_f = _param(system, 'D_f', 2.57)
    theta_euler = 0.5 * math.pi * (d_f - 2.0)
    cos_e = math.cos(theta_euler)
    sin_e = math.sin(theta_euler)
    ang_gain = _param(system, 'euler_angular_gain', 1.0)
    I0 = _param(system, 'I0', 0.00917)  # pre-extract — used in inner loop

    for name in names:
        s = system.sectors[name]
        ns = nxt.sectors[name]
        dV_dphi = (_perturbed_potential(system, name, dphi=h) - _perturbed_potential(system, name, dphi=-h)) / (2 * h)
        dV_drho = (_perturbed_potential(system, name, drho=h) - _perturbed_potential(system, name, drho=-h)) / (2 * h)
        spin = math.tanh(-alpha_s * dV_dphi)
        compat = homology_compatibility(system, name)

        leak_grad = compat * (-dV_drho)
        if use_euler:
            leak_rad = eps_h * cos_e * leak_grad
            leak_ang = eps_h * sin_e * leak_grad
        else:
            leak_rad = eps_h * leak_grad
            leak_ang = 0.0

        ns.spin = spin
        ns.rho = min(0.96, max(0.02, s.rho + dt * (-mu_rho * dV_drho + leak_rad - 0.03 * s.defect)))
        ns.theta = theta_from_rho(ns.rho)
        old_phi = s.phi
        ns.phi = s.phi + dt * (
            -mu_phi * dV_dphi
            + vort_gain * spin * vorts[name]
            + ang_gain * leak_ang
            + I0 * s.preference
        )
        dphi = (ns.phi - old_phi + math.pi) % (2.0 * math.pi) - math.pi
        avg_theta = 0.5 * (s.theta + ns.theta)
        ns.berry_phase = s.berry_phase + 0.5 * (1.0 - math.cos(avg_theta)) * dphi
        amp_target = TARGET_AMP[s.q_target]
        ns.amplitude = min(1.35, max(0.05, s.amplitude + dt * (
            relax_amp * (amp_target - s.amplitude)
            - 0.10 * closure_res[name]
            - 0.08 * s.defect
            + 0.04 * abs(leak_rad)
            + 0.02 * abs(leak_ang)
        )))
        ns.defect = max(0.0, s.defect + dt * (
            -0.28 * s.defect
            + 0.18 * closure_res[name]
            + 0.03 * abs(dV_dphi)
            + 0.03 * abs(dV_drho)
            + 0.20 * zeta_defect
        ))

    grads = tau_gradient(system)
    for name in names:
        s = system.sectors[name]
        ns = nxt.sectors[name]
        ns.tau = min(0.8, max(0.12, s.tau - tau_eta * grads[name] - tau_reg * dt * (s.tau - tau_base[name])))

    if nxt.zeta_pole is not None:
        theta_star = math.acos(-1.0 / 3.0)
        phase0 = _param(nxt, 'zeta_phase0', 0.0)
        target_phis = [phase0, phase0, phase0 + 2.0 * math.pi / 3.0, phase0 + 4.0 * math.pi / 3.0]
        target_thetas = [0.0, theta_star, theta_star, theta_star]
        mean_spin = sum(nxt.sectors[n].spin for n in names) / max(1, len(names))
        nxt.zeta_pole.spin = mean_spin
        nxt.zeta_pole.rho = min(0.96, max(0.02, nxt.zeta_pole.rho + dt * 0.05 * mean_spin))
        relax = _param(nxt, 'zeta_relax', 0.08)
        for idx, vertex in enumerate(nxt.zeta_pole.vertices):
            vertex.theta += dt * relax * (target_thetas[idx] - vertex.theta)
            dphi = (target_phis[idx] - vertex.phi + math.pi) % (2.0 * math.pi) - math.pi
            vertex.phi += dt * (0.08 * mean_spin + relax * dphi)

    nxt.params = dict(system.params)
    return nxt


def _apply_orbital_law_v0(base_system: OrbitalSystem, nxt: OrbitalSystem, dt: float) -> OrbitalSystem:
    state_view = _clone_system(nxt)
    residuals = closure_residuals(state_view)
    vorticities = local_vorticity(state_view)
    rho_gain = _param(state_view, 'orbital_rho_gain', 0.18)
    phi_gain = _param(state_view, 'orbital_phi_gain', 0.08)
    amp_gain = _param(state_view, 'orbital_amp_gain', 0.12)
    phase_slip_amp_penalty = _param(state_view, 'phase_slip_amp_penalty', 0.08)

    for name in state_view.names():
        prev = base_system.sectors[name]
        ns = nxt.sectors[name]
        mu_eff = effective_attractor_strength(state_view, name, residuals=residuals)
        tau_orbit = orbital_period_estimate(state_view, name, mu_eff=mu_eff)
        stability = orbit_stability_score(
            state_view,
            name,
            mu_eff=mu_eff,
            tau_orbit=tau_orbit,
            residuals=residuals,
            vorticities=vorticities,
        )
        mismatch = abs(orbit_radius_mismatch(state_view, name))
        phase_slip = phase_slip_readiness(state_view, name, stability=stability, mismatch=mismatch)

        target_rho = target_orbit_rho(ns.q_target)
        coupling = min(2.0, mu_eff / max(tau_orbit, 1e-6))
        ns.rho = min(0.96, max(0.02, ns.rho + dt * rho_gain * (target_rho - ns.rho) * coupling))
        ns.theta = theta_from_rho(ns.rho)

        orbital_sign = 1.0
        if abs(ns.spin) > 1e-9:
            orbital_sign = math.copysign(1.0, ns.spin)
        elif abs(ns.rhythm_ratio) > 1e-9:
            orbital_sign = math.copysign(1.0, ns.rhythm_ratio)

        old_phi = ns.phi
        ns.phi = ns.phi + dt * phi_gain * orbital_sign / max(tau_orbit, 1e-6)
        dphi = (ns.phi - old_phi + math.pi) % (2.0 * math.pi) - math.pi
        ns.berry_phase = ns.berry_phase + 0.5 * (1.0 - math.cos(ns.theta)) * dphi
        ns.winding = prev.winding + _wrap_crossings(prev.phi, ns.phi)

        amp_delta = dt * amp_gain * (stability - 0.5)
        if phase_slip:
            amp_delta -= dt * phase_slip_amp_penalty
        ns.amplitude = min(1.35, max(0.05, ns.amplitude + amp_delta))

        ns.mu_eff = mu_eff
        ns.tau_orbit = tau_orbit
        ns.orbit_stability = stability
        ns.phase_slip_ready = phase_slip

    nxt.params = dict(base_system.params)
    return nxt


def step(system: OrbitalSystem, dt: float = 0.025, tau_eta: float = 0.01, tau_reg: float = 0.00) -> OrbitalSystem:
    if bool(system.params.get('use_relational_lagrangian', True)):
        nxt = _relational_step(system, dt=dt, tau_eta=tau_eta, tau_reg=tau_reg)
    else:
        nxt = _legacy_step(system, dt=dt, tau_eta=tau_eta, tau_reg=tau_reg)
    if bool(system.params.get('use_orbital_law_v0', False)):
        nxt = _apply_orbital_law_v0(system, nxt, dt)
    return nxt
