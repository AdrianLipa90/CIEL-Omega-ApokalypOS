from __future__ import annotations
import cmath
import math
from typing import Dict, Tuple
import numpy as np
from .model import OrbitalSystem, ZetaVertex

ORBITAL_TARGET_THETA = {
    1: math.pi / 6.0,
    2: math.pi / 3.0,
    4: 2.0 * math.pi / 3.0,
}


def _param(system: OrbitalSystem, key: str, default: float) -> float:
    return float(system.params.get(key, default))


def bloch_vector(theta: float, phi: float):
    return (math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta))


def poincare_radius(theta: float) -> float:
    return math.tanh(math.tan(theta / 2.0))


def theta_from_rho(rho: float) -> float:
    rho = min(0.999999, max(1e-6, rho))
    return 2.0 * math.atan(math.atanh(rho))


def target_orbit_theta(q_target: int) -> float:
    return ORBITAL_TARGET_THETA.get(q_target, ORBITAL_TARGET_THETA[2])


def target_orbit_rho(q_target: int) -> float:
    return poincare_radius(target_orbit_theta(q_target))


def poincare_distance(theta_a: float, phi_a: float, theta_b: float, phi_b: float) -> float:
    ra = min(0.999999, abs(poincare_radius(theta_a)))
    rb = min(0.999999, abs(poincare_radius(theta_b)))
    dphi = phi_b - phi_a
    num = ra**2 + rb**2 - 2.0 * ra * rb * math.cos(dphi)
    den = max(1e-12, (1.0 - ra**2) * (1.0 - rb**2))
    arg = 1.0 + 2.0 * num / den
    arg = max(1.0, arg)
    return math.acosh(arg)


def berry_pair_phase(theta_a: float, phi_a: float, theta_b: float, phi_b: float) -> float:
    dphi = (phi_b - phi_a + math.pi) % (2 * math.pi) - math.pi
    avg_theta = 0.5 * (theta_a + theta_b)
    return 0.5 * (1.0 - math.cos(avg_theta)) * dphi


def _complex_coupling(base: float, tau_a: float, tau_b: float, theta_a: float, phi_a: float, theta_b: float, phi_b: float, sigma: float, beta: float, gamma: float) -> complex:
    if base <= 0.0:
        return 0.0 + 0.0j
    tau_factor = math.exp(-0.5 * (math.log(max(1e-9, tau_a / tau_b)) / sigma) ** 2)
    d_ij = poincare_distance(theta_a, phi_a, theta_b, phi_b)
    omega_ij = berry_pair_phase(theta_a, phi_a, theta_b, phi_b)
    phase = beta * omega_ij - gamma * d_ij
    return (base * tau_factor) * cmath.exp(1j * phase)


def A_ij(system: OrbitalSystem, a: str, b: str) -> complex:
    sigma = _param(system, 'sigma', 0.28)
    beta = _param(system, 'beta', 0.9)
    gamma = _param(system, 'gamma', 0.25)
    mesh_boost = _param(system, 'mesh_boost', 1.0)
    sa = system.sectors[a]
    sb = system.sectors[b]
    if a == b:
        return 0.0 + 0.0j
    base = system.coupling(a, b) * mesh_boost
    phi_a = sa.phi + sa.berry_phase
    phi_b = sb.phi + sb.berry_phase
    return _complex_coupling(base, sa.tau, sb.tau, sa.theta, phi_a, sb.theta, phi_b, sigma, beta, gamma)


def A_i_zeta_vertex_raw(system: OrbitalSystem, a: str, vertex: ZetaVertex) -> complex:
    sigma = _param(system, 'sigma', 0.28)
    beta = _param(system, 'beta', 0.9)
    gamma = _param(system, 'gamma', 0.25)
    zeta_scale = _param(system, 'zeta_coupling_scale', 0.35)
    sa = system.sectors[a]
    phi_a = sa.phi + sa.berry_phase
    base = zeta_scale * sa.coherence_weight * vertex.weight
    return _complex_coupling(base, sa.tau, vertex.tau, sa.theta, phi_a, vertex.theta, vertex.phi, sigma, beta, gamma)


