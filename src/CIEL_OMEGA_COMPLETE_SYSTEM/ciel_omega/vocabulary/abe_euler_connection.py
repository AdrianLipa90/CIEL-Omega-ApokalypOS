"""Source-derived Aharonov–Bohm–Berry–Euler phase connection.

Parents: Phase_Intention_Hamiltonian_Formal_Derivations, eqs. (7)-(15), (29)-(38), (62).

The source defines
    A_ABE = A_AB + A_B + A_E,
    A_AB = (q_e/hbar) A_em,
    A_B  = i<u|du>,
    A_E  = s_E omega_E, with s_E=1/2 in the spin-half sector.

The intention trace I_a in the covariant quantum momentum is kept separate:
    Pi_a = -i hbar nabla_a - hbar alpha_s A_ABE,a - lambda_s I_a.

No electromagnetic potential, Euler connection, intention trace, alpha_s or
lambda_s is invented by this module; callers must supply them with provenance.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Sequence
import math
import numpy as np

SPIN_HALF = 0.5
TWO_PI = 2.0 * math.pi


def aharonov_bohm_connection(A_em: Sequence[float], *, q_e: float, hbar: float) -> np.ndarray:
    if hbar == 0:
        raise ValueError("hbar must be nonzero")
    return (float(q_e)/float(hbar))*np.asarray(A_em,dtype=float)


def euler_connection(omega_e: Sequence[float], *, spin: float=SPIN_HALF) -> np.ndarray:
    return float(spin)*np.asarray(omega_e,dtype=float)


def total_abe_connection(
    A_ab: Sequence[float],
    A_berry: Sequence[float],
    A_euler: Sequence[float],
) -> np.ndarray:
    ab=np.asarray(A_ab,dtype=float); b=np.asarray(A_berry,dtype=float); e=np.asarray(A_euler,dtype=float)
    if ab.shape != b.shape or ab.shape != e.shape:
        raise ValueError("ABE connection components must have equal shape")
    return ab+b+e


def berry_euler_curvature(F_berry: np.ndarray, R_euler: np.ndarray, *, spin: float=SPIN_HALF) -> np.ndarray:
    fb=np.asarray(F_berry,dtype=float); re=np.asarray(R_euler,dtype=float)
    if fb.shape != re.shape:
        raise ValueError("curvature shapes must match")
    return fb+float(spin)*re


def phase_holonomy(phi_ab: float, phi_berry: float, phi_euler: float) -> complex:
    phi=float(phi_ab)+float(phi_berry)+float(phi_euler)
    return complex(math.cos(phi),math.sin(phi))


def closure_defect(
    *,
    phi_ab: float,
    phi_berry: float,
    euler_curvature_integral: float,
    theta_information: float,
    D: int,
    spin: float=SPIN_HALF,
) -> float:
    """epsilon_EB = [Phi_AB + Phi_B + s_E int R_E + Theta_I]/2pi - D."""
    total=(float(phi_ab)+float(phi_berry)+float(spin)*float(euler_curvature_integral)+float(theta_information))
    return float(total/TWO_PI-int(D))


def exact_closure(*, defect: float) -> bool:
    """Exact mathematical closure only; no arbitrary tolerance."""
    return float(defect) == 0.0


def empirical_closure(*, defect: float, epsilon_star: Optional[float]) -> Optional[bool]:
    """Tolerance is caller-supplied/calibrated; None => UNKNOWN."""
    if epsilon_star is None:
        return None
    if epsilon_star < 0:
        raise ValueError("epsilon_star must be nonnegative")
    return abs(float(defect)) <= float(epsilon_star)


def covariant_quantum_momentum_terms(
    *,
    hbar: float,
    alpha_s: float,
    A_abe: Sequence[float],
    lambda_s: float,
    intention_trace: Sequence[float],
) -> tuple[np.ndarray,np.ndarray]:
    """Return the source connection term and intention-trace term separately."""
    a=np.asarray(A_abe,dtype=float); i=np.asarray(intention_trace,dtype=float)
    if a.shape != i.shape:
        raise ValueError("A_abe and intention_trace must have equal shape")
    return -float(hbar)*float(alpha_s)*a, -float(lambda_s)*i


@dataclass(frozen=True)
class ABEReceipt:
    dimension: int
    spin: float
    closure_defect: float
    exact_closed: bool
    empirical_closed: Optional[bool]
    status: str


def abe_receipt(
    A_abe: Sequence[float],
    *,
    phi_ab: float,
    phi_berry: float,
    euler_curvature_integral: float,
    theta_information: float,
    D: int,
    spin: float=SPIN_HALF,
    epsilon_star: Optional[float]=None,
) -> ABEReceipt:
    a=np.asarray(A_abe,dtype=float)
    if a.ndim != 1:
        raise ValueError("A_abe must be a 1D covector")
    eps=closure_defect(phi_ab=phi_ab,phi_berry=phi_berry,euler_curvature_integral=euler_curvature_integral,theta_information=theta_information,D=D,spin=spin)
    return ABEReceipt(int(a.size),float(spin),eps,exact_closure(defect=eps),empirical_closure(defect=eps,epsilon_star=epsilon_star),"SOURCE_DERIVED_ABE_STRUCTURE")


__all__=[
    "SPIN_HALF","aharonov_bohm_connection","euler_connection","total_abe_connection",
    "berry_euler_curvature","phase_holonomy","closure_defect","exact_closure","empirical_closure",
    "covariant_quantum_momentum_terms","ABEReceipt","abe_receipt",
]
