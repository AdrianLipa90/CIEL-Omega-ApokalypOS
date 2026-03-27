"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Common field-level mathematical utilities.

Sources (unified — eliminates duplicates across ext17, ext18, ext20):
  - laplacian2()       — 2D discrete Laplacian (5-point stencil)
  - field_norm()       — RMS norm of complex field
  - coherence_metric() — phase coherence via autocorrelation
  - smooth2d()         — simple box filter (no-FFT)
  - normalize_field()  — RMS-1 normalisation
"""

from __future__ import annotations

import numpy as np


def laplacian2(a: np.ndarray) -> np.ndarray:
    """2D discrete Laplacian (5-point stencil, zero boundary)."""
    out = np.zeros_like(a)
    out[1:-1, 1:-1] = (
        a[2:, 1:-1] + a[:-2, 1:-1] + a[1:-1, 2:] + a[1:-1, :-2]
        - 4.0 * a[1:-1, 1:-1]
    )
    return out


def field_norm(psi: np.ndarray) -> float:
    """RMS norm: √⟨|ψ|²⟩."""
    return float(np.sqrt(np.mean(np.abs(psi) ** 2)) + 1e-12)


def coherence_metric(psi: np.ndarray) -> float:
    """Phase coherence — ratio of mean amplitude to RMS amplitude.

    Returns 1.0 for a perfectly coherent (uniform phase) field,
    < 1.0 for disordered phase.
    """
    amp = np.abs(psi)
    rms = float(np.sqrt(np.mean(amp ** 2)) + 1e-12)
    mean_amp = float(np.mean(amp))
    return mean_amp / rms


def normalize_field(field: np.ndarray) -> np.ndarray:
    """Normalise field to RMS = 1."""
    return field / (field_norm(field))


def smooth2d(a: np.ndarray, k: int = 1) -> np.ndarray:
    """Simple box filter (no-FFT) — *k* passes over a 2D array."""
    if k <= 0:
        return a
    out = a.copy()
    for _ in range(k):
        tmp = np.pad(out, ((1, 1), (1, 1)), mode="reflect")
        out = (
            tmp[1:-1, 1:-1]
            + tmp[0:-2, 1:-1]
            + tmp[2:, 1:-1]
            + tmp[1:-1, 0:-2]
            + tmp[1:-1, 2:]
        ) / 5.0
    return out


def gradient2d(field: np.ndarray):
    """Central-difference gradient (dy, dx) for a 2D complex/real array."""
    gy = np.zeros_like(field)
    gx = np.zeros_like(field)
    gy[1:-1, :] = 0.5 * (field[2:, :] - field[:-2, :])
    gx[:, 1:-1] = 0.5 * (field[:, 2:] - field[:, :-2])
    return gy, gx


__all__ = [
    "laplacian2",
    "field_norm",
    "coherence_metric",
    "normalize_field",
    "smooth2d",
    "gradient2d",
]
