from __future__ import annotations

import cmath
import math
from typing import Dict

import numpy as np

from .model import OrbitalSystem, ZetaVertex


def _param(system: OrbitalSystem, key: str, default: float) -> float:
    return float(system.params.get(key, default))


def bloch_vector(theta: float, phi: float) -> tuple[float, float, float]:
    return (
        math.sin(theta) * math.cos(phi),
        math.sin(theta) * math.sin(phi),
        math.cos(theta),
    )


def poincare_radius(theta: float) -> float:
    return math.tanh(math.tan(theta / 2.0))


def theta_from_rho(rho: float) -> float:
    rho = min(0.999999, max(1e-6, rho))
    return 2.0 * math.atan(math.atanh(rho))


def berry_pair_phase(theta_a: float, phi_a: float, theta_b: float, phi_b: float) -> float:
    dphi = (phi_b - phi_a + math.pi) % (2.0 * math.pi) - math.pi
    avg_theta = 0.5 * (theta_a + theta_b)
    return 0.5 * (1.0 - math.cos(avg_theta)) * dphi


def poincare_distance(theta_a: float, phi_a: float, theta_b: float, phi_b: float) -> float:
    ra = min(0.999999, abs(poincare_radius(theta_a)))
    rb = min(0.999999, abs(poincare_radius(theta_b)))
    dphi = phi_b - phi_a
    num = ra**2 + rb**2 - 2.0 * ra * rb * math.cos(dphi)
    den = max(1e-12, (1.0 - ra**2) * (1.0 - rb**2))
    arg = max(1.0, 1.0 + 2.0 * num / den)
    return math.acosh(arg)


def _complex_coupling(
    base: float,
    tau_a: float,
    tau_b: float,
    theta_a: float,
    phi_a: float,
    theta_b: float,
    phi_b: float,
    sigma: float,
    beta: float,
    gamma: float,
) -> complex:
    if base <= 0.0:
        return 0.0j
    tau_factor = math.exp(-0.5 * (math.log(max(1e-9, tau_a / tau_b)) / sigma) ** 2)
    d_ij = poincare_distance(theta_a, phi_a, theta_b, phi_b)
    omega_ij = berry_pair_phase(theta_a, phi_a, theta_b, phi_b)
    phase = beta * omega_ij - gamma * d_ij
    return (base * tau_factor) * cmath.exp(1j * phase)


def A_ij(system: OrbitalSystem, a: str, b: str) -> complex:
    if a == b:
        return 0.0j
    sigma = _param(system, 'sigma', 0.28)
    beta = _param(system, 'beta', 0.9)
    gamma = _param(system, 'gamma', 0.25)
    mesh_boost = _param(system, 'mesh_boost', 1.0)
    sa = system.sectors[a]
    sb = system.sectors[b]
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
        return 0.0j
    return z / math.sqrt(1.0 + alpha * (abs(z) ** 2))


def A_i_zeta_vertex(system: OrbitalSystem, a: str, vertex: ZetaVertex) -> complex:
    raw = A_i_zeta_vertex_raw(system, a, vertex)
    alpha = _param(system, 'zeta_heisenberg_alpha', 8.0)
    i0_scale = _param(system, 'zeta_i0_scale', 1.0) * _param(system, 'I0', 0.00917)
    return i0_scale * heisenberg_soft_clip(raw, alpha)


def A_i_zeta(system: OrbitalSystem, a: str) -> complex:
    if system.zeta_pole is None:
        return 0.0j
    total = 0.0j
    for vertex in system.zeta_pole.vertices:
        total += A_i_zeta_vertex(system, a, vertex)
    return total


def A_numpy(system: OrbitalSystem) -> np.ndarray:
    names = system.names()
    mat = np.zeros((len(names), len(names)), dtype=complex)
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            mat[i, j] = A_ij(system, a, b)
    return mat


def global_coherence(system: OrbitalSystem) -> float:
    weights = [max(0.0, s.coherence_weight) for s in system.sectors.values()]
    total = sum(weights)
    if total <= 0.0:
        return 0.0
    vec = 0.0j
    for s in system.sectors.values():
        vec += s.coherence_weight * cmath.exp(1j * (s.phi + s.berry_phase))
    return max(0.0, min(1.0, abs(vec) / total))


