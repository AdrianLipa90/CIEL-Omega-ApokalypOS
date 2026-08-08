"""
CIEL N-body Kepler canon v2 theorem helpers.

Exact/conditional results only.
"""
from __future__ import annotations
import numpy as np

def tetrahedral_vertices() -> np.ndarray:
    s=np.sqrt(3.0)
    return np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]],dtype=float)/s

def tetrahedral_first_moment() -> np.ndarray:
    return tetrahedral_vertices().sum(axis=0)

def tetrahedral_second_moment() -> np.ndarray:
    V=tetrahedral_vertices()
    return V.T@V

def tetrahedral_isotropic_second_moment() -> bool:
    return bool(np.allclose(tetrahedral_first_moment(),0.0,atol=1e-15,rtol=0.0)
                and np.allclose(tetrahedral_second_moment(),(4.0/3.0)*np.eye(3),atol=1e-15,rtol=0.0))

def radial_current_3d(r: float, flux_constant: float) -> float:
    r=float(r)
    if r<=0:
        raise ValueError("r must be positive")
    return float(flux_constant/(4.0*np.pi*r*r))

def inverse_distance_potential_from_flux(r: float, flux_constant: float) -> float:
    r=float(r)
    if r<=0:
        raise ValueError("r must be positive")
    return float(-flux_constant/(4.0*np.pi*r))
