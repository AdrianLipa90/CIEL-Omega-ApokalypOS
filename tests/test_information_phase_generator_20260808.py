"""Regression tests for source-derived intention/information phase generator."""
import math
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.information_phase_generator import (
    KAPPA_INFORMATION,
    information_generator_expectation,
    semiclassical_intention_charge,
    free_phase_hamiltonian_expectation,
    bind_phase_offset_to_information_generator,
    build_canonical_state_with_information_offset,
    block_diagonal_metric,
    structure_receipt,
)


def test_kappa_is_ln2_over_24pi():
    assert np.isclose(KAPPA_INFORMATION,math.log(2)/(24*math.pi))


def test_information_generator_is_linear_source_equation():
    got=information_generator_expectation(3.0,0.25)
    expected=KAPPA_INFORMATION*3.0+0.25
    assert np.isclose(got,expected)


def test_semiclassical_intention_charge_matches_formal_source():
    got=semiclassical_intention_charge(2.0,0.1,hbar=1.5,rho_s=0.4)
    I=KAPPA_INFORMATION*2.0+0.1
    assert np.isclose(got,1.5*0.4*I)


def test_free_phase_energy_is_charge_over_delta_tau():
    charge=semiclassical_intention_charge(2.0,0.1,hbar=1.5,rho_s=0.4)
    got=free_phase_hamiltonian_expectation(2.0,0.1,hbar=1.5,delta_tau=0.2,rho_s=0.4)
    assert np.isclose(got,charge/0.2)


def test_phase_offset_binding_uses_hbar_rho_information_generator():
    b=bind_phase_offset_to_information_generator(
        1.0,0.2,hbar=2.0,rho_s=0.5,provenance="formal-source"
    )
    assert b.status=="SOURCE_DERIVED_SEMICLASSICAL_PHASE_OFFSET"
    assert abs(b.source_identity_residual)<1e-15
    assert np.isclose(b.J0_phase_offset,2.0*0.5*b.I_expectation)


def test_canonical_state_receives_phase_offset_not_total_J():
    state,b=build_canonical_state_with_information_offset(
        np.zeros(2),np.ones(2),J=3.0,I_phi=2.0,
        W_expectation=1.0,delta_I0_expectation=0.0,
        hbar=2.0,rho_s=0.5,provenance="formal-source",
    )
    assert np.isclose(state.J0_phase_offset,b.J0_phase_offset)
    assert state.J==3.0


def test_block_metric_is_exact_direct_sum():
    gfs=np.diag([1.0,2.0]); gd=np.array([[3.0]]); grel=np.diag([4.0,5.0,6.0])
    G=block_diagonal_metric(gfs,gd,grel)
    assert G.shape==(6,6)
    assert np.allclose(np.diag(G),[1,2,3,4,5,6])
    assert np.allclose(G-np.diag(np.diag(G)),0.0)


def test_structure_receipt_reports_source_derived_offset_and_dimension():
    r=structure_receipt(
        1.5,0.2,[np.eye(2),np.eye(1),np.eye(3)],
        hbar=1.0,delta_tau=0.5,rho_s=0.75,
    )
    assert r.metric_dimension==6
    assert r.status=="SOURCE_DERIVED_STRUCTURE"
    assert r.semiclassical_phase_offset is not None
    assert r.free_phase_energy_expectation is not None
