"""
CIEL / TIR — Source-Derived Phase-First Geometry v3

Standard source blocks:
    ds_FS^2 = 1/4 (dtheta^2 + sin^2(theta) dphi^2)
    A_B = (1-cos(theta))/2 dphi
    F_B = 1/2 sin(theta) dtheta wedge dphi
    ds_D^2 = 4 (du^2+dv^2)/(1-u^2-v^2)^2
    G = g_FS direct_sum g_D direct_sum g_rel

New in v3:
    the local coherent-point relational block can be built from the Hessian of
    S_rel=-kappa log R rather than supplied arbitrarily. Its ambient inverse is
    the Moore-Penrose inverse and acts as the exact inverse on the horizontal
    quotient subspace with the global U(1) mode removed.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


def fubini_study_metric(theta: float) -> np.ndarray:
    s=math.sin(float(theta))
    return np.array([[0.25,0.0],[0.0,0.25*s*s]],dtype=float)


def fubini_study_inverse_metric(theta: float) -> np.ndarray:
    s=math.sin(float(theta))
    if s == 0.0:
        raise ValueError("Bloch polar coordinate singularity: use another chart")
    return np.array([[4.0,0.0],[0.0,4.0/(s*s)]],dtype=float)


def fubini_study_inverse_metric_derivatives(theta: float) -> np.ndarray:
    s=math.sin(float(theta)); c=math.cos(float(theta))
    if s == 0.0:
        raise ValueError("Bloch polar coordinate singularity")
    out=np.zeros((2,2,2),dtype=float)
    out[0,1,1]=-8.0*c/(s**3)
    return out


def berry_connection(theta: float) -> np.ndarray:
    return np.array([0.0,0.5*(1.0-math.cos(float(theta)))],dtype=float)


def berry_connection_derivatives(theta: float) -> np.ndarray:
    out=np.zeros((2,2),dtype=float)
    out[0,1]=0.5*math.sin(float(theta))
    return out


def berry_curvature_matrix(theta: float) -> np.ndarray:
    f=0.5*math.sin(float(theta))
    return np.array([[0.0,f],[-f,0.0]],dtype=float)


def poincare_disk_metric(u: float, v: float) -> np.ndarray:
    r2=float(u)*float(u)+float(v)*float(v)
    if not r2 < 1.0:
        raise ValueError("Poincare disk requires u^2+v^2 < 1")
    return 4.0/((1.0-r2)**2)*np.eye(2)


def poincare_disk_inverse_metric(u: float, v: float) -> np.ndarray:
    r2=float(u)*float(u)+float(v)*float(v)
    if not r2 < 1.0:
        raise ValueError("Poincare disk requires u^2+v^2 < 1")
    return ((1.0-r2)**2)/4.0*np.eye(2)


def poincare_disk_inverse_metric_derivatives(u: float, v: float) -> np.ndarray:
    r2=float(u)*float(u)+float(v)*float(v)
    if not r2 < 1.0:
        raise ValueError("Poincare disk requires u^2+v^2 < 1")
    one_minus=1.0-r2
    out=np.zeros((2,2,2),dtype=float)
    out[0]=-float(u)*one_minus*np.eye(2)
    out[1]=-float(v)*one_minus*np.eye(2)
    return out


def block_diag(*blocks: np.ndarray) -> np.ndarray:
    mats=[]
    for b in blocks:
        a=np.asarray(b,dtype=float)
        if a.ndim!=2 or a.shape[0]!=a.shape[1]:
            raise ValueError("blocks must be square")
        mats.append(a)
    n=sum(a.shape[0] for a in mats)
    out=np.zeros((n,n),dtype=float)
    k=0
    for a in mats:
        m=a.shape[0]
        out[k:k+m,k:k+m]=a
        k+=m
    return out


def direct_sum_metric(theta: float, u: float, v: float, g_rel: np.ndarray) -> np.ndarray:
    rel=np.asarray(g_rel,dtype=float)
    if rel.ndim!=2 or rel.shape[0]!=rel.shape[1]:
        raise ValueError("g_rel must be square")
    return block_diag(fubini_study_metric(theta),poincare_disk_metric(u,v),rel)


def direct_sum_inverse_metric(theta: float, u: float, v: float, g_rel_inv: np.ndarray) -> np.ndarray:
    rel=np.asarray(g_rel_inv,dtype=float)
    if rel.ndim!=2 or rel.shape[0]!=rel.shape[1]:
        raise ValueError("g_rel_inv must be square")
    return block_diag(fubini_study_inverse_metric(theta),poincare_disk_inverse_metric(u,v),rel)


def direct_sum_inverse_metric_derivatives(theta: float,u: float,v: float,g_rel_inv: np.ndarray,d_g_rel_inv: np.ndarray) -> np.ndarray:
    rel=np.asarray(g_rel_inv,dtype=float); drel=np.asarray(d_g_rel_inv,dtype=float)
    nrel=rel.shape[0]
    if rel.shape!=(nrel,nrel) or drel.shape!=(nrel,nrel,nrel):
        raise ValueError("relational metric derivative shapes")
    ntot=4+nrel
    out=np.zeros((ntot,ntot,ntot),dtype=float)
    dfs=fubini_study_inverse_metric_derivatives(theta)
    out[0,:2,:2]=dfs[0]; out[1,:2,:2]=dfs[1]
    dd=poincare_disk_inverse_metric_derivatives(u,v)
    out[2,2:4,2:4]=dd[0]; out[3,2:4,2:4]=dd[1]
    for j in range(nrel):
        out[4+j,4:,4:]=drel[j]
    return out


def source_connection_and_derivatives(theta: float,total_dimension: int,*,A_extra: np.ndarray|None=None,d_A_extra: np.ndarray|None=None):
    if total_dimension < 4:
        raise ValueError("total dimension must include FS and disk blocks")
    A=np.zeros(total_dimension,dtype=float); dA=np.zeros((total_dimension,total_dimension),dtype=float)
    A[:2]=berry_connection(theta); dA[:2,:2]=berry_connection_derivatives(theta)
    if A_extra is not None:
        extra=np.asarray(A_extra,dtype=float)
        if extra.shape!=(total_dimension,): raise ValueError("A_extra shape")
        A=A+extra
    if d_A_extra is not None:
        de=np.asarray(d_A_extra,dtype=float)
        if de.shape!=(total_dimension,total_dimension): raise ValueError("d_A_extra shape")
        dA=dA+de
    return A,dA


def build_source_hamiltonian_geometry(theta: float,u: float,v: float,g_rel_inv: np.ndarray,d_g_rel_inv: np.ndarray,grad_V: np.ndarray,*,V: float=0.0,A_extra: np.ndarray|None=None,d_A_extra: np.ndarray|None=None):
    from .canonical_information_backreaction import HamiltonianGeometry
    Ginv=direct_sum_inverse_metric(theta,u,v,g_rel_inv)
    dG=direct_sum_inverse_metric_derivatives(theta,u,v,g_rel_inv,d_g_rel_inv)
    A,dA=source_connection_and_derivatives(theta,Ginv.shape[0],A_extra=A_extra,d_A_extra=d_A_extra)
    grad=np.asarray(grad_V,dtype=float)
    if grad.shape!=(Ginv.shape[0],): raise ValueError("grad_V shape")
    return HamiltonianGeometry(Ginv,A,dG,dA,grad,float(V))


def build_local_tir_hamiltonian_geometry(theta: float,u: float,v: float,d_rel: int,grad_V: np.ndarray,*,V: float=0.0,A_extra: np.ndarray|None=None,d_A_extra: np.ndarray|None=None):
    """Build the coherent-point local TIR geometry with derived g_rel Hessian.

    The relational inverse is the pseudoinverse because the ambient metric has
    one global-U(1) zero mode. It is the exact inverse on the horizontal quotient.
    The coherent-point Hessian is constant to this local order, so d_g_rel_inv=0.
    """
    from .relational_information_metric import local_relational_metric_pseudoinverse
    ginv=local_relational_metric_pseudoinverse(int(d_rel))
    dginv=np.zeros((int(d_rel),int(d_rel),int(d_rel)),dtype=float)
    return build_source_hamiltonian_geometry(theta,u,v,ginv,dginv,grad_V,V=V,A_extra=A_extra,d_A_extra=d_A_extra)


@dataclass(frozen=True)
class ExplicitGeometryReceipt:
    theta: float
    u: float
    v: float
    berry_chern_local_density: float
    fs_dimension: int
    disk_dimension: int
    relational_dimension: int
    total_dimension: int
    status: str


def geometry_receipt(theta: float,u: float,v: float,g_rel: np.ndarray) -> ExplicitGeometryReceipt:
    rel=np.asarray(g_rel,dtype=float); G=direct_sum_metric(theta,u,v,rel)
    return ExplicitGeometryReceipt(float(theta),float(u),float(v),float(0.5*math.sin(float(theta))),2,2,int(rel.shape[0]),int(G.shape[0]),"SOURCE_DERIVED_STANDARD_GEOMETRY_BLOCKS")


__all__=[
    "fubini_study_metric","fubini_study_inverse_metric","fubini_study_inverse_metric_derivatives",
    "berry_connection","berry_connection_derivatives","berry_curvature_matrix",
    "poincare_disk_metric","poincare_disk_inverse_metric","poincare_disk_inverse_metric_derivatives",
    "block_diag","direct_sum_metric","direct_sum_inverse_metric","direct_sum_inverse_metric_derivatives",
    "source_connection_and_derivatives","build_source_hamiltonian_geometry","build_local_tir_hamiltonian_geometry",
    "ExplicitGeometryReceipt","geometry_receipt",
]
