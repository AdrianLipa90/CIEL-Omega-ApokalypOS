"""Relational information Hessian geometry from the TIR overlap action.

Parent receipt: TIR_KEPLER_DIRECT_DERIVATION_TEST_V0_1.

For d phase coordinates
    z(phi)=(1/d) sum_j exp(i phi_j),
    R(phi)=|z|^2,
    S_rel(phi)=-kappa log R,

the coherent point has local Hessian metric
    g_rel_local=(2 kappa/d)[I-(1/d)11^T].

This module also derives the exact Hessian of S_rel at every point with R>0.
That Hessian always has the global-U(1) zero mode, but it is not guaranteed to
be positive semidefinite away from the coherent region. Therefore:

- exact Hessian tensor: DERIVED globally on R>0;
- Riemannian metric interpretation: LOCAL/REGIONAL, only where the horizontal
  Hessian is positive definite;
- no arbitrary global metric extension is introduced.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

KAPPA_INFORMATION=math.log(2.0)/(24.0*math.pi)


def global_phase_projector(d: int) -> np.ndarray:
    d=int(d)
    if d<2: raise ValueError("d must be >=2")
    one=np.ones((d,1),dtype=float)
    return np.eye(d)-one@one.T/d


def local_relational_metric(d: int,*,kappa: float=KAPPA_INFORMATION) -> np.ndarray:
    d=int(d)
    if kappa<=0: raise ValueError("kappa must be positive")
    return (2.0*float(kappa)/d)*global_phase_projector(d)


def local_relational_metric_pseudoinverse(d: int,*,kappa: float=KAPPA_INFORMATION) -> np.ndarray:
    d=int(d)
    if kappa<=0: raise ValueError("kappa must be positive")
    return (d/(2.0*float(kappa)))*global_phase_projector(d)


def horizontalize(delta: np.ndarray) -> np.ndarray:
    x=np.asarray(delta,dtype=float).ravel()
    if x.size<2: raise ValueError("delta must have at least two components")
    return global_phase_projector(x.size)@x


def overlap_order_parameter(phi: np.ndarray) -> complex:
    x=np.asarray(phi,dtype=float).ravel()
    if x.size<2: raise ValueError("phase state must have at least two components")
    return complex(np.mean(np.exp(1j*x)))


def exact_overlap_action(phi: np.ndarray,*,kappa: float=KAPPA_INFORMATION) -> float:
    z=overlap_order_parameter(phi); R=float(abs(z)**2)
    if R<=0.0: return math.inf
    return float(-float(kappa)*math.log(R))


def overlap_R_gradient_hessian(phi: np.ndarray) -> tuple[float,np.ndarray,np.ndarray]:
    """Exact R=|mean exp(i phi)|^2, gradient and Hessian."""
    x=np.asarray(phi,dtype=float).ravel(); d=x.size
    if d<2: raise ValueError("phase state must have at least two components")
    u=np.exp(1j*x); z=np.mean(u); R=float(abs(z)**2)
    grad=np.array([-2.0/d*np.imag(np.conj(z)*ua) for ua in u],dtype=float)
    H=np.empty((d,d),dtype=float)
    for a in range(d):
        H[a,a]=2.0*(1.0/d**2-np.real(np.conj(z)*u[a])/d)
        for b in range(a+1,d):
            v=2.0/d**2*math.cos(float(x[a]-x[b]))
            H[a,b]=H[b,a]=v
    return R,grad,H


def exact_action_hessian(phi: np.ndarray,*,kappa: float=KAPPA_INFORMATION) -> np.ndarray:
    """Exact Hessian of S_rel=-kappa log R for R>0."""
    if kappa<=0: raise ValueError("kappa must be positive")
    R,grad_R,H_R=overlap_R_gradient_hessian(phi)
    if R<=0.0: raise ValueError("S_rel Hessian undefined at R=0")
    return float(kappa)*(np.outer(grad_R,grad_R)/(R*R)-H_R/R)


def quadratic_action(delta: np.ndarray,*,kappa: float=KAPPA_INFORMATION) -> float:
    x=np.asarray(delta,dtype=float).ravel(); g=local_relational_metric(x.size,kappa=kappa)
    return float(0.5*x@g@x)


def single_coordinate_quadratic_coefficient(d: int,*,kappa: float=KAPPA_INFORMATION) -> float:
    d=int(d)
    if d<2: raise ValueError
    return float(kappa)*(d-1)/(d*d)


@dataclass(frozen=True)
class HessianSignature:
    dimension: int
    overlap_R: float
    eigenvalues: tuple[float,...]
    negative_count: int
    zero_count_numerical: int
    positive_count: int
    global_phase_residual: float
    interpretation: str


def hessian_signature(phi: np.ndarray,*,kappa: float=KAPPA_INFORMATION,numerical_zero_tol: float=1e-12) -> HessianSignature:
    """Report tensor signature. Tolerance is numerical zero detection only."""
    x=np.asarray(phi,dtype=float).ravel(); R,_,_=overlap_R_gradient_hessian(x)
    H=exact_action_hessian(x,kappa=kappa)
    vals=np.linalg.eigvalsh(H)
    neg=int(np.sum(vals < -abs(float(numerical_zero_tol))))
    pos=int(np.sum(vals > abs(float(numerical_zero_tol))))
    zero=int(vals.size-neg-pos)
    phase_res=float(np.linalg.norm(H@np.ones(x.size)))
    if neg==0 and pos==x.size-1:
        interp="RIEMANNIAN_ON_HORIZONTAL_QUOTIENT"
    elif neg>0:
        interp="ACTION_HESSIAN_INDEFINITE__NOT_GLOBAL_RIEMANNIAN_METRIC"
    else:
        interp="DEGENERATE_ACTION_HESSIAN__METRIC_STATUS_UNRESOLVED"
    return HessianSignature(x.size,R,tuple(float(v) for v in vals),neg,zero,pos,phase_res,interp)


@dataclass(frozen=True)
class RelationalMetricReceipt:
    dimension: int
    rank: int
    nullity: int
    nonzero_eigenvalue: float
    single_coordinate_coefficient: float
    status: str
    global_extension_status: str
    kepler_direct_status: str


def metric_receipt(d: int=36,*,kappa: float=KAPPA_INFORMATION) -> RelationalMetricReceipt:
    g=local_relational_metric(d,kappa=kappa); rank=int(np.linalg.matrix_rank(g,tol=1e-13))
    return RelationalMetricReceipt(
        int(d),rank,int(d-rank),float(2.0*float(kappa)/int(d)),
        single_coordinate_quadratic_coefficient(d,kappa=kappa),
        "DERIVED_LOCAL_HESSIAN_METRIC_ON_PHASE_QUOTIENT",
        "EXACT_GLOBAL_ACTION_HESSIAN_DERIVED__RIEMANNIAN_ONLY_WHERE_HORIZONTAL_POSITIVE",
        "FAIL_FOR_1_OVER_R__LOCAL_QUADRATIC_PASS",
    )


__all__=[
    "KAPPA_INFORMATION","global_phase_projector","local_relational_metric",
    "local_relational_metric_pseudoinverse","horizontalize","overlap_order_parameter",
    "overlap_R_gradient_hessian","exact_action_hessian","quadratic_action","exact_overlap_action",
    "single_coordinate_quadratic_coefficient","HessianSignature","hessian_signature",
    "RelationalMetricReceipt","metric_receipt",
]
