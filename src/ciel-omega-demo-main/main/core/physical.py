from __future__ import annotations

from dataclasses import dataclass
from .ciel_constants import DEFAULT_CONSTANTS

@dataclass(frozen=True)
class PhysicalConstants:
    c: float = DEFAULT_CONSTANTS.c
    hbar: float = DEFAULT_CONSTANTS.hbar
    mu0: float = DEFAULT_CONSTANTS.mu0
    eps0: float = DEFAULT_CONSTANTS.eps0
    G: float = DEFAULT_CONSTANTS.G
    k_B: float = DEFAULT_CONSTANTS.k_B
    Lp: float = DEFAULT_CONSTANTS.Lp
    tp: float = DEFAULT_CONSTANTS.tp
    mp: float = DEFAULT_CONSTANTS.mp

C = DEFAULT_CONSTANTS.c
HBAR = DEFAULT_CONSTANTS.hbar
MU0 = DEFAULT_CONSTANTS.mu0
EPS0 = DEFAULT_CONSTANTS.eps0
G = DEFAULT_CONSTANTS.G
K_B = DEFAULT_CONSTANTS.k_B
LP = DEFAULT_CONSTANTS.Lp
TP = DEFAULT_CONSTANTS.tp
MP = DEFAULT_CONSTANTS.mp
