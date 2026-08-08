"""
CIEL / TIR — Source-Derived Phase-First Geometry v1

Implements the explicit standard geometric blocks from the current
Hilbert_Kahler_Phase_Intention_Hamiltonian source:

Fubini-Study on CP1 / Bloch coordinates (theta,phi):
    ds_FS^2 = 1/4 (dtheta^2 + sin^2(theta) dphi^2)

Berry connection in the stated standard gauge:
    A_B = (1-cos(theta))/2 dphi

Berry curvature:
    F_B = 1/2 sin(theta) dtheta wedge dphi

Poincare disk coordinates (u,v), r^2=u^2+v^2<1:
    ds_D^2 = 4 (du^2+dv^2)/(1-r^2)^2

The full source metric is structurally
    G = g_FS direct_sum g_D direct_sum g_rel.

g_rel and the AB/Euler/intention connection pieces are intentionally supplied
by callers until their runtime forms are canonically bound.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import math
import numpy as np


def fubini_study_metric(theta: float) -> np.ndarray:
    s=math.sin(float(theta))
    return np.array([[0.25,0.0],[0.0,0.25*s*s]],dtype=float)


def fubini_study_inverse_metric(theta: float) -> np.ndarray:
    s=math.sin(float(theta))
    if s == 0.0:
        raise ValueError("Bloch polar coordinate singularity: use another chart at theta=0 or pi")
    return np.array([[4.0,0.0],[0.0,4.0/(s*s)]],dtype=float)


def fubini_study_inverse_metric_derivatives(theta: float) -> np.ndarray:
    """Return d_g_inv[k,a,b] for coordinates k=(theta,phi)."""
    s=math.sin(float(theta)); c=math.cos(float(theta))
    if s == 0.0:
        raise ValueError("Bloch polar coordinate singularity")
    out=np.zeros((2,2,2),dtype=float)
    out[0,1,1]=-8.0*c/(s**3)
    return out


def berry_connection(theta: float) -> np.ndarray:
    """Components A=(A_theta,A_phi) in the source's standard gauge."""
    return np.array([0.0,0.5*(1.0-math.cos(float(theta)))],dtype=float)


def berry_connection_derivatives(theta: float) -> np.ndarray:
    """d_A[k,a]=partial_k A_a in coordinates (theta,phi)."""
    out=np.zeros((2,2),dtype=float)
    out[0,1]=0.5*math.sin(float(theta))
    return out


def berry_curvature_matrix(theta: float) -> np.ndarray:
    """Antisymmetric F_ka = partial_k A_a - partial_a A_k."""
    f=0.5*math.sin(float(theta))
    return np.array([[0.0,f],[-f,0.0]],dtype=float)


def poincare_disk_metric(u: float, v: float) -> np.ndarray:
    r2=float(u)*float(u)+float(v)*float(v)
    if not r2 < 1.0:
        raise ValueError("Poincare disk requires u^2+v^2 < 1")
    factor=4.0/((1.0-r2)**2)
    return factor*np.eye(2)


def poincare_disk_inverse_metric(u: float, v: float) -> np.ndarray:
    r2=float(u)*float(u)+float(v)*float(v)
    if not r2 < 1.0:
        raise ValueError("Poincare disk requires u^2+v^2 < 1")
    factor=((1.0-r2)**2)/4.0
    return factor*np.eye(2)


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
    """G = g_FS direct_sum g_D direct_sum g_rel."""
    rel=np.asarray(g_rel,dtype=float)
    if rel.ndim!=2 or rel.shape[0]!=rel.shape[1]:
        raise ValueError("g_rel must be square")
    return block_diag(fubini_study_metric(theta),poincare_disk_metric(u,v),rel)


def direct_sum_inverse_metric(theta: float, u: float, v: float, g_rel_inv: np.ndarray) -> np.ndarray:
    rel=np.asarray(g_rel_inv,dtype=float)
    if rel.ndim!=2 or rel.shape[0]!=rel.shape[1]:
        raise ValueError("g_rel_inv must be square")
    return block_diag(fubini_study_inverse_metric(theta),poincare_disk_inverse_metric(u,v),rel)


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


def geometry_receipt(theta: float, u: float, v: float, g_rel: np.ndarray) -> ExplicitGeometryReceipt:
    rel=np.asarray(g_rel,dtype=float)
    G=direct_sum_metric(theta,u,v,rel)
    return ExplicitGeometryReceipt(
        theta=float(theta),u=float(u),v=float(v),
        berry_chern_local_density=float(0.5*math.sin(float(theta))),
        fs_dimension=2,disk_dimension=2,
        relational_dimension=int(rel.shape[0]),
        total_dimension=int(G.shape[0]),
        status="SOURCE_DERIVED_STANDARD_GEOMETRY_BLOCKS",
    )


__all__=[
    "fubini_study_metric","fubini_study_inverse_metric","fubini_study_inverse_metric_derivatives",
    "berry_connection","berry_connection_derivatives","berry_curvature_matrix",
    "poincare_disk_metric","poincare_disk_inverse_metric","poincare_disk_inverse_metric_derivatives",
    "block_diag","direct_sum_metric","direct_sum_inverse_metric",
    "ExplicitGeometryReceipt","geometry_receipt",
]
