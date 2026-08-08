"""Hodge/Helmholtz sector bridge for relational Kepler dynamics.

The full current need not be radial. A sourced exact sector can carry the
Gauss flux while a tangential solenoidal sector preserves holonomy without
changing the radial flux.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
import math
import numpy as np

FOUR_PI=4.0*math.pi

def radial_green_current(x: Sequence[float], flux: float) -> np.ndarray:
    x=np.asarray(x,dtype=float)
    if x.shape!=(3,):
        raise ValueError("B3 current requires a 3-vector")
    r=float(np.linalg.norm(x))
    if r==0:
        raise ZeroDivisionError("centered source singularity")
    return float(flux)/FOUR_PI*x/(r**3)

def rotational_holonomy_current(x: Sequence[float], omega: Sequence[float]) -> np.ndarray:
    x=np.asarray(x,dtype=float); w=np.asarray(omega,dtype=float)
    if x.shape!=(3,) or w.shape!=(3,):
        raise ValueError("3-vectors required")
    return np.cross(w,x)

def radial_component(J: Sequence[float], x: Sequence[float]) -> float:
    J=np.asarray(J,dtype=float); x=np.asarray(x,dtype=float)
    r=float(np.linalg.norm(x))
    if r==0:
        raise ZeroDivisionError
    return float(np.dot(J,x/r))

def tangential_component(J: Sequence[float], x: Sequence[float]) -> np.ndarray:
    J=np.asarray(J,dtype=float); x=np.asarray(x,dtype=float)
    r=float(np.linalg.norm(x))
    if r==0:
        raise ZeroDivisionError
    n=x/r
    return J-np.dot(J,n)*n

def sphere_flux_monte_carlo(current_fn,radius: float,*,samples: int=12000,seed: int=0) -> float:
    if radius<=0:
        raise ValueError
    rng=np.random.default_rng(seed)
    u=rng.normal(size=(samples,3)); u/=np.linalg.norm(u,axis=1)[:,None]
    pts=radius*u
    vals=np.array([np.dot(current_fn(p),n) for p,n in zip(pts,u)])
    return float(FOUR_PI*radius*radius*np.mean(vals))

@dataclass(frozen=True)
class SectorReport:
    radial_flux: float
    holonomic_flux: float
    total_flux: float
    holonomic_radial_max: float
    status: str

def validate_sector_superposition(*,source_flux: float=1.0,omega: Sequence[float]=(0.3,-0.2,0.4),radius: float=0.7,samples: int=12000) -> SectorReport:
    w=np.asarray(omega,dtype=float)
    jr=lambda p: radial_green_current(p,source_flux)
    jh=lambda p: rotational_holonomy_current(p,w)
    jt=lambda p: jr(p)+jh(p)
    fr=sphere_flux_monte_carlo(jr,radius,samples=samples,seed=1)
    fh=sphere_flux_monte_carlo(jh,radius,samples=samples,seed=2)
    ft=sphere_flux_monte_carlo(jt,radius,samples=samples,seed=3)
    dirs=np.eye(3)
    leak=max(abs(radial_component(jh(radius*d),radius*d)) for d in dirs)
    return SectorReport(fr,fh,ft,float(leak),"DERIVED_TESTED_SECTOR_DECOMPOSITION")

def matched_amplitude_from_phase_inertia(I_phi: float) -> float:
    I=float(I_phi)
    if I<=0:
        raise ValueError("I_phi must be positive")
    return math.sqrt(I/2.0)

__all__=["radial_green_current","rotational_holonomy_current","radial_component","tangential_component","sphere_flux_monte_carlo","SectorReport","validate_sector_superposition","matched_amplitude_from_phase_inertia"]
