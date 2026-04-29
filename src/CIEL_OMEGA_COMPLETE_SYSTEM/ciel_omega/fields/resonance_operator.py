"""CIEL/Ω Resonance Operator — R(S,I) = |⟨S|I⟩|² / (‖S‖² · ‖I‖²)

Restored from Adrian Lipa / Intention Lab — DrWatsonProject/brainmemorytopology.py.

Semantic relevance as geometric inner product, not frequency statistics.
Two representations:
  - vector: full R(S,I) for multi-dimensional feature vectors
  - phase: scalar shortcut for Berry-phase-encoded concepts (most common use)
"""

from __future__ import annotations

import math
import numpy as np


class ResonanceOperator:
    """Universal Resonance Operator R(S,I) = |⟨S|I⟩|² / (‖S‖² · ‖I‖²).

    Measures how much a symbolic state S resonates with an intention I.
    Returns 1.0 for perfect alignment, 0.0 for orthogonality.
    """

    @staticmethod
    def compute(S: np.ndarray, I: np.ndarray) -> float:
        """Resonance between vectors S and I (complex or real)."""
        S = np.asarray(S, dtype=complex)
        I = np.asarray(I, dtype=complex)
        if S.shape != I.shape:
            min_len = min(S.size, I.size)
            S = S.flat[:min_len]
            I = I.flat[:min_len]
        norm_sq = (np.linalg.norm(S) * np.linalg.norm(I)) ** 2
        if norm_sq == 0.0:
            return 0.0
        return float(abs(np.vdot(S, I)) ** 2 / norm_sq)

    @staticmethod
    def phase_resonance(phi_item: float, phi_intention: float) -> float:
        """Scalar resonance between two Berry phases (angles on Bloch sphere).

        Equivalent to |cos(phi_item - phi_intention)|² — purely geometric,
        no sampling, no frequency counting.
        """
        return math.cos(phi_item - phi_intention) ** 2

    @staticmethod
    def phase_alignment(phi1: np.ndarray, phi2: np.ndarray) -> float:
        """Mean phase alignment across oscillatory fields."""
        return float(abs(np.mean(np.cos(np.asarray(phi1) - np.asarray(phi2)))))

    @staticmethod
    def is_coherent(resonance: float, threshold: float = 0.5) -> bool:
        return resonance >= threshold


__all__ = ["ResonanceOperator"]
