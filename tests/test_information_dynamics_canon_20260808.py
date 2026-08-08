"""Regression tests for the 2026-08-08 relational/information-dynamics canon."""
import math
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary import (
    EthicalResonanceIndex,
    nd_green_potential_from_r,
    dimensional_report,
    tetrahedral_isotropic_second_moment,
    validate_embedding,
    rotational_holonomy_current,
    radial_component,
    zero_sectors,
    InformationFieldState,
    continuity_step_from_faces,
)


def test_signed_eri_distinguishes_opposition_from_alignment():
    i=np.array([1.0,0.0])
    same=np.array([1.0,0.0])
    opposite=np.array([-1.0,0.0])
    assert EthicalResonanceIndex.signed_alignment(i,same) == 1.0
    assert EthicalResonanceIndex.signed_alignment(i,opposite) == -1.0
    assert EthicalResonanceIndex.calculate(1.0,-1.0,1.0) == -1.0


def test_kepler_inverse_distance_is_dimension_selective():
    assert dimensional_report(3).kepler_inverse_distance is True
    assert dimensional_report(2).kepler_inverse_distance is False
    assert dimensional_report(4).kepler_inverse_distance is False
    assert np.isclose(nd_green_potential_from_r(2.0,1.0,3),-0.5)
    assert np.isclose(nd_green_potential_from_r(2.0,1.0,4),-0.125)


def test_tetrahedral_second_moment_isotropic():
    assert tetrahedral_isotropic_second_moment()


def test_u1_rotor_current_embedding():
    rep=validate_embedding(3.7,[0.2,-0.4,0.7])
    assert rep.residual < 1e-12
    assert abs(2.0*rep.amplitude**2-3.7) < 1e-12


def test_holonomy_representative_has_zero_radial_component():
    x=np.array([0.4,-0.2,0.7])
    J=rotational_holonomy_current(x,[0.3,0.1,-0.5])
    assert abs(radial_component(J,x)) < 1e-14


def test_finite_volume_information_balance():
    shape=(4,3,2)
    dx=0.25
    rho=np.ones(shape)
    phase=np.zeros(shape+(3,))
    state=InformationFieldState(rho,phase,zero_sectors(shape),dx)

    Fx=np.zeros((shape[0]+1,shape[1],shape[2]))
    Fy=np.zeros((shape[0],shape[1]+1,shape[2]))
    Fz=np.zeros((shape[0],shape[1],shape[2]+1))
    Fx[-1]=0.2
    outflow=0.2*shape[1]*shape[2]*dx*dx
    sigma=np.full(shape,outflow/(np.prod(shape)*dx**3))

    _,receipt=continuity_step_from_faces(state,(Fx,Fy,Fz),sigma,0.01)
    assert abs(receipt.balance_residual) < 1e-12
    assert receipt.max_local_residual < 1e-12
