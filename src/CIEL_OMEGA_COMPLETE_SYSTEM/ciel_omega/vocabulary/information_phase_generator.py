"""
CIEL / TIR — Intention/Information Phase Generator v1

Source parent: Hilbert_Kahler_Phase_Intention_Hamiltonian, eqs. (71)-(76).

The classical bare phase rotor momentum J is replaced in the quantized
phase-first sector by the intention/information generator

    I_hat_s(tau,k) = kappa W_hat_s + delta I_hat_0(tau,k)

with

    kappa = ln(2)/(24*pi).

The free phase Hamiltonian is

    H_phase/free = (hbar / Delta tau_k) rho_s(k)
                   [kappa W_hat_s + delta I_hat_0(tau,k)].

The full kinetic block uses

    G = g_FS direct_sum g_D direct_sum g_rel

and the covariant momentum

    Pi_A = -i hbar nabla_A - hbar A_ABE_A - lambda_s(k) I_A.

This module implements the coefficient/expectation bookkeeping only. It does
not invent W, delta I0, rho_s, lambda_s, metric tensors, or connections.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Optional, Sequence, Tuple
import numpy as np

KAPPA_INFORMATION = math.log(2.0)/(24.0*math.pi)


def information_generator_expectation(
    W_expectation: float,
    delta_I0_expectation: float,
    *,
    kappa: float = KAPPA_INFORMATION,
) -> float:
    """<I_s> = kappa <W_s> + <delta I_0>."""
    return float(kappa)*float(W_expectation)+float(delta_I0_expectation)


def free_phase_hamiltonian_expectation(
    W_expectation: float,
    delta_I0_expectation: float,
    *,
    hbar: float,
    delta_tau: float,
    rho_s: float,
    kappa: float = KAPPA_INFORMATION,
) -> float:
    """Expectation of eq. (73), with all non-kappa quantities supplied."""
    if delta_tau <= 0:
        raise ValueError("delta_tau must be positive")
    I=information_generator_expectation(W_expectation,delta_I0_expectation,kappa=kappa)
    return float(hbar/delta_tau * rho_s * I)


@dataclass(frozen=True)
class PhaseGeneratorBinding:
    """
    Explicit classical/quantum bridge receipt.

    J_classical:
        canonical phase momentum used by the classical Hamiltonian sector.
    I_expectation:
        expectation value of the quantized intention/information generator.
    status:
        states whether equality is asserted by the caller or remains a candidate
        semiclassical identification.
    """
    J_classical: float
    I_expectation: float
    status: str
    provenance: str

    @property
    def residual(self) -> float:
        return float(self.J_classical-self.I_expectation)


def bind_classical_J_to_information_generator(
    J_classical: float,
    W_expectation: float,
    delta_I0_expectation: float,
    *,
    provenance: str,
    assert_semiclassical_identification: bool=False,
) -> PhaseGeneratorBinding:
    I=information_generator_expectation(W_expectation,delta_I0_expectation)
    status=(
        "SEMICLASSICAL_IDENTIFICATION_ASSERTED"
        if assert_semiclassical_identification
        else "CANDIDATE_CLASSICAL_QUANTUM_BINDING"
    )
    return PhaseGeneratorBinding(float(J_classical),I,status,str(provenance))


def block_diagonal_metric(*blocks: np.ndarray) -> np.ndarray:
    """
    Construct G = g_FS direct_sum g_D direct_sum g_rel from supplied blocks.

    This is structural composition only; the metric components are not invented.
    """
    if not blocks:
        return np.zeros((0,0),dtype=float)
    mats=[]
    for b in blocks:
        a=np.asarray(b,dtype=float)
        if a.ndim!=2 or a.shape[0]!=a.shape[1]:
            raise ValueError("metric blocks must be square")
        if not np.allclose(a,a.T,atol=1e-14,rtol=0.0):
            raise ValueError("metric blocks must be symmetric")
        mats.append(a)
    sizes=[m.shape[0] for m in mats]
    out=np.zeros((sum(sizes),sum(sizes)),dtype=float)
    cursor=0
    for m in mats:
        n=m.shape[0]
        out[cursor:cursor+n,cursor:cursor+n]=m
        cursor+=n
    return out


@dataclass(frozen=True)
class FullPhaseFirstStructure:
    kappa: float
    metric_dimension: int
    information_generator_expectation: float
    free_phase_energy_expectation: Optional[float]
    status: str


def structure_receipt(
    W_expectation: float,
    delta_I0_expectation: float,
    metric_blocks: Sequence[np.ndarray],
    *,
    hbar: Optional[float]=None,
    delta_tau: Optional[float]=None,
    rho_s: Optional[float]=None,
) -> FullPhaseFirstStructure:
    G=block_diagonal_metric(*metric_blocks)
    I=information_generator_expectation(W_expectation,delta_I0_expectation)
    energy=None
    if hbar is not None or delta_tau is not None or rho_s is not None:
        if hbar is None or delta_tau is None or rho_s is None:
            raise ValueError("hbar, delta_tau and rho_s must be supplied together")
        energy=free_phase_hamiltonian_expectation(
            W_expectation,delta_I0_expectation,
            hbar=hbar,delta_tau=delta_tau,rho_s=rho_s,
        )
    return FullPhaseFirstStructure(
        kappa=KAPPA_INFORMATION,
        metric_dimension=int(G.shape[0]),
        information_generator_expectation=I,
        free_phase_energy_expectation=energy,
        status="SOURCE_DERIVED_STRUCTURE",
    )


__all__=[
    "KAPPA_INFORMATION",
    "information_generator_expectation",
    "free_phase_hamiltonian_expectation",
    "PhaseGeneratorBinding","bind_classical_J_to_information_generator",
    "block_diagonal_metric","FullPhaseFirstStructure","structure_receipt",
]
