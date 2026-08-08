"""
CIEL/Ω Vocabulary — Relational Medium Closure (Entries 041–045)

Status: NEW_DERIVED_CLOSURE

Authorized 2026-08-08. These entries fill the historical numbering gap, but
are NOT backdated as recovered March-2025 Dictionary content.

041 Medium -> 042 Relation -> 043 Relational Field
-> 044 Ethical Scalar -> 045 Ethical Gradient/Trajectory -> 046 Initiation

Ethics is a continuous scalar on a relational medium/field.
No moral threshold is encoded here.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple
import numpy as np

@dataclass(frozen=True)
class RelationalMedium:
    """041 Medium. M={Psi_i}: supplied carrier/domain for relations."""
    states: Tuple[np.ndarray, ...]

    @classmethod
    def from_states(cls, states: Sequence[np.ndarray]) -> "RelationalMedium":
        if not states:
            raise ValueError("Relational medium requires at least one state")
        arr=tuple(np.asarray(s) for s in states)
        shape=arr[0].shape
        if any(s.shape != shape for s in arr):
            raise ValueError("All states in one relational medium must share shape")
        return cls(arr)

    @property
    def cardinality(self) -> int:
        return len(self.states)

class Relation:
    """042 Relation. rho_ij=R(Psi_i,Psi_j), continuous and unthresholded."""

    @staticmethod
    def scalar(psi_i: np.ndarray, psi_j: np.ndarray) -> float:
        from .core_concepts import Resonance
        return float(Resonance.calculate(psi_i, psi_j))

    @staticmethod
    def matrix(medium: RelationalMedium) -> np.ndarray:
        n=medium.cardinality
        W=np.eye(n,dtype=float)
        for i in range(n):
            for j in range(i+1,n):
                r=Relation.scalar(medium.states[i], medium.states[j])
                W[i,j]=W[j,i]=r
        return W

@dataclass(frozen=True)
class RelationalField:
    """043 Relational Field. F_R=(M,W), W_ij=rho_ij."""
    medium: RelationalMedium
    weights: np.ndarray

    @classmethod
    def derive(cls, medium: RelationalMedium) -> "RelationalField":
        return cls(medium, Relation.matrix(medium))

    def node_coherence(self) -> np.ndarray:
        n=self.medium.cardinality
        if n==1:
            return np.ones(1,dtype=float)
        return (self.weights.sum(axis=1)-1.0)/(n-1)

    def global_coherence(self) -> float:
        n=self.medium.cardinality
        if n==1:
            return 1.0
        iu=np.triu_indices(n,k=1)
        return float(np.mean(self.weights[iu]))

@dataclass(frozen=True)
class EthicalScalarState:
    """
    044 Ethical Scalar.

        E_rel = R_M * A_rel * S_rel

    R_M in [0,1]  : coherence of the relational medium/field.
    A_rel in [-1,1]: SIGNED intention/effect alignment.
    S_rel in [0,1] : temporal/phase stability.
    E_rel in [-1,1].

    No PASS/FAIL threshold belongs to this scalar.
    """
    relational_coherence: float
    alignment: float
    stability: float
    value: float

    @staticmethod
    def compute_signed_alignment(intention: Sequence[float], effect: Sequence[float]) -> Optional[float]:
        i=np.asarray(intention,dtype=float).ravel()
        e=np.asarray(effect,dtype=float).ravel()
        if i.shape != e.shape or i.size == 0:
            return None
        ni=float(np.linalg.norm(i))
        ne=float(np.linalg.norm(e))
        if ni == 0.0 or ne == 0.0:
            return None
        return float(np.dot(i,e)/(ni*ne))

    @classmethod
    def derive(
        cls,
        field: RelationalField,
        intention: Sequence[float],
        effect: Sequence[float],
        stability: float,
    ) -> Optional["EthicalScalarState"]:
        A=cls.compute_signed_alignment(intention,effect)
        if A is None:
            return None
        R=float(field.global_coherence())
        S=float(stability)
        if not 0.0 <= R <= 1.0:
            raise ValueError("relational coherence must lie in [0,1]")
        if not -1.0 <= A <= 1.0:
            raise ValueError("signed alignment must lie in [-1,1]")
        if not 0.0 <= S <= 1.0:
            raise ValueError("stability must lie in [0,1]")
        return cls(R,A,S,float(R*A*S))

@dataclass(frozen=True)
class EthicalGradient:
    """
    045 Ethical Gradient / Relational Trajectory.

        grad_E ~ Delta E_rel / Delta tau

    Sign is direction of change of relational scalar, not a binary moral label.
    """
    delta: float
    rate: Optional[float]

    @classmethod
    def between(
        cls,
        previous: EthicalScalarState,
        current: EthicalScalarState,
        delta_tau: Optional[float]=None,
    ) -> "EthicalGradient":
        d=float(current.value-previous.value)
        if delta_tau is None:
            return cls(d,None)
        if delta_tau <= 0:
            raise ValueError("delta_tau must be positive")
        return cls(d,float(d/delta_tau))

__all__=[
    "RelationalMedium","Relation","RelationalField",
    "EthicalScalarState","EthicalGradient"
]
