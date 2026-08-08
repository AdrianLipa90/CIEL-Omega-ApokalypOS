"""Canonical epistemic registry for N-body relational Green/Kepler dynamics.

The registry preserves both positive derivations and falsification receipts.
Direct local TIR does not yield 1/r; the Kepler sector is a separate conditional
B3 Green/Gauss path. A constructive constant-modulus rotor embedding closes one
explicit local Noether-current lift, while a unique/general physical field lift
remains open.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class CanonNode:
    id: str
    status: str
    statement: str
    parents: Tuple[str,...]

DIRECT_TIR_LOCAL = CanonNode(
    "NBK-DIRECT-TIR-LOCAL",
    "TESTED_FAIL_FOR_INVERSE_DISTANCE__PASS_QUADRATIC_LOCAL",
    "Canonical local TIR action scales as relational distance squared near coherent overlap; direct 1/r derivation fails.",
    ("TIR_KEPLER_DIRECT_DERIVATION_TEST_V0_1",),
)

RECIPROCAL_OVERLAP = CanonNode(
    "NBK-RECIPROCAL-OVERLAP",
    "TESTED_FAIL_FOR_INVERSE_DISTANCE",
    "Near z≈1, |1/z|-1 remains analytic/quadratic and does not generate a 1/r singularity.",
    ("TIR_KEPLER_DIRECT_DERIVATION_TEST_V0_1",),
)

DIM_GREEN = CanonNode(
    "NBK-DIM-GREEN-FAMILY",
    "PROMOTED_SoT_CONDITIONAL_EXACT",
    "Under isotropic conserved radial flux: N=2 gives V~log r; N>2 gives V~-1/((N-2)r^(N-2)), |F|~r^(1-N).",
    ("isotropic conserved radial flux","intrinsic dimension N>=2"),
)

N3_KEPLER = CanonNode(
    "NBK-N3-KEPLER-SECTOR",
    "PROMOTED_SoT_CONDITIONAL_EXACT",
    "On the centered Euclidean B3 radial Green sector, V=-mu/r + const and |F|=mu/r^2.",
    ("NBK-DIM-GREEN-FAMILY","intrinsic_dimension=3","centered isotropic conserved flux"),
)

B3_RADIAL_OBSERVABLE = CanonNode(
    "NBK-B3-RADIAL-OBSERVABLE",
    "SOURCE_SUPPORTED_GEOMETRIC",
    "The project B3 geometry supplies rho_TIR=||r|| as a non-fitted radial observable.",
    ("TIR_KEPLER_B3_GREEN_BRIDGE_V0_3","project tetrahedral depth B3"),
)

FINITE_PHASE_CHARGE = CanonNode(
    "NBK-FINITE-PHASE-CHARGE",
    "SOURCE_SUPPORTED_CONSERVED_CONDITIONAL",
    "Cyclic chi gives conserved finite-dimensional phase momentum J when the Lagrangian has no explicit chi dependence.",
    ("Phase-Intention Hamiltonian rotor embedding","U(1) phase symmetry"),
)

EMBEDDED_FIELD_LIFT = CanonNode(
    "NBK-EMBEDDED-FIELD-LIFT",
    "CONSTRUCTIVE_EMBEDDED_SECTOR_EXACT",
    "The explicit embedding psi=sqrt(I_phi/2) exp(i chi) yields local Noether current J^mu=I_phi D^mu chi in the constant-modulus sector.",
    ("NBK-FINITE-PHASE-CHARGE","TIR_KEPLER_NOETHER_PHASE_BINDING_V0_4","N-Body Kepler Canon v4"),
)

GENERAL_FIELD_LIFT = CanonNode(
    "NBK-GENERAL-FIELD-LIFT",
    "OPEN_NOT_UNIQUE_NOT_VALIDATED",
    "No theorem yet establishes that every finite-dimensional relational state uniquely induces the constructed local B3 field/current.",
    ("NBK-FINITE-PHASE-CHARGE","NBK-B3-RADIAL-OBSERVABLE","NBK-EMBEDDED-FIELD-LIFT"),
)

TIR_FLUX_BINDING = CanonNode(
    "NBK-TIR-TO-RADIAL-FLUX",
    "PARTIAL_CONSTRUCTIVE__GENERAL_OPEN",
    "Inside the constructed constant-modulus field sector, a static centered radial conserved current gives the exact B3 1/r profile; general physical field selection/radiality remains open.",
    ("NBK-EMBEDDED-FIELD-LIFT","NBK-N3-KEPLER-SECTOR","NBK-GENERAL-FIELD-LIFT"),
)

USER_DELTA = CanonNode(
    "NBK-USER-PRED-DELTA",
    "USER_PREDICTION_UNTESTED",
    "relative delta ~ 1e-3",
    ("user preregistration",),
)

USER_SIGMA = CanonNode(
    "NBK-USER-PRED-SIGMA",
    "USER_PREDICTION_UNTESTED",
    "significance ~ 6.3 sigma",
    ("user preregistration","future declared noise model"),
)

CANON_NODES=(
    DIRECT_TIR_LOCAL,RECIPROCAL_OVERLAP,DIM_GREEN,N3_KEPLER,
    B3_RADIAL_OBSERVABLE,FINITE_PHASE_CHARGE,EMBEDDED_FIELD_LIFT,GENERAL_FIELD_LIFT,
    TIR_FLUX_BINDING,USER_DELTA,USER_SIGMA,
)
