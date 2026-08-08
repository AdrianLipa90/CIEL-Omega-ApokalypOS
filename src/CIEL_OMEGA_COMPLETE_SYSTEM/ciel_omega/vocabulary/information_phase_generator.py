"""
CIEL / TIR — Intention/Information Phase Generator v4

Quantized generator:
    I_hat_s = kappa W_hat_s + delta I_hat_0
    kappa = ln(2)/(24*pi)

Formal semiclassical phase offset:
    J0_phase_offset = hbar rho_s [kappa <W_s> + <delta I_0>].

v4 adds an executable epistemic admission gate. The source-derived Killing W_s
may be used directly, while rho_s and delta I_0 keep their actual provenance
status. Canonical execution is refused unless every input is canon-admissible.
Experimental execution remains possible and returns its explicit receipt.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional, Sequence
import numpy as np

KAPPA_INFORMATION=math.log(2.0)/(24.0*math.pi)


def information_generator_expectation(W_expectation: float,delta_I0_expectation: float,*,kappa: float=KAPPA_INFORMATION) -> float:
    return float(kappa)*float(W_expectation)+float(delta_I0_expectation)


def generator_expectation_from_killing_state(coefficients: Sequence[complex],mode_indices: Sequence[int],delta_I0_expectation: float,*,kappa: float=KAPPA_INFORMATION) -> float:
    from .killing_information_generator import killing_expectation
    return information_generator_expectation(killing_expectation(coefficients,mode_indices),delta_I0_expectation,kappa=kappa)


def semiclassical_intention_charge(W_expectation: float,delta_I0_expectation: float,*,hbar: float,rho_s: float,kappa: float=KAPPA_INFORMATION) -> float:
    I=information_generator_expectation(W_expectation,delta_I0_expectation,kappa=kappa)
    return float(hbar)*float(rho_s)*I


def free_phase_hamiltonian_expectation(W_expectation: float,delta_I0_expectation: float,*,hbar: float,delta_tau: float,rho_s: float,kappa: float=KAPPA_INFORMATION) -> float:
    if delta_tau<=0: raise ValueError("delta_tau must be positive")
    return semiclassical_intention_charge(W_expectation,delta_I0_expectation,hbar=hbar,rho_s=rho_s,kappa=kappa)/float(delta_tau)


@dataclass(frozen=True)
class PhaseOffsetBinding:
    J0_phase_offset: float
    I_expectation: float
    hbar: float
    rho_s: float
    W_expectation: float
    W_status: str
    rho_status: str
    fluctuation_status: str
    status: str
    provenance: str

    @property
    def source_identity_residual(self) -> float:
        return float(self.J0_phase_offset-self.hbar*self.rho_s*self.I_expectation)


def bind_phase_offset_to_information_generator(
    W_expectation: float,delta_I0_expectation: float,*,hbar: float,rho_s: float,provenance: str,
    W_status: str="SUPPLIED_EXPECTATION",rho_status: str="SUPPLIED_RHYTHM__CANONICAL_LAW_OPEN",
    fluctuation_status: str="SUPPLIED_FLUCTUATION__LAW_OPEN",
) -> PhaseOffsetBinding:
    I=information_generator_expectation(W_expectation,delta_I0_expectation)
    JI=semiclassical_intention_charge(W_expectation,delta_I0_expectation,hbar=hbar,rho_s=rho_s)
    return PhaseOffsetBinding(JI,I,float(hbar),float(rho_s),float(W_expectation),str(W_status),str(rho_status),str(fluctuation_status),"SOURCE_DERIVED_SEMICLASSICAL_PHASE_OFFSET",str(provenance))


def bind_phase_offset_from_killing_state(coefficients: Sequence[complex],mode_indices: Sequence[int],delta_I0_expectation: float,*,hbar: float,rho_s: float,axis_provenance: str) -> PhaseOffsetBinding:
    from .killing_information_generator import killing_expectation
    Wexp=killing_expectation(coefficients,mode_indices)
    return bind_phase_offset_to_information_generator(
        Wexp,delta_I0_expectation,hbar=hbar,rho_s=rho_s,
        provenance=f"W_s=-iL_V; axis={axis_provenance}",
        W_status="CONDITIONALLY_CLOSED_KILLING_GENERATOR_EXPECTATION",
        rho_status="SUPPLIED_RHYTHM__CANONICAL_LAW_OPEN",
        fluctuation_status="SUPPLIED_FLUCTUATION__LAW_OPEN",
    )


def bind_phase_offset_from_contract(contract,*,hbar: float,require_canonical: bool=False) -> tuple[PhaseOffsetBinding,object]:
    """Execute the generator through GeneratorInputContract.

    If require_canonical=True, unresolved/reference/hypothesis inputs raise a
    CanonicalInputError before the phase offset is evaluated.
    """
    from .generator_input_contract import (
        GeneratorInputContract,assert_canonical_generator_inputs,admission_receipt
    )
    if not isinstance(contract,GeneratorInputContract):
        raise TypeError("contract must be GeneratorInputContract")
    receipt=admission_receipt(contract)
    if require_canonical:
        assert_canonical_generator_inputs(contract)
    b=bind_phase_offset_to_information_generator(
        contract.W_expectation.value,
        contract.delta_I0_expectation.value,
        hbar=float(hbar),rho_s=contract.rho_s.value,
        provenance="; ".join([
            f"W:{contract.W_expectation.provenance}",
            f"rho:{contract.rho_s.provenance}",
            f"deltaI0:{contract.delta_I0_expectation.provenance}",
            f"axis:{contract.axis_provenance}",
        ]),
        W_status=contract.W_expectation.status.value,
        rho_status=contract.rho_s.status.value,
        fluctuation_status=contract.delta_I0_expectation.status.value,
    )
    return b,receipt


def build_canonical_state_with_information_offset(q: np.ndarray,p: np.ndarray,*,J: float,I_phi: float,W_expectation: float,delta_I0_expectation: float,hbar: float,rho_s: float,provenance: str):
    from .canonical_information_backreaction import CanonicalRelationalState
    binding=bind_phase_offset_to_information_generator(W_expectation,delta_I0_expectation,hbar=hbar,rho_s=rho_s,provenance=provenance)
    state=CanonicalRelationalState(np.asarray(q,dtype=float),np.asarray(p,dtype=float),float(J),binding.J0_phase_offset,float(I_phi))
    return state,binding


def block_diagonal_metric(*blocks: np.ndarray) -> np.ndarray:
    if not blocks: return np.zeros((0,0),dtype=float)
    mats=[]
    for b in blocks:
        a=np.asarray(b,dtype=float)
        if a.ndim!=2 or a.shape[0]!=a.shape[1]: raise ValueError("metric blocks must be square")
        if not np.allclose(a,a.T,atol=1e-14,rtol=0.0): raise ValueError("metric blocks must be symmetric")
        mats.append(a)
    out=np.zeros((sum(m.shape[0] for m in mats),)*2,dtype=float); cursor=0
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


def structure_receipt(W_expectation: float,delta_I0_expectation: float,metric_blocks: Sequence[np.ndarray],*,hbar: Optional[float]=None,delta_tau: Optional[float]=None,rho_s: Optional[float]=None) -> FullPhaseFirstStructure:
    G=block_diagonal_metric(*metric_blocks)
    I=information_generator_expectation(W_expectation,delta_I0_expectation)
    offset=None; energy=None
    supplied=[hbar is not None,delta_tau is not None,rho_s is not None]
    if any(supplied):
        if not all(supplied): raise ValueError("hbar, delta_tau and rho_s must be supplied together")
        offset=semiclassical_intention_charge(W_expectation,delta_I0_expectation,hbar=float(hbar),rho_s=float(rho_s))
        energy=free_phase_hamiltonian_expectation(W_expectation,delta_I0_expectation,hbar=float(hbar),delta_tau=float(delta_tau),rho_s=float(rho_s))
    return FullPhaseFirstStructure(KAPPA_INFORMATION,int(G.shape[0]),I,offset,energy,"SOURCE_DERIVED_STRUCTURE")


__all__=[
    "KAPPA_INFORMATION","information_generator_expectation","generator_expectation_from_killing_state",
    "semiclassical_intention_charge","free_phase_hamiltonian_expectation",
    "PhaseOffsetBinding","bind_phase_offset_to_information_generator","bind_phase_offset_from_killing_state",
    "bind_phase_offset_from_contract","build_canonical_state_with_information_offset",
    "block_diagonal_metric","FullPhaseFirstStructure","structure_receipt",
]
