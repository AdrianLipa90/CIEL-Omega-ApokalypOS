"""Canonical signed relational Ethical Resonance Index.

Supersedes the legacy unsigned package-level ERI semantics without deleting
historical source. Direct legacy imports remain readable; the vocabulary package
exports this implementation as canonical runtime ERI.
"""
from __future__ import annotations
from typing import List
import numpy as np

from .core_concepts import Resonance, Coherence

class EthicalResonanceIndex:
    """ERI = R * A * S with signed intention-effect alignment A in [-1,1]."""

    @staticmethod
    def calculate(resonance: float, alignment: float, stability: float) -> float:
        R=float(resonance); A=float(alignment); S=float(stability)
        if not 0.0 <= R <= 1.0:
            raise ValueError("resonance must lie in [0,1]")
        if not -1.0 <= A <= 1.0:
            raise ValueError("alignment must lie in [-1,1]")
        if not 0.0 <= S <= 1.0:
            raise ValueError("stability must lie in [0,1]")
        return float(R*A*S)

    @staticmethod
    def signed_alignment(intention: np.ndarray, effect: np.ndarray):
        i=np.asarray(intention).ravel()
        e=np.asarray(effect).ravel()
        if i.shape != e.shape or i.size == 0:
            return None
        ni=float(np.linalg.norm(i)); ne=float(np.linalg.norm(e))
        if ni == 0.0 or ne == 0.0:
            return None
        # vdot preserves complex-conjugate semantics; the ethical scalar uses
        # the signed real projection, not |dot|.
        return float(np.real(np.vdot(i,e))/(ni*ne))

    @classmethod
    def from_state(
        cls,
        psi_self: np.ndarray,
        psi_field: np.ndarray,
        intention: np.ndarray,
        effect: np.ndarray,
        coherence_history: List[float],
    ):
        R=Resonance.calculate(psi_self,psi_field)
        A=cls.signed_alignment(intention,effect)
        if A is None:
            return None
        raw_stability=Coherence.temporal_stability(coherence_history)
        # ERI expects S in [0,1]. This bound is a normalization of the legacy
        # inverse-variance observable, not a moral threshold.
        S=float(np.clip(raw_stability,0.0,1.0))
        return cls.calculate(R,A,S)

__all__=["EthicalResonanceIndex"]
