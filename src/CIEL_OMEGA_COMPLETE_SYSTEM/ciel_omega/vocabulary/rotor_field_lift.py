"""Constructive constant-modulus rotor -> local Noether-current field lift.

Parents:
- TIR_KEPLER_NOETHER_PHASE_BINDING_V0_4.md
- N-Body Kepler Canon v4
- relational phase rotor Hamiltonian

This module closes only the explicitly constructed embedded sector:

    psi = sqrt(I_phi/2) exp(i chi)

For the standard complex-scalar U(1) Noether current,

    J^mu = 2 A^2 D^mu chi = I_phi D^mu chi.

Thus the background-free relational rotor current has an exact local field
representation in this chosen constant-modulus embedding.

This is NOT a theorem that every finite-dimensional relational state uniquely
induces a spacetime field on B3. General/unique field-lift physics remains OPEN.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence
import numpy as np


def rotor_field_amplitude(I_phi: float) -> float:
    I=float(I_phi)
    if I <= 0:
        raise ValueError("I_phi must be positive")
    return math.sqrt(I/2.0)


def embed_rotor_field(chi: np.ndarray | float, I_phi: float) -> np.ndarray:
    """psi=sqrt(I_phi/2) exp(i chi), pointwise."""
    phase=np.asarray(chi,dtype=float)
    A=rotor_field_amplitude(I_phi)
    return A*np.exp(1j*phase)


def noether_current_from_covariant_phase_gradient(
    D_chi: Sequence[float] | np.ndarray,
    I_phi: float,
) -> np.ndarray:
    """J^mu=I_phi D^mu chi in the constructive constant-modulus sector."""
    d=np.asarray(D_chi,dtype=float)
    return float(I_phi)*d


def scalar_field_current_from_amplitude(
    D_chi: Sequence[float] | np.ndarray,
    amplitude: float,
) -> np.ndarray:
    """Polar U(1) identity J^mu=2 A^2 D^mu chi."""
    A=float(amplitude)
    if A < 0:
        raise ValueError("amplitude must be nonnegative")
    return 2.0*A*A*np.asarray(D_chi,dtype=float)


def embedding_current_residual(D_chi: Sequence[float] | np.ndarray, I_phi: float) -> float:
    A=rotor_field_amplitude(I_phi)
    a=scalar_field_current_from_amplitude(D_chi,A)
    b=noether_current_from_covariant_phase_gradient(D_chi,I_phi)
    return float(np.linalg.norm(a-b))


def radial_phase_gradient(
    radius: float,
    *,
    flux_constant: float,
    I_phi: float,
) -> float:
    """
    Static centered radial constant-modulus sector on Euclidean B3.

    Conservation gives r^2 I_phi chi'(r)=C, hence
        chi'(r)=C/(I_phi r^2).
    """
    r=float(radius); I=float(I_phi)
    if r <= 0:
        raise ValueError("radius must be positive")
    if I <= 0:
        raise ValueError("I_phi must be positive")
    return float(flux_constant)/(I*r*r)


def radial_phase_profile(
    radius: float,
    *,
    flux_constant: float,
    I_phi: float,
    chi_infinity_constant: float=0.0,
) -> float:
    """chi(r)=chi0-C/(I_phi r), up to the supplied additive constant."""
    r=float(radius); I=float(I_phi)
    if r <= 0:
        raise ValueError("radius must be positive")
    if I <= 0:
        raise ValueError("I_phi must be positive")
    return float(chi_infinity_constant)-float(flux_constant)/(I*r)


def radial_flux_from_gradient(
    radius: float,
    *,
    phase_gradient: float,
    I_phi: float,
) -> float:
    """Integrated centered spherical flux 4*pi*r^2*I_phi*chi'(r)."""
    r=float(radius)
    if r <= 0:
        raise ValueError("radius must be positive")
    return float(4.0*math.pi*r*r*float(I_phi)*float(phase_gradient))


@dataclass(frozen=True)
class RotorFieldLiftReceipt:
    I_phi: float
    amplitude: float
    current_residual: float
    embedded_sector_status: str
    general_field_lift_status: str
    radial_kepler_status: str


def lift_receipt(I_phi: float, D_chi: Sequence[float] | np.ndarray) -> RotorFieldLiftReceipt:
    return RotorFieldLiftReceipt(
        I_phi=float(I_phi),
        amplitude=rotor_field_amplitude(I_phi),
        current_residual=embedding_current_residual(D_chi,I_phi),
        embedded_sector_status="CONSTRUCTIVE_EMBEDDED_SECTOR_EXACT",
        general_field_lift_status="OPEN_NOT_UNIQUE_NOT_VALIDATED",
        radial_kepler_status="EXACT_CONDITIONAL_ON_STATIC_CENTERED_RADIAL_CONSTANT_MODULUS_B3_SECTOR",
    )


__all__=[
    "rotor_field_amplitude","embed_rotor_field",
    "noether_current_from_covariant_phase_gradient","scalar_field_current_from_amplitude",
    "embedding_current_residual","radial_phase_gradient","radial_phase_profile",
    "radial_flux_from_gradient","RotorFieldLiftReceipt","lift_receipt",
]