def chord_tension(system: OrbitalSystem) -> float:
    names = system.names()
    total = 0.0
    count = 0
    for i, a in enumerate(names):
        sa = system.sectors[a]
        va = bloch_vector(sa.theta, sa.phi + sa.berry_phase)
        for b in names[i + 1:]:
            sb = system.sectors[b]
            vb = bloch_vector(sb.theta, sb.phi + sb.berry_phase)
            dot = max(-1.0, min(1.0, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2]))
            total += system.coupling(a, b) * (1.0 - dot)
            count += 1
    return total / max(1, count)


def global_chirality(system: OrbitalSystem) -> float:
    values = [s.spin for s in system.sectors.values()]
    return sum(values) / max(1, len(values))


def closure_penalty(system: OrbitalSystem) -> float:
    return max(0.0, 1.0 - global_coherence(system)) + chord_tension(system)


def total_relational_potential(system: OrbitalSystem) -> float:
    tension_weight = _param(system, 'tension_weight', 0.25)
    closure_weight = _param(system, 'closure_weight', 0.10)
    return tension_weight * chord_tension(system) + closure_weight * closure_penalty(system)


def radial_spread(system: OrbitalSystem) -> float:
    radii = [poincare_radius(s.theta) for s in system.sectors.values()]
    if not radii:
        return 0.0
    mean = sum(radii) / len(radii)
    return sum((r - mean) ** 2 for r in radii) / len(radii)


def spectral_observables(system: OrbitalSystem) -> Dict[str, float]:
    A = A_numpy(system)
    if A.size == 0:
        return {'spectral_radius_A': 0.0, 'spectral_gap_A': 0.0, 'fiedler_L': 0.0}
    evals = np.linalg.eigvals(A)
    spectral_radius = float(max(abs(v) for v in evals)) if len(evals) else 0.0
    mags = sorted((float(abs(v)) for v in evals), reverse=True)
    spectral_gap = mags[0] - mags[1] if len(mags) >= 2 else (mags[0] if mags else 0.0)
    W = np.abs(A)
    D = np.diag(np.sum(W, axis=1))
    L = D - W
    le = np.linalg.eigvalsh(L)
    fiedler = float(le[1]) if len(le) >= 2 else 0.0
    return {
        'spectral_radius_A': spectral_radius,
        'spectral_gap_A': float(spectral_gap),
        'fiedler_L': fiedler,
    }


def holonomy_defect(system: OrbitalSystem) -> complex:
    total = 0.0j
    for s in system.sectors.values():
        total += cmath.exp(1j * (s.phi + s.berry_phase))
    return total


def closure_residuals(system: OrbitalSystem) -> Dict[str, float]:
    g = global_coherence(system)
    return {name: max(0.0, 1.0 - g + s.defect) for name, s in system.sectors.items()}


def local_vorticity(system: OrbitalSystem) -> Dict[str, float]:
    return {name: float(s.spin) for name, s in system.sectors.items()}


def homology_compatibility(system: OrbitalSystem) -> float:
    if not system.sectors:
        return 1.0
    penalties = [abs(s.rho - poincare_radius(s.theta)) for s in system.sectors.values()]
    return max(0.0, 1.0 - sum(penalties) / max(1, len(penalties)))


def zeta_tetra_defect(system: OrbitalSystem) -> float:
    if system.zeta_pole is None:
        return 0.0
    taus = [v.tau for v in system.zeta_pole.vertices]
    mean = sum(taus) / len(taus)
    return sum(abs(t - mean) for t in taus) / len(taus)


def effective_tau_zeta(system: OrbitalSystem) -> float:
    if system.zeta_pole is None:
        return 0.0
    weights = [v.weight for v in system.zeta_pole.vertices]
    total = sum(weights)
    return sum(v.tau * v.weight for v in system.zeta_pole.vertices) / max(1e-12, total)


def effective_phase_zeta(system: OrbitalSystem) -> float:
    if system.zeta_pole is None:
        return 0.0
    total = 0.0j
    for vertex in system.zeta_pole.vertices:
        total += vertex.weight * cmath.exp(1j * vertex.phi)
    return cmath.phase(total) if total != 0 else 0.0


def zeta_coupling_norm_raw(system: OrbitalSystem) -> float:
    if system.zeta_pole is None:
        return 0.0
    return sum(abs(A_i_zeta_vertex_raw(system, name, vertex)) for name in system.names() for vertex in system.zeta_pole.vertices)


def zeta_coupling_norm(system: OrbitalSystem) -> float:
    if system.zeta_pole is None:
        return 0.0
    return sum(abs(A_i_zeta_vertex(system, name, vertex)) for name in system.names() for vertex in system.zeta_pole.vertices)
