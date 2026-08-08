"""Canonical epistemic registry for N-body relational Green/Kepler dynamics.

Current correction incorporates the preregistered direct-derivation receipt:
- the local canonical TIR action is quadratic near coherent overlap;
- simple reciprocal overlap 1/z is also locally quadratic;
- neither directly yields a Kepler 1/r singularity.

The valid Kepler result is instead a conditional Green/Gauss theorem on the
source-supported Euclidean B3 radial sector. The missing edge is the field lift
from finite-dimensional conserved phase charge to a local conserved B3 current.
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

TIR_FIELD_LIFT = CanonNode(
    "NBK-TIR-FIELD-LIFT",
    "OPEN_FIRST_PRINCIPLES",
    "Derive/validate the lift of finite-dimensional conserved J to a local conserved current J^mu on the B3 sector.",
    ("NBK-FINITE-PHASE-CHARGE","NBK-B3-RADIAL-OBSERVABLE"),
)

TIR_FLUX_BINDING = CanonNode(
    "NBK-TIR-TO-RADIAL-FLUX",
    "OPEN_FACTORIZED",
    "TIR->Kepler is not a direct local-action map; it requires the open J->J^mu field lift plus a static centered isotropic-current condition.",
    ("NBK-TIR-FIELD-LIFT","NBK-N3-KEPLER-SECTOR"),
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
    B3_RADIAL_OBSERVABLE,FINITE_PHASE_CHARGE,TIR_FIELD_LIFT,TIR_FLUX_BINDING,
    USER_DELTA,USER_SIGMA,
)
