"""Local relational information metric derived from the TIR overlap action.

Parent receipt: TIR_KEPLER_DIRECT_DERIVATION_TEST_V0_1.

For d phase coordinates with
    z(delta) = (1/d) sum_j exp(i delta_j),
    R = |z|^2,
    S_rel = -kappa log R,

the coherent point delta=0 has quadratic expansion
    S_rel = kappa[(1/d) sum_j delta_j^2 - (1/d^2)(sum_j delta_j)^2] + O(delta^3/4)
          = 1/2 delta^T g_rel delta + higher order,
with
    g_rel = (2 kappa/d) [I - (1/d) 11^T].

The all-ones direction is the global U(1) phase zero mode. Therefore g_rel is
positive semidefinite in the ambient coordinates and positive definite on the
horizontal/quotient subspace sum_j delta_j=0.

This module does not turn the quadratic local action into a Kepler potential;
it records the opposite: the direct local TIR sector is harmonic/quadratic.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

KAPPA_INFORMATION = math.log(2.0)/(24.0*math.pi)


def global_phase_projector(d: int) -> np.ndarray:
    d=int(d)
    if d < 2:
        raise ValueError("d must be >=2")
    one=np.ones((d,1),dtype=float)
    return np.eye(d)-one@one.T/d


def local_relational_metric(d: int, *, kappa: float=KAPPA_INFORMATION) -> np.ndarray:
    d=int(d)
    if kappa <= 0:
        raise ValueError("kappa must be positive")
    return (2.0*float(kappa)/d)*global_phase_projector(d)


def local_relational_metric_pseudoinverse(d: int, *, kappa: float=KAPPA_INFORMATION) -> np.ndarray:
    """Moore-Penrose inverse; exact inverse on the horizontal quotient subspace."""
    d=int(d)
    return (d/(2.0*float(kappa)))*global_phase_projector(d)


def horizontalize(delta: np.ndarray) -> np.ndarray:
    x=np.asarray(delta,dtype=float).ravel()
    if x.size < 2:
        raise ValueError("delta must have at least two components")
    return global_phase_projector(x.size)@x


def quadratic_action(delta: np.ndarray, *, kappa: float=KAPPA_INFORMATION) -> float:
    x=np.asarray(delta,dtype=float).ravel()
    g=local_relational_metric(x.size,kappa=kappa)
    return float(0.5*x@g@x)


def exact_overlap_action(delta: np.ndarray, *, kappa: float=KAPPA_INFORMATION) -> float:
    x=np.asarray(delta,dtype=float).ravel()
    if x.size < 2:
        raise ValueError("delta must have at least two components")
    z=np.mean(np.exp(1j*x))
    R=float(abs(z)**2)
    if R <= 0.0:
        return math.inf
    return float(-float(kappa)*math.log(R))


def single_coordinate_quadratic_coefficient(d: int, *, kappa: float=KAPPA_INFORMATION) -> float:
    d=int(d)
    if d < 2:
        raise ValueError
    return float(kappa)*(d-1)/(d*d)


@dataclass(frozen=True)
class RelationalMetricReceipt:
    dimension: int
    rank: int
    nullity: int
    nonzero_eigenvalue: float
    single_coordinate_coefficient: float
    status: str
    kepler_direct_status: str


def metric_receipt(d: int=36, *, kappa: float=KAPPA_INFORMATION) -> RelationalMetricReceipt:
    g=local_relational_metric(d,kappa=kappa)
    rank=int(np.linalg.matrix_rank(g,tol=1e-13))
    return RelationalMetricReceipt(
        dimension=int(d),
        rank=rank,
        nullity=int(d-rank),
        nonzero_eigenvalue=float(2.0*float(kappa)/int(d)),
        single_coordinate_coefficient=single_coordinate_quadratic_coefficient(d,kappa=kappa),
        status="DERIVED_LOCAL_HESSIAN_METRIC_ON_PHASE_QUOTIENT",
        kepler_direct_status="FAIL_FOR_1_OVER_R__LOCAL_QUADRATIC_PASS",
    )


__all__=[
    "KAPPA_INFORMATION","global_phase_projector","local_relational_metric",
    "local_relational_metric_pseudoinverse","horizontalize","quadratic_action",
    "exact_overlap_action","single_coordinate_quadratic_coefficient",
    "RelationalMetricReceipt","metric_receipt",
]
