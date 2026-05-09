"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Soul Invariant Σ — spectral coherence measure of consciousness fields.

Consolidated: formerly split across fields/ and memory/. Single source of truth.

  - SoulInvariant         — stateful: soul_field (8-dim complex), topological charge,
                            persistence, memory traces, Zeta-Riemann zeros. [ext3]
  - SoulInvariantOperator — FFT-based spectral Σ, stateless. [ext1]
  - ZetaRiemannOperator   — product-over-zeros filter ∏(s - ρ_k). [unique]
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# First 10 non-trivial zeros of ζ(s) on the critical line
_RIEMANN_ZEROS = np.array([
    0.5 + 14.134725j, 0.5 + 21.022040j, 0.5 + 25.010858j,
    0.5 + 30.424876j, 0.5 + 32.935062j, 0.5 + 37.586178j,
    0.5 + 40.918720j, 0.5 + 43.327073j, 0.5 + 48.005151j,
    0.5 + 49.773832j,
], dtype=complex)


class SoulInvariant:
    """Σ — topological invariant in intention-phase space.

    Stateful: carries soul_field (complex vector), topological charge,
    persistence, and memory traces. Also computes gradient-based Σ
    from external fields (no-FFT, real-time safe).
    """

    def __init__(self, dimension: int = 8, delta: float = 0.3, eps: float = 1e-12):
        self.dimension = int(dimension)
        self.delta = delta
        self.eps = eps
        self.soul_field = np.zeros(self.dimension, dtype=complex)
        self.topological_charge: float = 0.0
        self.persistence_factor: float = 1.0
        self.memory_traces: List[Dict[str, Any]] = []

    # ── Stateless Σ from external field ──────────────────────────────────────

    def compute(self, field: np.ndarray) -> float:
        """Σ = log(1 + ⟨|∇f|²⟩ / ⟨|f|²⟩)  — gradient-based, no FFT."""
        f = np.abs(field)
        norm = float(np.mean(f ** 2))
        grad_energy = float(np.mean(sum(np.abs(k) ** 2 for k in np.gradient(f))))
        return float(np.log1p(grad_energy / (norm + self.eps)))

    def normalise(self, field: np.ndarray) -> np.ndarray:
        """Rescale field so that Σ → 1."""
        sigma = self.compute(field)
        return field / (np.sqrt(sigma) + self.eps)

    # ── Stateful soul field ───────────────────────────────────────────────────

    def initialize_soul_field(self, pattern: str = "identity") -> np.ndarray:
        """Initialize soul_field with a chosen pattern.

        'identity'  — unique random normalized vector
        'coherent'  — uniform amplitude, linear phase ramp
        'entangled' — fixed 8-dim entangled pattern
        """
        pat = (pattern or "identity").lower()
        if pat == "identity":
            z = np.random.random(self.dimension) + 1j * np.random.random(self.dimension)
            self.soul_field = z / (np.linalg.norm(z) + 1e-12)
        elif pat == "coherent":
            phase = np.linspace(0.0, 2.0 * np.pi, self.dimension, endpoint=False)
            self.soul_field = np.exp(1j * phase) / np.sqrt(self.dimension)
        elif pat == "entangled":
            base = np.array([
                1+1j, -1+1j, 1-1j, -1-1j,
                0.5+0.5j, -0.5+0.5j, 0.5-0.5j, -0.5-0.5j,
            ], dtype=complex)
            if self.dimension != 8:
                reps = int(np.ceil(self.dimension / 8))
                base = np.tile(base, reps)[:self.dimension]
            self.soul_field = base / (np.linalg.norm(base) + 1e-12)
        else:
            raise ValueError(f"Unknown soul pattern: {pattern!r}")
        return self.soul_field

    def compute_topological_invariant(self, connection_field: np.ndarray) -> float:
        """Σ as discretized winding number ∮ dφ / 2π over connection_field."""
        cf = np.asarray(connection_field, dtype=complex).ravel()
        if cf.size < 2:
            cf = self.soul_field if self.soul_field.size >= 2 else np.array([1+0j, 1+0j])
        if cf[0] != cf[-1]:
            cf = np.concatenate([cf, cf[:1]])
        angles = np.unwrap(np.angle(cf))
        self.topological_charge = float((angles[-1] - angles[0]) / (2.0 * np.pi))
        return self.topological_charge

    def soul_resonance(self, other: "SoulInvariant") -> float:
        """| ⟨ψ_self | ψ_other⟩ |² clipped to [0, 1]."""
        a, b = self.soul_field, other.soul_field
        if a.size == 0 or b.size == 0:
            return 0.0
        n = min(a.size, b.size)
        return float(np.clip(np.abs(np.vdot(a[:n], b[:n])) ** 2, 0.0, 1.0))

    def update_persistence(self, coherence_level: float, dt: float = 1.0) -> float:
        """Persistence decays slower at high coherence. Floor = 0.1."""
        c = float(np.clip(coherence_level, 0.0, 1.0))
        self.persistence_factor *= float(np.exp(-0.01 * (1.0 - c) * max(dt, 0.0)))
        self.persistence_factor = max(self.persistence_factor, 0.1)
        return self.persistence_factor

    def store_memory_trace(self, experience: Dict[str, Any]) -> None:
        """Append a memory trace snapshot tied to current soul state."""
        self.memory_traces.append({
            "timestamp": time.time(),
            "experience": experience,
            "soul_state": self.soul_field.copy(),
            "topological_charge": self.topological_charge,
            "persistence": self.persistence_factor,
        })
        if len(self.memory_traces) > 1000:
            self.memory_traces = self.memory_traces[-1000:]


class SoulInvariantOperator:
    """FFT-based Σ — spectral power weighted by log(1 + |k|²).

    Stateless. Richer spectral information than gradient-based.
    """

    def __init__(self, eps: float = 1e-12):
        self.eps = eps

    def compute_sigma_invariant(self, field: np.ndarray) -> float:
        F = np.fft.fft2(field)
        power = np.abs(F) ** 2
        h, w = field.shape
        ky = np.fft.fftfreq(h)
        kx = np.fft.fftfreq(w)
        k2 = ky[:, None] ** 2 + kx[None, :] ** 2
        return float(np.mean(power * np.log1p(k2 + self.eps)))

    def rescale_to_ethics_bound(self, field: np.ndarray, bound: float = 0.90) -> np.ndarray:
        amp = np.sqrt(np.mean(np.abs(field) ** 2)) + self.eps
        return field * (np.sqrt(bound) / amp)


class ZetaRiemannOperator:
    """Product-over-zeros filter ∏(s - ρ_k - ε) applied to a spectrum.

    Defaults to the first 10 non-trivial zeros of ζ(s) on the critical line.
    Does NOT numerically evaluate ζ(s) itself.
    """

    def __init__(self, s_zeros: Optional[np.ndarray] = None):
        self.zeros = np.asarray(s_zeros, dtype=complex) if s_zeros is not None else _RIEMANN_ZEROS.copy()

    def apply(self, psi_spectrum: np.ndarray, s_values: np.ndarray, epsilon: float = 1e-6) -> np.ndarray:
        psi = np.asarray(psi_spectrum, dtype=complex)
        s = np.asarray(s_values, dtype=complex)
        if psi.size != s.size:
            raise ValueError("psi_spectrum and s_values must have the same size")
        zeta_like = np.ones_like(s, dtype=complex)
        for zero in self.zeros:
            zeta_like *= (s - (zero + epsilon))
        return zeta_like * psi


__all__ = ["SoulInvariant", "SoulInvariantOperator", "ZetaRiemannOperator"]
