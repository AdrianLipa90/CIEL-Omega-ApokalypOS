"""
CIEL / TIR — Canonical Information Backreaction v1.1

Source parent: Hilbert_Kahler_Phase_Intention_Hamiltonian, eqs. (61)-(70).

Minimal relational Lagrangian:
    L = 1/2 g_ab qdot^a qdot^b + I_phi/2 (D_t chi)^2
        + J0_phase_offset D_t chi - V(q)

Canonical phase momentum:
    J = I_phi D_t chi + J0_phase_offset

Relational canonical momentum:
    p_a = g_ab qdot^b + J A_a

Covariant momentum:
    Pi_a = p_a - J A_a

Hamiltonian:
    H = (J-J0_phase_offset)^2/(2 I_phi)
        + 1/2 g^{ab} Pi_a Pi_b + V(q)

NOTATION FIREWALL:
`J0_phase_offset` is the scalar source symbol J_0 from the Hamiltonian.
It is not the residual spatial information current `J_residual` from
`information_dynamics.py`.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class CanonicalRelationalState:
    q: np.ndarray
    p: np.ndarray
    J: float
    J0_phase_offset: float
    I_phi: float

    def __post_init__(self):
        q=np.asarray(self.q,dtype=float)
        p=np.asarray(self.p,dtype=float)
        if q.ndim!=1 or p.shape!=q.shape:
            raise ValueError("q and p must be equal-shaped 1D vectors")
        if self.I_phi<=0:
            raise ValueError("I_phi must be positive")
        if not np.isscalar(self.J) or not np.isscalar(self.J0_phase_offset):
            raise ValueError("J and J0_phase_offset must be scalar")
        object.__setattr__(self,"q",q)
        object.__setattr__(self,"p",p)


@dataclass(frozen=True)
class HamiltonianGeometry:
    g_inv: np.ndarray
    A: np.ndarray
    d_g_inv: np.ndarray
    d_A: np.ndarray
    grad_V: np.ndarray
    V: float=0.0

    def __post_init__(self):
        G=np.asarray(self.g_inv,dtype=float)
        A=np.asarray(self.A,dtype=float)
        dG=np.asarray(self.d_g_inv,dtype=float)
        dA=np.asarray(self.d_A,dtype=float)
        grad=np.asarray(self.grad_V,dtype=float)
        n=A.size
        if G.shape!=(n,n): raise ValueError("g_inv shape")
        if dG.shape!=(n,n,n): raise ValueError("d_g_inv shape must be (n,n,n)")
        if dA.shape!=(n,n): raise ValueError("d_A shape must be (n,n)")
        if grad.shape!=(n,): raise ValueError("grad_V shape")
        if not np.allclose(G,G.T,atol=1e-14,rtol=0.0):
            raise ValueError("g_inv must be symmetric")
        object.__setattr__(self,"g_inv",G)
        object.__setattr__(self,"A",A)
        object.__setattr__(self,"d_g_inv",dG)
        object.__setattr__(self,"d_A",dA)
        object.__setattr__(self,"grad_V",grad)


def covariant_momentum(state: CanonicalRelationalState,geom: HamiltonianGeometry) -> np.ndarray:
    if geom.A.shape!=state.q.shape:
        raise ValueError("geometry/state dimension mismatch")
    return state.p-float(state.J)*geom.A


def phase_velocity(state: CanonicalRelationalState) -> float:
    return float((state.J-state.J0_phase_offset)/state.I_phi)


def hamiltonian(state: CanonicalRelationalState,geom: HamiltonianGeometry) -> float:
    Pi=covariant_momentum(state,geom)
    H_phase=(state.J-state.J0_phase_offset)**2/(2.0*state.I_phi)
    H_rel=0.5*float(Pi@geom.g_inv@Pi)+float(geom.V)
    return float(H_phase+H_rel)


def hamilton_equations(state: CanonicalRelationalState,geom: HamiltonianGeometry):
    """
    Fixed-J local Hamilton equations:
        qdot^a = g^{ab} Pi_b
        pdot_k = J (partial_k A_a) qdot^a
                 - 1/2 Pi_a (partial_k g^{ab}) Pi_b
                 - partial_k V.
    """
    Pi=covariant_momentum(state,geom)
    qdot=geom.g_inv@Pi
    pdot=np.empty(state.q.size,dtype=float)
    for k in range(state.q.size):
        connection_term=float(state.J)*float(geom.d_A[k]@qdot)
        metric_term=0.5*float(Pi@geom.d_g_inv[k]@Pi)
        pdot[k]=connection_term-metric_term-float(geom.grad_V[k])
    return qdot,pdot


def curvature_tensor(d_A: np.ndarray) -> np.ndarray:
    dA=np.asarray(d_A,dtype=float)
    if dA.ndim!=2 or dA.shape[0]!=dA.shape[1]:
        raise ValueError("d_A must be square")
    return dA-dA.T


def covariant_momentum_rate_flat_metric(state: CanonicalRelationalState,geom: HamiltonianGeometry) -> np.ndarray:
    """For coordinate-constant metric: Pi_dot = J F qdot - grad V."""
    if np.max(np.abs(geom.d_g_inv))>1e-14:
        raise ValueError("flat/coordinate-constant metric required")
    qdot,pdot=hamilton_equations(state,geom)
    dA_dt=geom.d_A.T@qdot
    return pdot-float(state.J)*dA_dt


@dataclass(frozen=True)
class BackreactionReceipt:
    hamiltonian: float
    phase_velocity: float
    qdot: tuple[float,...]
    pdot: tuple[float,...]
    covariant_momentum: tuple[float,...]
    J: float
    J0_phase_offset: float
    status: str
    normalization: str


def backreaction_receipt(state: CanonicalRelationalState,geom: HamiltonianGeometry) -> BackreactionReceipt:
    qdot,pdot=hamilton_equations(state,geom)
    Pi=covariant_momentum(state,geom)
    return BackreactionReceipt(
        hamiltonian(state,geom),phase_velocity(state),
        tuple(float(x) for x in qdot),tuple(float(x) for x in pdot),
        tuple(float(x) for x in Pi),float(state.J),float(state.J0_phase_offset),
        "SOURCE_DERIVED_CANONICAL_BACKREACTION",
        "connection coupling coefficient is canonical phase momentum J; no fitted force coefficient",
    )


__all__=[
    "CanonicalRelationalState","HamiltonianGeometry","covariant_momentum","phase_velocity",
    "hamiltonian","hamilton_equations","curvature_tensor","covariant_momentum_rate_flat_metric",
    "BackreactionReceipt","backreaction_receipt",
]
