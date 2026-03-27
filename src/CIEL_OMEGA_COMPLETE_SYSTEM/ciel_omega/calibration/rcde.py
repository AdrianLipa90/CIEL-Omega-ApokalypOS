"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

RCDE — Resonance-Coherence-Drift-Equilibrium calibrators.

Sources (unified — eliminates 3 duplicates):
  - ext2.RCDECalibrated      — static normalize / resonance index / calibrate
  - ext17.RCDECalibrator      — lite Σ↔Ψ homeostat
  - ext18.RCDECalibratorPro   — adaptive target Σ* + λ gain
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.math_utils import field_norm


# ---------------------------------------------------------------------------
# Basic static calibration (ext2)
# ---------------------------------------------------------------------------

class RCDECalibrated:
    """Static utility methods for field normalisation and resonance."""

    @staticmethod
    def normalize_field(field: np.ndarray) -> np.ndarray:
        return field / field_norm(field)

    @staticmethod
    def compute_resonance_index(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.mean(np.abs(a * np.conj(b))))

    @staticmethod
    def calibrate(reference: np.ndarray, test: np.ndarray) -> float:
        ref = RCDECalibrated.normalize_field(reference)
        tst = RCDECalibrated.normalize_field(test)
        return float(np.tanh(RCDECalibrated.compute_resonance_index(ref, tst)))


# ---------------------------------------------------------------------------
# Lite homeostat (ext17)
# ---------------------------------------------------------------------------

@dataclass
class RCDECalibrator:
    """Lite Σ ↔ Ψ homeostat with fixed target and gain."""

    target: float = 0.8
    lam: float = 0.05

    def step(self, sigma: float, psi: np.ndarray) -> float:
        """Return updated Σ scalar after one homeostat step."""
        psi_norm = field_norm(psi)
        error = self.target - sigma
        return float(sigma + self.lam * error * psi_norm)


# ---------------------------------------------------------------------------
# Pro homeostat with adaptive λ (ext18)
# ---------------------------------------------------------------------------

@dataclass
class RCDECalibratorPro:
    """Adaptive Σ ↔ Ψ homeostat: target Σ* adjusts, λ adapts to error."""

    target: float = 0.8
    lam: float = 0.05
    adapt_rate: float = 0.01

    def step(self, sigma: float, psi: np.ndarray) -> float:
        psi_norm = field_norm(psi)
        error = self.target - sigma
        new_sigma = float(sigma + self.lam * error * psi_norm)
        # adapt λ: increase when far from target, decrease when close
        self.lam += self.adapt_rate * (abs(error) - self.lam)
        self.lam = float(np.clip(self.lam, 0.001, 0.5))
        return new_sigma


__all__ = ["RCDECalibrated", "RCDECalibrator", "RCDECalibratorPro"]