def heisenberg_soft_clip(z: complex, alpha: float) -> complex:
    if z == 0:
        return 0.0 + 0.0j
    return z / math.sqrt(1.0 + alpha * (abs(z) ** 2))


def A_i_zeta_vertex(system: OrbitalSystem, a: str, vertex: ZetaVertex) -> complex:
    raw = A_i_zeta_vertex_raw(system, a, vertex)
    alpha = _param(system, 'zeta_heisenberg_alpha', 8.0)
    i0_scale = _param(system, 'zeta_i0_scale', 1.0) * _param(system, 'I0', 0.00917)
    return i0_scale * heisenberg_soft_clip(raw, alpha)


def A_i_zeta(system: OrbitalSystem, a: str) -> complex:
    if system.zeta_pole is None:
        return 0.0 + 0.0j
    total = 0.0 + 0.0j
    for vertex in system.zeta_pole.vertices:
        total += A_i_zeta_vertex(system, a, vertex)
    return total


def A_matrix(system: OrbitalSystem) -> Dict[str, Dict[str, Tuple[float, float]]]:
    out: Dict[str, Dict[str, Tuple[float, float]]] = {}
    for a in system.names():
        out[a] = {}
        for b in system.names():
            z = A_ij(system, a, b)
            out[a][b] = (abs(z), cmath.phase(z) if z != 0 else 0.0)
    return out


def A_numpy(system: OrbitalSystem) -> np.ndarray:
    names = system.names()
    n = len(names)
    A = np.zeros((n, n), dtype=np.complex128)
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            A[i, j] = A_ij(system, a, b)
    return A


def spectral_observables(system: OrbitalSystem) -> dict:
    A = A_numpy(system)
    eigA = np.linalg.eigvals(A)
    W = np.abs(A)
    Wsym = 0.5 * (W + W.T)
    deg = np.sum(Wsym, axis=1)
    L = np.diag(deg) - Wsym
    eigL = np.linalg.eigvalsh(L)
    eigA_sorted = sorted(eigA, key=lambda z: abs(z), reverse=True)
    eigL_sorted = sorted(float(x.real) for x in eigL)
    spectral_radius = float(abs(eigA_sorted[0])) if len(eigA_sorted) else 0.0
    spectral_gap_A = float(abs(eigA_sorted[0]) - abs(eigA_sorted[1])) if len(eigA_sorted) > 1 else spectral_radius
    fiedler = float(eigL_sorted[1]) if len(eigL_sorted) > 1 else 0.0
    return {
        'spectral_radius_A': spectral_radius,
        'spectral_gap_A': spectral_gap_A,
        'fiedler_L': fiedler,
        'eig_A': [{'real': float(z.real), 'imag': float(z.imag), 'abs': float(abs(z))} for z in eigA_sorted],
        'eig_L': eigL_sorted,
    }


def zeta_tetra_defect(system: OrbitalSystem) -> float:
    if system.zeta_pole is None:
        return 0.0
    vecs = [bloch_vector(v.theta, v.phi) for v in system.zeta_pole.vertices]
    total = 0.0
    for i in range(len(vecs)):
        for j in range(i + 1, len(vecs)):
            dot = sum(a * b for a, b in zip(vecs[i], vecs[j]))
            total += (dot + 1.0 / 3.0) ** 2
    return system.zeta_pole.kappa_tetra * total


def effective_tau_zeta(system: OrbitalSystem) -> float:
    if system.zeta_pole is None:
        return 0.0
    return sum(v.weight * v.tau for v in system.zeta_pole.vertices)


def effective_phase_zeta(system: OrbitalSystem) -> float:
    if system.zeta_pole is None:
        return 0.0
    z = sum(v.weight * cmath.exp(1j * v.phi) for v in system.zeta_pole.vertices)
    return cmath.phase(z) if abs(z) > 1e-12 else 0.0


