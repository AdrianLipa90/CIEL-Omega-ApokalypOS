"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Experiment registry — 10 baseline experiments for CIEL/Ω validation.

Source: ext17 (experiments + ExpRegistry + make_seed)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple

import numpy as np

from ciel_omega.bio.schumann import SchumannClock, schumann_harmonics
from ciel_omega.calibration.rcde import RCDECalibrator
from ciel_omega.core.math_utils import coherence_metric, field_norm, laplacian2
from ciel_omega.runtime.omega.drift_core import OmegaDriftCore

# -- helpers ----------------------------------------------------------------

ExpFn = Callable[[], Dict[str, Any]]


def make_seed(n: int = 96, a: float = 1.0, b: float = 0.3) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    x = np.linspace(-2, 2, n)
    X, Y = np.meshgrid(x, x)
    psi0 = np.exp(-(X ** 2 + Y ** 2)) * np.exp(1j * (a * X + b * Y))
    sigma0 = np.exp(-(X ** 2 + Y ** 2) / 2.0)
    return psi0.astype(np.complex128), sigma0.astype(np.float64), (X + 0j)


@dataclass
class ExpRegistry:
    exps: Dict[str, ExpFn] = field(default_factory=dict)

    def add(self, name: str, fn: ExpFn):
        self.exps[name] = fn

    def run(self, names: List[str]) -> Dict[str, Dict[str, Any]]:
        return {n: self.exps[n]() for n in names if n in self.exps}


# -- 10 experiments ---------------------------------------------------------

def exp_c01() -> Dict[str, Any]:
    """Norm stability without drift."""
    psi, _, _ = make_seed()
    for _ in range(20):
        psi = psi + 1j * 0.02 * laplacian2(psi)
        psi /= field_norm(psi)
    return {"norm": field_norm(psi), "coherence": coherence_metric(psi)}


def exp_c02() -> Dict[str, Any]:
    """Phase drift over time."""
    psi, _, _ = make_seed()
    for t in range(20):
        psi *= np.exp(1j * 0.05 * t)
        psi = psi + 1j * 0.01 * laplacian2(psi)
        psi /= field_norm(psi)
    return {"norm": field_norm(psi), "coherence": coherence_metric(psi)}


def exp_a2ebdead() -> Dict[str, Any]:
    """Two-field synchronisation (phase death)."""
    A, _, _ = make_seed()
    B, _, _ = make_seed(b=0.6)
    for _ in range(30):
        A = A * np.conj(B)
        A /= field_norm(A); B /= field_norm(B)
        if np.mean(np.abs(A - B)) < 1e-3:
            return {"sync": True, "delta": float(np.mean(np.abs(A - B)))}
        B = 0.5 * (B + A * np.exp(1j * 0.01))
    return {"sync": False, "delta": float(np.mean(np.abs(A - B)))}


def exp_47fdb331() -> Dict[str, Any]:
    """Schumann harmonic energy."""
    n = 1024
    t = np.linspace(0, 1, n)
    omega = 2 * np.pi * schumann_harmonics(7.83, 1)
    sig = np.sin(omega * t) + 0.3 * np.sin(2 * omega * t)
    energy = float(np.mean(sig ** 2))
    return {"energy": energy, "rms": float(np.sqrt(energy))}


def exp_72b221d9() -> Dict[str, Any]:
    """Controlled phase collapse."""
    psi, _, _ = make_seed()
    for _ in range(25):
        ph = np.angle(psi)
        psi *= np.exp(-np.abs(ph) / 15.0)
        psi = psi + 1j * 0.005 * laplacian2(psi)
        psi /= field_norm(psi)
    return {"coherence": coherence_metric(psi), "norm": field_norm(psi)}


def exp_rcde_calibrated() -> Dict[str, Any]:
    """Σ ↔ Ψ homeostat."""
    psi, _, _ = make_seed()
    rcde = RCDECalibrator(target=0.8, lam=0.25)
    sigmas = []
    sigma = 0.6
    for _ in range(30):
        psi = psi + 1j * 0.01 * laplacian2(psi)
        psi /= field_norm(psi)
        sigma = rcde.step(sigma, psi)
        sigmas.append(sigma)
    return {"sigma_last": float(sigmas[-1]), "sigma_mean": float(np.mean(sigmas))}


def exp_rescxparker_lite() -> Dict[str, Any]:
    """Parallel empathy (lite, no sockets)."""
    psiA, _, _ = make_seed(b=0.2)
    psiB, _, _ = make_seed(b=-0.2)
    clk = SchumannClock()
    drift = OmegaDriftCore(clk, drift_gain=0.03, harmonic=1)
    es = []
    for _ in range(20):
        psiA = drift.step(psiA, sigma_scalar=0.9)
        psiB = drift.step(psiB, sigma_scalar=0.9)
        es.append(float(np.exp(-np.mean(np.abs(psiA - psiB)))))
    return {"empathy_mean": float(np.mean(es)), "empathy_last": float(es[-1])}


def exp_vych_boot_ritual() -> Dict[str, Any]:
    """Ceremonial boot aligned to 7.83 Hz."""
    psi, sigma, _ = make_seed()
    clk = SchumannClock()
    omega = OmegaDriftCore(clk, drift_gain=0.04, harmonic=1)
    rcde = RCDECalibrator(target=0.8, lam=0.2)
    s = 0.5
    for _ in range(16):
        psi = omega.step(psi, sigma_scalar=s)
        s = rcde.step(s, psi)
    return {"boot_complete": True, "sigma": s, "coherence": coherence_metric(psi)}


def exp_dissociation() -> Dict[str, Any]:
    """Ego ↔ world correlation."""
    ego, _, _ = make_seed()
    world = np.roll(ego, 3, axis=0) * np.exp(1j * 0.2)
    a = ego.real.ravel(); b = world.real.ravel()
    a = (a - a.mean()) / (a.std() + 1e-12)
    b = (b - b.mean()) / (b.std() + 1e-12)
    rho = float(np.dot(a, b) / (len(a) - 1))
    state = "integration" if rho > 0.8 else ("dissociation" if rho < 0.3 else "mixed")
    return {"rho": rho, "state": state}


def exp_noweparadoxy() -> Dict[str, Any]:
    """Semantic stress test — controlled decision chaos."""
    val = random.random()
    paradox = (1 - val) if random.random() > 0.5 else val
    vals = [random.random() for _ in range(9)]
    med = float(np.median(vals))
    return {"paradox_out": paradox, "median_noise": med}


# -- factory ----------------------------------------------------------------

def make_lab_registry() -> ExpRegistry:
    reg = ExpRegistry()
    reg.add("c01", exp_c01)
    reg.add("c02", exp_c02)
    reg.add("a2ebdead", exp_a2ebdead)
    reg.add("47fdb331", exp_47fdb331)
    reg.add("72b221d9", exp_72b221d9)
    reg.add("rcde_calibrated", exp_rcde_calibrated)
    reg.add("ResCxParKer_lite", exp_rescxparker_lite)
    reg.add("VYCH_BOOT_RITUAL", exp_vych_boot_ritual)
    reg.add("dissociation", exp_dissociation)
    reg.add("noweparadoxy", exp_noweparadoxy)
    return reg


__all__ = ["ExpRegistry", "make_lab_registry", "make_seed"]
