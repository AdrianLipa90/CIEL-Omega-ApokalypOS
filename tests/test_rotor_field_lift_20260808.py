"""Regression tests for the constructive rotor -> local Noether field lift."""
import math
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.rotor_field_lift import (
    rotor_field_amplitude, embed_rotor_field,
    noether_current_from_covariant_phase_gradient, scalar_field_current_from_amplitude,
    embedding_current_residual, radial_phase_gradient, radial_phase_profile,
    radial_flux_from_gradient, lift_receipt,
)


def test_constant_modulus_is_forced_by_I_phi_in_embedded_sector():
    I=3.2
    A=rotor_field_amplitude(I)
    assert np.isclose(2*A*A,I)
    psi=embed_rotor_field(np.array([0.0,0.3,-1.2]),I)
    assert np.allclose(np.abs(psi),A)


def test_scalar_field_and_relational_rotor_currents_are_identical():
    I=2.7
    d=np.array([0.2,-0.5,0.9,0.1])
    A=rotor_field_amplitude(I)
    a=scalar_field_current_from_amplitude(d,A)
    b=noether_current_from_covariant_phase_gradient(d,I)
    assert np.allclose(a,b,atol=1e-14)
    assert embedding_current_residual(d,I) < 1e-13


def test_static_radial_b3_sector_has_inverse_square_gradient_and_inverse_distance_profile():
    C=0.7; I=1.4
    r1=0.25; r2=0.5
    g1=radial_phase_gradient(r1,flux_constant=C,I_phi=I)
    g2=radial_phase_gradient(r2,flux_constant=C,I_phi=I)
    assert np.isclose(g1/g2,(r2/r1)**2)
    p1=radial_phase_profile(r1,flux_constant=C,I_phi=I)
    p2=radial_phase_profile(r2,flux_constant=C,I_phi=I)
    assert np.isclose(p1/p2,r2/r1)


def test_integrated_radial_flux_is_radius_independent():
    C=0.8; I=2.0
    expected=4*math.pi*C
    for r in (0.2,0.4,0.8):
        grad=radial_phase_gradient(r,flux_constant=C,I_phi=I)
        assert np.isclose(radial_flux_from_gradient(r,phase_gradient=grad,I_phi=I),expected)


def test_receipt_does_not_promote_general_field_lift():
    r=lift_receipt(1.5,[0.2,0.4,-0.1])
    assert r.embedded_sector_status=="CONSTRUCTIVE_EMBEDDED_SECTOR_EXACT"
    assert r.general_field_lift_status=="OPEN_NOT_UNIQUE_NOT_VALIDATED"
    assert r.current_residual < 1e-13
