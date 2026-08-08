"""Primitive information structural generator W_s from Bloch-sphere Killing flow.

Source parent: METATIME_SM_DEBT1_KILLING_GENERATOR_POLAR_AXIS_v1_7.

Canonical formal definition:
    W_s = -i L_{V_s}
where V_s is a seed-selected Killing generator on CP1 ~= S2_Bloch.

For an axial chart V=partial_phi, Fourier modes exp(i m phi) satisfy
    W exp(i m phi) = m exp(i m phi).

This module implements the exact finite Fourier-mode representation. The
physical axis/sector selection is NOT inferred; it must be supplied with
provenance. Collatz rhythm and zero-level fluctuations are separate layers.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence
import numpy as np


def fourier_killing_operator(mode_indices: Sequence[int]) -> np.ndarray:
    """Matrix of -i d/dphi in an explicitly supplied Fourier-mode basis."""
    modes=np.asarray(tuple(int(m) for m in mode_indices),dtype=float)
    if modes.ndim != 1 or modes.size == 0:
        raise ValueError("mode_indices must be a non-empty 1D sequence")
    return np.diag(modes).astype(complex)


def killing_expectation(coefficients: Sequence[complex], mode_indices: Sequence[int]) -> float:
    """Normalized expectation <psi|W|psi>/<psi|psi> in the Fourier basis."""
    c=np.asarray(coefficients,dtype=complex).ravel()
    W=fourier_killing_operator(mode_indices)
    if c.size != W.shape[0]:
        raise ValueError("coefficient/mode dimension mismatch")
    norm=float(np.real(np.vdot(c,c)))
    if norm <= 0.0:
        raise ValueError("state must have nonzero norm")
    value=np.vdot(c,W@c)/norm
    if abs(float(np.imag(value))) > 1e-12:
        raise ValueError("Hermitian Killing-generator expectation must be real")
    return float(np.real(value))


def apply_killing_operator(coefficients: Sequence[complex], mode_indices: Sequence[int]) -> np.ndarray:
    c=np.asarray(coefficients,dtype=complex).ravel()
    W=fourier_killing_operator(mode_indices)
    if c.size != W.shape[0]:
        raise ValueError("coefficient/mode dimension mismatch")
    return W@c


def is_hermitian_operator(W: np.ndarray) -> bool:
    a=np.asarray(W,dtype=complex)
    return bool(a.ndim==2 and a.shape[0]==a.shape[1] and np.allclose(a,a.conj().T,atol=1e-14,rtol=0.0))


@dataclass(frozen=True)
class KillingGeneratorReceipt:
    modes: tuple[int,...]
    dimension: int
    hermitian: bool
    axis_selection_status: str
    generator_status: str
    provenance: str


def generator_receipt(mode_indices: Iterable[int], *, axis_provenance: str) -> KillingGeneratorReceipt:
    modes=tuple(int(m) for m in mode_indices)
    W=fourier_killing_operator(modes)
    return KillingGeneratorReceipt(
        modes=modes,
        dimension=len(modes),
        hermitian=is_hermitian_operator(W),
        axis_selection_status="SUPPLIED_MODEL_SELECTION__NOT_DERIVED_HERE",
        generator_status="CONDITIONALLY_CLOSED_FORMAL_GEOMETRIC_GENERATOR",
        provenance=str(axis_provenance),
    )


__all__=[
    "fourier_killing_operator","killing_expectation","apply_killing_operator",
    "is_hermitian_operator","KillingGeneratorReceipt","generator_receipt",
]
