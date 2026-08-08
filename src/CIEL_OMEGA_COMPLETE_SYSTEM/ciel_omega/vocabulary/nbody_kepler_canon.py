"""
Canonical epistemic registry for N-body relational Green/Kepler dynamics.

Do not collapse:
CONDITIONAL_EXACT != OPEN_FIRST_PRINCIPLES != USER_PREDICTION_UNTESTED.
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

DIM_GREEN = CanonNode(
    "NBK-DIM-GREEN-FAMILY",
    "PROMOTED_SoT_CONDITIONAL_EXACT",
    "N=2: V~log r; N>2: V~-1/((N-2)r^(N-2)); |F|~r^(1-N)",
    ("isotropic conserved radial flux","intrinsic dimension N>=2"),
)

N3_KEPLER = CanonNode(
    "NBK-N3-KEPLER-SECTOR",
    "PROMOTED_SoT_CONDITIONAL_EXACT",
    "N=3 => V=-mu/r and |F|=mu/r^2",
    ("NBK-DIM-GREEN-FAMILY","intrinsic_dimension=3"),
)

TIR_FLUX_BINDING = CanonNode(
    "NBK-TIR-TO-RADIAL-FLUX",
    "OPEN_FIRST_PRINCIPLES",
    "TIR relational/information flow -> conserved isotropic radial flux on intrinsic B3",
    ("TIR relational action/potential","B3 geometry bridge","continuity/conservation law"),
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

CANON_NODES=(DIM_GREEN,N3_KEPLER,TIR_FLUX_BINDING,USER_DELTA,USER_SIGMA)
