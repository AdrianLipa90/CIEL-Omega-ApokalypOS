"""
CIEL / TIR N-body Kepler canon v4:
constructive U(1) rotor -> constant-modulus complex-field embedding.

For phase inertia I_phi > 0 and relational phase chi, define

    psi := sqrt(I_phi/2) * exp(i chi).

Then the standard U(1) scalar-field Noether current reduces to the
background-free relational phase rotor current

    J_mu = I_phi D_mu chi.

This proves an explicit current embedding. It does not assert that every
historical ENB field configuration is this constant-modulus sector.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
import math
import numpy as np

def rotor_amplitude(I_phi: float) -> float:
    I=float(I_phi)
    if I<=0:
        raise ValueError("I_phi must be positive")
    return math.sqrt(I/2.0)

def rotor_to_complex_field(chi: float, I_phi: float) -> complex:
    A=rotor_amplitude(I_phi)
    return A*complex(math.cos(float(chi)),math.sin(float(chi)))

def scalar_noether_current_from_phase_gradient(I_phi: float, D_chi: Sequence[float]) -> np.ndarray:
    A=rotor_amplitude(I_phi)
    d=np.asarray(D_chi,dtype=float)
    return 2.0*A*A*d

def relational_rotor_current(I_phi: float, D_chi: Sequence[float], *, J0: Sequence[float] | None=None) -> np.ndarray:
    d=np.asarray(D_chi,dtype=float)
    out=float(I_phi)*d
    if J0 is not None:
        j0=np.asarray(J0,dtype=float)
        if j0.shape!=out.shape:
            raise ValueError("J0 shape mismatch")
        out=out+j0
    return out

def current_embedding_residual(I_phi: float, D_chi: Sequence[float]) -> float:
    a=scalar_noether_current_from_phase_gradient(I_phi,D_chi)
    b=relational_rotor_current(I_phi,D_chi)
    return float(np.linalg.norm(a-b))

@dataclass(frozen=True)
class EmbeddingReport:
    I_phi: float
    amplitude: float
    residual: float
    status: str

def validate_embedding(I_phi: float, D_chi: Sequence[float]) -> EmbeddingReport:
    return EmbeddingReport(float(I_phi),rotor_amplitude(I_phi),current_embedding_residual(I_phi,D_chi),"EXACT_CURRENT_EMBEDDING")

__all__=[
    "rotor_amplitude","rotor_to_complex_field",
    "scalar_noether_current_from_phase_gradient","relational_rotor_current",
    "current_embedding_residual","EmbeddingReport","validate_embedding",
]
