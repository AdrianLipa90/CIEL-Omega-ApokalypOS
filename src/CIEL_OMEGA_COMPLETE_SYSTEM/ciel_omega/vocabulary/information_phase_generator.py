"""
CIEL / TIR — Intention/Information Phase Generator v2

Current-source reconciliation:

Quantized information/intention generator:
    I_hat_s(tau,k) = kappa W_hat_s + delta I_hat_0(tau,k)
    kappa = ln(2)/(24*pi)

Formal semiclassical intention charge / phase offset:
    J_I,s(tau,k) = hbar rho_s(k) I_s(tau,k)

or, at expectation/scalar level,
    J0_phase_offset = hbar rho_s(k)
                      [kappa <W_s> + <delta I_0>].

This is the correct bridge into the classical phase-first Hamiltonian
    J = I_phi D_t chi + J0_phase_offset.

It is NOT the statement J == <I_hat_s>.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional, Sequence
import numpy as np

KAPPA_INFORMATION=math.log(2.0)/(24.0*math.pi)


def information_generator_expectation(
    W_expectation: float,
    delta_I0_expectation: float,
    *,kappa: float=KAPPA_INFORMATION,
) -> float:
    return float(kappa)*float(W_expectation)+float(delta_I0_expectation)


def semiclassical_intention_charge(
    W_expectation: float,
    delta_I0_expectation: float,
    *,hbar: float,rho_s: float,kappa: float=KAPPA_INFORMATION,
) -> float:
    """
    J_I,s = hbar rho_s <I_s>
          = hbar rho_s [kappa <W_s> + <delta I_0>].

    All state-dependent inputs are supplied; no rhythm or fluctuation model is
    invented here.
    """
    I=information_generator_expectation(W_expectation,delta_I0_expectation,kappa=kappa)
    return float(hbar)*float(rho_s)*I


def free_phase_hamiltonian_expectation(
    W_expectation: float,
    delta_I0_expectation: float,
    *,hbar: float,delta_tau: float,rho_s: float,kappa: float=KAPPA_INFORMATION,
) -> float:
    if delta_tau<=0:
        raise ValueError("delta_tau must be positive")
    charge=semiclassical_intention_charge(
        W_expectation,delta_I0_expectation,hbar=hbar,rho_s=rho_s,kappa=kappa
    )
    return float(charge/delta_tau)


@dataclass(frozen=True)
class PhaseOffsetBinding:
    J0_phase_offset: float
    I_expectation: float
    hbar: float
    rho_s: float
    status: str
    provenance: str

    @property
    def source_identity_residual(self) -> float:
        return float(self.J0_phase_offset-self.hbar*self.rho_s*self.I_expectation)


def bind_phase_offset_to_information_generator(
    W_expectation: float,
    delta_I0_expectation: float,
    *,hbar: float,rho_s: float,provenance: str,
) -> PhaseOffsetBinding:
    I=information_generator_expectation(W_expectation,delta_I0_expectation)
    JI=semiclassical_intention_charge(
        W_expectation,delta_I0_expectation,hbar=hbar,rho_s=rho_s
    )
    return PhaseOffsetBinding(
        J0_phase_offset=JI,
        I_expectation=I,
        hbar=float(hbar),rho_s=float(rho_s),
        status="SOURCE_DERIVED_SEMICLASSICAL_PHASE_OFFSET",
        provenance=str(provenance),
    )


def build_canonical_state_with_information_offset(
    q: np.ndarray,
    p: np.ndarray,
    *,
    J: float,
    I_phi: float,
    W_expectation: float,
    delta_I0_expectation: float,
    hbar: float,
    rho_s: float,
    provenance: str,
):
    """Create CanonicalRelationalState using source-derived J_I,s as phase offset."""
    from .canonical_information_backreaction import CanonicalRelationalState
    binding=bind_phase_offset_to_information_generator(
        W_expectation,delta_I0_expectation,hbar=hbar,rho_s=rho_s,provenance=provenance
    )
    state=CanonicalRelationalState(
        q=np.asarray(q,dtype=float),p=np.asarray(p,dtype=float),J=float(J),
        J0_phase_offset=binding.J0_phase_offset,I_phi=float(I_phi),
    )
    return state,binding


def block_diagonal_metric(*blocks: np.ndarray) -> np.ndarray:
    if not blocks: return np.zeros((0,0),dtype=float)
    mats=[]
    for b in blocks:
        a=np.asarray(b,dtype=float)
        if a.ndim!=2 or a.shape[0]!=a.shape[1]: raise ValueError("metric blocks must be square")
        if not np.allclose(a,a.T,atol=1e-14,rtol=0.0): raise ValueError("metric blocks must be symmetric")
        mats.append(a)
    out=np.zeros((sum(m.shape[0] for m in mats),)*2,dtype=float)
    cursor=0
    for m in mats:
        n=m.shape[0]; out[cursor:cursor+n,cursor:cursor+n]=m; cursor+=n
    return out


@dataclass(frozen=True)
class FullPhaseFirstStructure:
    kappa: float
    metric_dimension: int
    information_generator_expectation: float
    semiclassical_phase_offset: Optional[float]
    free_phase_energy_expectation: Optional[float]
    status: str


def structure_receipt(
    W_expectation: float,
    delta_I0_expectation: float,
    metric_blocks: Sequence[np.ndarray],
    *,hbar: Optional[float]=None,delta_tau: Optional[float]=None,rho_s: Optional[float]=None,
) -> FullPhaseFirstStructure:
    G=block_diagonal_metric(*metric_blocks)
    I=information_generator_expectation(W_expectation,delta_I0_expectation)
    offset=None; energy=None
    supplied=[hbar is not None,delta_tau is not None,rho_s is not None]
    if any(supplied):
        if not all(supplied):
            raise ValueError("hbar, delta_tau and rho_s must be supplied together")
        offset=semiclassical_intention_charge(
            W_expectation,delta_I0_expectation,hbar=float(hbar),rho_s=float(rho_s)
        )
        energy=free_phase_hamiltonian_expectation(
            W_expectation,delta_I0_expectation,
            hbar=float(hbar),delta_tau=float(delta_tau),rho_s=float(rho_s),
        )
    return FullPhaseFirstStructure(
        KAPPA_INFORMATION,int(G.shape[0]),I,offset,energy,"SOURCE_DERIVED_STRUCTURE"
    )


__all__=[
    "KAPPA_INFORMATION","information_generator_expectation","semiclassical_intention_charge",
    "free_phase_hamiltonian_expectation","PhaseOffsetBinding","bind_phase_offset_to_information_generator",
    "build_canonical_state_with_information_offset","block_diagonal_metric",
    "FullPhaseFirstStructure","structure_receipt",
]
