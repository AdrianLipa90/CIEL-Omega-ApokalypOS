"""End-to-end noncanonical information-dynamics reference harness.

This harness intentionally combines only already identified pieces:

1. twin-prime paired Collatz state;
2. Hilbert-Kahler eq.56 reference rhythm (REFERENCE_RULE);
3. formal Bloch Killing W_s expectation (DERIVED, axis provenance supplied);
4. explicit zero-level fluctuation hypothesis (HYPOTHESIS unless caller has a
   stronger provenance-bearing law);
5. source-derived semiclassical phase offset.

The harness is for falsification/experiments. It is structurally unable to claim
canonical readiness while the reference rhythm or open fluctuation law is used.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .killing_information_generator import killing_expectation
from .reference_collatz_rhythm import reference_rhythm_receipt, reference_rhythm_contract_input
from .generator_input_contract import (
    GeneratorInputContract, derived_killing_expectation_input, open_fluctuation_input,
    admission_receipt,
)
from .information_phase_generator import bind_phase_offset_from_contract


@dataclass(frozen=True)
class ReferenceInformationStep:
    seed: tuple[int,int]
    k: int
    paired_state: tuple[int,int]
    rho_s: float
    W_expectation: float
    delta_I0_expectation: float
    information_generator_expectation: float
    intention_phase_increment: float
    J0_phase_offset: float
    admission_decision: str
    canon_ready: bool
    status: str


def run_reference_information_step(
    *,
    seed_p: int,
    k: int,
    coefficients: Sequence[complex],
    mode_indices: Sequence[int],
    delta_I0_expectation: float,
    hbar: float,
    axis_provenance: str,
    fluctuation_provenance: str="OPEN_ZERO_LEVEL_FLUCTUATION_HYPOTHESIS",
) -> ReferenceInformationStep:
    rr=reference_rhythm_receipt(seed_p,k)
    Wexp=killing_expectation(coefficients,mode_indices)
    contract=GeneratorInputContract(
        W_expectation=derived_killing_expectation_input(
            Wexp,f"W_s=-iL_V; axis={axis_provenance}"
        ),
        rho_s=reference_rhythm_contract_input(seed_p,k),
        delta_I0_expectation=open_fluctuation_input(
            float(delta_I0_expectation),str(fluctuation_provenance)
        ),
        axis_provenance=str(axis_provenance),
    )
    binding,admission=bind_phase_offset_from_contract(
        contract,hbar=float(hbar),require_canonical=False
    )
    theta_increment=float(contract.rho_s.value*binding.I_expectation)
    return ReferenceInformationStep(
        seed=rr.seed,k=rr.k,paired_state=rr.paired_state,rho_s=rr.rho_s,
        W_expectation=Wexp,delta_I0_expectation=float(delta_I0_expectation),
        information_generator_expectation=binding.I_expectation,
        intention_phase_increment=theta_increment,
        J0_phase_offset=binding.J0_phase_offset,
        admission_decision=admission.decision,
        canon_ready=admission.canon_ready,
        status="REFERENCE_EXPERIMENT_EXECUTABLE__CANON_BLOCKED",
    )


__all__=["ReferenceInformationStep","run_reference_information_step"]
