"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Psychic (empathic) interaction between two consciousness fields.

Source: ext6.PsychField
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.math_utils import field_norm


@dataclass
class PsychField:
    """Empathic coupling of two (or more) consciousness fields."""

    empathy: float = 0.7       # 0..1  coupling strength
    phase_lock: float = 0.2    # 0..1  phase alignment strength

    def interact(self, psi_a: np.ndarray, psi_b: np.ndarray) -> np.ndarray:
        """Return the empathically-merged field (weighted mix + phase alignment)."""
        # amplitude-weighted blend
        blend = (1.0 - self.empathy) * psi_a + self.empathy * psi_b

        # partial phase-locking toward psi_b
        phase_a = np.angle(blend)
        phase_b = np.angle(psi_b)
        new_phase = phase_a + self.phase_lock * (phase_b - phase_a)
        result = np.abs(blend) * np.exp(1j * new_phase)

        result /= field_norm(result)
        return result

    def resonance(self, psi_a: np.ndarray, psi_b: np.ndarray) -> float:
        """Scalar empathic resonance score ∈ [0, 1]."""
        return float(np.tanh(np.mean(np.abs(np.conj(psi_a) * psi_b))))


__all__ = ["PsychField"]
