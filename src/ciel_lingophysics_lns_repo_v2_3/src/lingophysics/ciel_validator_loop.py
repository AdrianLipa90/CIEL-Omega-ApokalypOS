from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set


@dataclass(frozen=True)
class ValidationResult:
    accepted: bool
    status: str
    missing_expectations: tuple[str, ...]
    notes: tuple[str, ...]


def validate_expectations(expected: Iterable[str], observed: Iterable[str]) -> ValidationResult:
    expected_set: Set[str] = set(expected)
    observed_set: Set[str] = set(observed)
    missing = tuple(sorted(expected_set - observed_set))
    if missing:
        return ValidationResult(False, "REJECT_OR_REPAIR", missing, ("Some CIEL invariants were not preserved.",))
    return ValidationResult(True, "ACCEPT", (), ("All declared CIEL invariants were preserved.",))


def validate_output_against_tensor(tensor: Dict, observed_invariants: Iterable[str]) -> ValidationResult:
    return validate_expectations(tensor.get("validator_expectations", []), observed_invariants)


def repair_plan(result: ValidationResult) -> List[str]:
    if result.accepted:
        return []
    return [f"repair:{x}" for x in result.missing_expectations]