def zeta_coupling_norm(system: OrbitalSystem) -> float:
    if system.zeta_pole is None:
        return 0.0
    return sum(abs(A_i_zeta(system, name)) for name in system.names())


def zeta_coupling_norm_raw(system: OrbitalSystem) -> float:
    if system.zeta_pole is None:
        return 0.0
    total = 0.0
    for name in system.names():
        total += abs(sum(A_i_zeta_vertex_raw(system, name, v) for v in system.zeta_pole.vertices))
    return total


def homology_compatibility(system: OrbitalSystem, a: str) -> float:
    if system.zeta_pole is None:
        return 0.0
    raw = abs(sum(A_i_zeta_vertex_raw(system, a, v) for v in system.zeta_pole.vertices))
    eff = abs(A_i_zeta(system, a))
    return eff / (1.0 + raw)


def closure_residuals(system: OrbitalSystem) -> Dict[str, float]:
    out = {}
    tau_z = effective_tau_zeta(system)
    for a in system.names():
        sa = system.sectors[a]
        lhs = 0j
        for b in system.names():
            lhs += A_ij(system, a, b) * system.sectors[b].tau
        if system.zeta_pole is not None:
            lhs += A_i_zeta(system, a) * tau_z
        rhs = cmath.exp(1j * (sa.phi + sa.berry_phase))
        out[a] = abs(lhs - rhs)
    return out


def closure_penalty(system: OrbitalSystem) -> float:
    res = closure_residuals(system)
    penalty = sum(v * v for v in res.values())
    if system.zeta_pole is not None:
        penalty += _param(system, 'zeta_tetra_weight', 0.5) * zeta_tetra_defect(system)
    return penalty


def local_vorticity(system: OrbitalSystem) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for a in system.names():
        sa = system.sectors[a]
        eff_a = sa.phi + sa.berry_phase
        ra = max(1e-6, sa.rho)
        vort = 0.0
        for b in system.names():
            if a == b:
                continue
            sb = system.sectors[b]
            eff_b = sb.phi + sb.berry_phase
            rb = max(1e-6, sb.rho)
            Aab = A_ij(system, a, b)
            vort += abs(Aab) * ra * rb * math.sin((eff_b - eff_a) + cmath.phase(Aab))
        if system.zeta_pole is not None:
            for vertex in system.zeta_pole.vertices:
                rv = max(1e-6, poincare_radius(vertex.theta))
                Aaz = A_i_zeta_vertex(system, a, vertex)
                vort += abs(Aaz) * ra * rv * math.sin((vertex.phi - eff_a) + cmath.phase(Aaz))
        out[a] = vort
    return out


def orbit_radius_mismatch(system: OrbitalSystem, a: str) -> float:
    sa = system.sectors[a]
    return sa.rho - target_orbit_rho(sa.q_target)


def effective_attractor_strength(system: OrbitalSystem, a: str, residuals: Dict[str, float] | None = None) -> float:
    residuals = residuals or closure_residuals(system)
    sa = system.sectors[a]
    coupling_sum = 0.0
    for b in system.names():
        if a == b:
            continue
        coupling_sum += abs(A_ij(system, a, b))
    mismatch = abs(orbit_radius_mismatch(system, a))
    coherence = max(1e-6, sa.coherence_weight * sa.amplitude)
    base = sa.info_mass * coherence * (1.0 + coupling_sum)
    penalty = 1.0 + sa.defect + residuals[a] + mismatch
    return max(1e-6, base / penalty)


def orbital_period_estimate(system: OrbitalSystem, a: str, mu_eff: float | None = None) -> float:
    sa = system.sectors[a]
    mu_eff = mu_eff if mu_eff is not None else effective_attractor_strength(system, a)
    return math.sqrt((max(1e-6, sa.rho) ** 3) / max(1e-6, mu_eff))


