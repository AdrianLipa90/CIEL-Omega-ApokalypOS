"""Epistemic/runtime contract for unresolved information-generator inputs.

Purpose
-------
The theory currently has asymmetric closure status:

- kappa = ln(2)/(24*pi): FROZEN / exact project constant.
- W_s = -i L_{V_s}: conditionally closed formal geometric generator.
- physical axis selection for V_s: supplied/model-dependent.
- rho_s(k): positive rhythm required, canonical law still OPEN.
- delta I_0(tau): fluctuation channel required/allowed, canonical law still OPEN.

This module prevents a reference rhythm, heuristic fluctuation, synthetic fixture,
or unproven axis selection from silently entering a production/canonical execution
as if it were promoted SoT.

It does not solve the open laws. It makes their epistemic state executable.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional
import math


class InputStatus(str, Enum):
    DERIVED = "DERIVED"
    SOURCE_DEFINED = "SOURCE_DEFINED"
    CALIBRATED = "CALIBRATED"
    MEASURED = "MEASURED"
    CONVENTIONAL = "CONVENTIONAL"
    HYPOTHESIS = "HYPOTHESIS"
    REFERENCE_RULE = "REFERENCE_RULE"
    TEST_FIXTURE = "TEST_FIXTURE"
    UNKNOWN = "UNKNOWN"


CANON_ADMISSIBLE = frozenset({
    InputStatus.DERIVED,
    InputStatus.SOURCE_DEFINED,
    InputStatus.CALIBRATED,
    InputStatus.MEASURED,
})


@dataclass(frozen=True)
class ProvenancedScalarInput:
    name: str
    value: float
    status: InputStatus
    provenance: str
    law_id: Optional[str] = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("input name required")
        if not math.isfinite(float(self.value)):
            raise ValueError(f"{self.name} must be finite")
        if not str(self.provenance).strip():
            raise ValueError(f"{self.name} provenance required")

    @property
    def canon_admissible(self) -> bool:
        return self.status in CANON_ADMISSIBLE


@dataclass(frozen=True)
class GeneratorInputContract:
    """All dynamic scalar inputs needed for a semiclassical generator step."""
    W_expectation: ProvenancedScalarInput
    rho_s: ProvenancedScalarInput
    delta_I0_expectation: ProvenancedScalarInput
    axis_provenance: str

    def __post_init__(self):
        if self.W_expectation.name != "W_expectation":
            raise ValueError("W input must be named W_expectation")
        if self.rho_s.name != "rho_s":
            raise ValueError("rhythm input must be named rho_s")
        if self.delta_I0_expectation.name != "delta_I0_expectation":
            raise ValueError("fluctuation input must be named delta_I0_expectation")
        if self.rho_s.value <= 0:
            raise ValueError("formal rhythm condition requires rho_s > 0")
        if not str(self.axis_provenance).strip():
            raise ValueError("axis provenance required")

    @property
    def unresolved_inputs(self) -> tuple[str,...]:
        rows=[]
        if not self.W_expectation.canon_admissible:
            rows.append("W_expectation")
        if not self.rho_s.canon_admissible:
            rows.append("rho_s")
        if not self.delta_I0_expectation.canon_admissible:
            rows.append("delta_I0_expectation")
        return tuple(rows)

    @property
    def canon_ready(self) -> bool:
        return len(self.unresolved_inputs) == 0


class CanonicalInputError(RuntimeError):
    pass


def assert_canonical_generator_inputs(contract: GeneratorInputContract) -> None:
    """Hard gate for production/canonical execution."""
    unresolved=contract.unresolved_inputs
    if unresolved:
        detail=", ".join(
            f"{name}={getattr(contract,name).status.value}"
            for name in unresolved
        )
        raise CanonicalInputError(
            "generator inputs are not canon-admissible: " + detail
        )


def reference_rhythm_input(value: float, provenance: str, *, law_id: str="REFERENCE_RHYTHM") -> ProvenancedScalarInput:
    """Explicitly noncanonical convenience constructor."""
    return ProvenancedScalarInput("rho_s",float(value),InputStatus.REFERENCE_RULE,provenance,law_id)


def open_fluctuation_input(value: float, provenance: str, *, law_id: str="OPEN_FLUCTUATION") -> ProvenancedScalarInput:
    """Explicitly hypothesis-level fluctuation; never silently promoted."""
    return ProvenancedScalarInput("delta_I0_expectation",float(value),InputStatus.HYPOTHESIS,provenance,law_id)


def derived_killing_expectation_input(value: float, provenance: str, *, law_id: str="W=-iL_V") -> ProvenancedScalarInput:
    return ProvenancedScalarInput("W_expectation",float(value),InputStatus.DERIVED,provenance,law_id)


@dataclass(frozen=True)
class GeneratorAdmissionReceipt:
    canon_ready: bool
    unresolved_inputs: tuple[str,...]
    statuses: tuple[tuple[str,str],...]
    decision: str


def admission_receipt(contract: GeneratorInputContract) -> GeneratorAdmissionReceipt:
    statuses=(
        ("W_expectation",contract.W_expectation.status.value),
        ("rho_s",contract.rho_s.status.value),
        ("delta_I0_expectation",contract.delta_I0_expectation.status.value),
    )
    ready=contract.canon_ready
    return GeneratorAdmissionReceipt(
        canon_ready=ready,
        unresolved_inputs=contract.unresolved_inputs,
        statuses=statuses,
        decision="CANON_EXECUTION_ALLOWED" if ready else "EXPERIMENTAL_ONLY__CANON_BLOCKED",
    )


__all__=[
    "InputStatus","CANON_ADMISSIBLE","ProvenancedScalarInput",
    "GeneratorInputContract","CanonicalInputError","assert_canonical_generator_inputs",
    "reference_rhythm_input","open_fluctuation_input","derived_killing_expectation_input",
    "GeneratorAdmissionReceipt","admission_receipt",
]
