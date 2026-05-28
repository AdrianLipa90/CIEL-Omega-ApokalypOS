"""Constraint definitions for the NOEMA Holonomic Doctor.

The constants here are not physical claims.  They are code-health analogues:

* ``D_lambda`` tracks slow global manifest drift between diagnostic cycles.
* ``epsilon_neutrino`` is the small local tolerance used when comparing
  phase-like closure scores across diagnostic flavours.

Values are derived from machine precision / observed manifest drift at runtime,
not treated as arbitrary project magic numbers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DoctorConstraint:
    """A named invariant checked by the doctor cycle."""

    name: str
    description: str
    severity: str = "medium"
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


DEFAULT_CONSTRAINTS: tuple[DoctorConstraint, ...] = (
    DoctorConstraint(
        name="no_inverted_rh_metric",
        description="R_H must be treated as lower-is-better holonomic defect; raw '1 - R_H' is suspicious unless explicitly bounded first.",
        severity="high",
    ),
    DoctorConstraint(
        name="no_dead_rh_helper",
        description="R_H helper/adapter modules should be imported by a runtime path or represented by an explicit patch candidate.",
        severity="medium",
    ),
    DoctorConstraint(
        name="append_only_reports",
        description="Doctor reports must be append-only; CURRENT files may point at latest report but must not erase history.",
        severity="high",
    ),
    DoctorConstraint(
        name="no_unproven_magic_constants",
        description="New numerical constants require provenance, derivation, or an explicit 'analogy/regulator' status.",
        severity="medium",
    ),
    DoctorConstraint(
        name="no_fake_source_claims",
        description="Diagnostics must distinguish NOEMA SoT, artifact-grounded evidence, proxy interpretation, and simulation.",
        severity="critical",
    ),
)


__all__ = ["DoctorConstraint", "DEFAULT_CONSTRAINTS"]