def orbit_stability_score(
    system: OrbitalSystem,
    a: str,
    mu_eff: float | None = None,
    tau_orbit: float | None = None,
    residuals: Dict[str, float] | None = None,
    vorticities: Dict[str, float] | None = None,
) -> float:
    residuals = residuals or closure_residuals(system)
    vorticities = vorticities or local_vorticity(system)
    mu_eff = mu_eff if mu_eff is not None else effective_attractor_strength(system, a, residuals=residuals)
    tau_orbit = tau_orbit if tau_orbit is not None else orbital_period_estimate(system, a, mu_eff=mu_eff)
    mismatch = abs(orbit_radius_mismatch(system, a))
    closure = residuals[a]
    vort = abs(vorticities[a])
    denom = 1.0 + 1.2 * mismatch + 0.6 * closure + 0.15 * vort + 0.05 * tau_orbit
    return 1.0 / denom


def phase_slip_readiness(
    system: OrbitalSystem,
    a: str,
    stability: float | None = None,
    mismatch: float | None = None,
) -> bool:
    threshold = _param(system, 'phase_slip_stability_threshold', 0.52)
    mismatch_threshold = _param(system, 'phase_slip_radius_threshold', 0.08)
    stability = stability if stability is not None else orbit_stability_score(system, a)
    mismatch = mismatch if mismatch is not None else abs(orbit_radius_mismatch(system, a))
    return stability < threshold and abs(mismatch) > mismatch_threshold


def orbital_law_state(system: OrbitalSystem) -> Dict[str, dict]:
    residuals = closure_residuals(system)
    vorticities = local_vorticity(system)
    out: Dict[str, dict] = {}
    for a in system.names():
        mu_eff = effective_attractor_strength(system, a, residuals=residuals)
        tau_orbit = orbital_period_estimate(system, a, mu_eff=mu_eff)
        stability = orbit_stability_score(
            system,
            a,
            mu_eff=mu_eff,
            tau_orbit=tau_orbit,
            residuals=residuals,
            vorticities=vorticities,
        )
        mismatch = orbit_radius_mismatch(system, a)
        out[a] = {
            'target_rho': target_orbit_rho(system.sectors[a].q_target),
            'delta_r': mismatch,
            'mu_eff': mu_eff,
            'tau_orbit': tau_orbit,
            'orbit_stability': stability,
            'phase_slip_ready': phase_slip_readiness(system, a, stability=stability, mismatch=abs(mismatch)),
            'winding': system.sectors[a].winding,
        }
    return out


def global_chirality(system: OrbitalSystem) -> float:
    vort = local_vorticity(system)
    total = 0.0
    for name, sector in system.sectors.items():
        A_k = sector.coherence_weight * sector.amplitude
        total += A_k * sector.spin * vort[name]
    return total


def effective_mass(system: OrbitalSystem, tension_weight: float | None = None, closure_weight: float | None = None) -> Dict[str, float]:
    if tension_weight is None:
        tension_weight = _param(system, 'tension_weight', 0.25)
    if closure_weight is None:
        closure_weight = _param(system, 'closure_weight', 0.10)
    names = system.names()
    residuals = closure_residuals(system)
    masses: Dict[str, float] = {}
    for a in names:
        sa = system.sectors[a]
        local_tension = 0.0
        for b in names:
            if a == b:
                continue
            sb = system.sectors[b]
            va = bloch_vector(sa.theta, sa.phi + sa.berry_phase)
            vb = bloch_vector(sb.theta, sb.phi + sb.berry_phase)
            dot = max(-1.0, min(1.0, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2]))
            local_tension += abs(A_ij(system, a, b)) * (1.0 - dot)
        if system.zeta_pole is not None:
            va = bloch_vector(sa.theta, sa.phi + sa.berry_phase)
            for vertex in system.zeta_pole.vertices:
                vb = bloch_vector(vertex.theta, vertex.phi)
                dot = max(-1.0, min(1.0, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2]))
                local_tension += abs(A_i_zeta_vertex(system, a, vertex)) * (1.0 - dot)
        masses[a] = sa.info_mass * (1.0 + tension_weight * local_tension + closure_weight * residuals[a]) / sa.rhythm_ratio
    return masses


def holonomy_defect(system: OrbitalSystem) -> complex:
    z = 0j
    for sector in system.sectors.values():
        eff_phi = sector.phi + sector.berry_phase
        A_k = sector.coherence_weight * sector.amplitude
        z += A_k * cmath.exp(1j * eff_phi)
    if system.zeta_pole is not None:
        zeta_amp = _param(system, 'zeta_amplitude', 0.35)
        zeta_alpha = _param(system, 'zeta_heisenberg_alpha', 8.0)
        zeta_i0_scale = _param(system, 'zeta_i0_scale', 1.0) * _param(system, 'I0', 0.00917)
        zeta_eff = zeta_i0_scale * zeta_amp / math.sqrt(1.0 + zeta_alpha * (zeta_amp ** 2))
        z += zeta_eff * cmath.exp(1j * effective_phase_zeta(system))
    return z


def global_coherence(system: OrbitalSystem) -> float:
    return abs(holonomy_defect(system)) ** 2


def chord_tension(system: OrbitalSystem) -> float:
    names = system.names()
    total = 0.0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            sa = system.sectors[a]
            sb = system.sectors[b]
            va = bloch_vector(sa.theta, sa.phi + sa.berry_phase)
            vb = bloch_vector(sb.theta, sb.phi + sb.berry_phase)
            dot = max(-1.0, min(1.0, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2]))
            total += abs(A_ij(system, a, b)) * (1.0 - dot)
        if system.zeta_pole is not None:
            sa = system.sectors[a]
            va = bloch_vector(sa.theta, sa.phi + sa.berry_phase)
            for vertex in system.zeta_pole.vertices:
                vb = bloch_vector(vertex.theta, vertex.phi)
                dot = max(-1.0, min(1.0, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2]))
                total += abs(A_i_zeta_vertex(system, a, vertex)) * (1.0 - dot)
    if system.zeta_pole is not None:
        total += _param(system, 'zeta_tetra_weight', 0.5) * zeta_tetra_defect(system)
    return total


def closure_details(system: OrbitalSystem):
    out = {}
    tau_z = effective_tau_zeta(system)
    for a in system.names():
        sa = system.sectors[a]
        lhs = 0j
        for b in system.names():
            lhs += A_ij(system, a, b) * system.sectors[b].tau
        if system.zeta_pole is not None:
            lhs += A_i_zeta(system, a) * tau_z
        rhs_phase = sa.phi + sa.berry_phase
        rhs = cmath.exp(1j * rhs_phase)
        phase_err = (cmath.phase(lhs) - rhs_phase + math.pi) % (2.0 * math.pi) - math.pi
        mag_err = abs(lhs) - 1.0
        out[a] = {
            'lhs_abs': abs(lhs),
            'lhs_phase': cmath.phase(lhs),
            'rhs_phase': rhs_phase,
            'phase_error': phase_err,
            'magnitude_error': mag_err,
            'residual': abs(lhs - rhs),
        }
    return out


def radial_spread(system: OrbitalSystem) -> float:
    vals = [s.rho for s in system.sectors.values()]
    mean = sum(vals) / len(vals)
    return math.sqrt(sum((x - mean) ** 2 for x in vals) / len(vals))


def total_relational_potential(system: OrbitalSystem) -> float:
    kappa_h = _param(system, 'kappa_H', 1.0)
    lambda_t = _param(system, 'lambda_tension', 0.15)
    lambda_d = _param(system, 'lambda_distortion', 1.0)
    lambda_z = _param(system, 'lambda_zeta_tetra', 1.0)
    return kappa_h * global_coherence(system) + lambda_t * chord_tension(system) + lambda_d * closure_penalty(system) + lambda_z * zeta_tetra_defect(system)
