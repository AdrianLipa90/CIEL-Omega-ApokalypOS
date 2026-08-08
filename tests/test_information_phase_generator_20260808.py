"""Regression tests for source-derived intention/information phase generator."""
import math
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.information_phase_generator import (
    KAPPA_INFORMATION,
    information_generator_expectation,
    free_phase_hamiltonian_expectation,
    bind_classical_J_to_information_generator,
    block_diagonal_metric,
    structure_receipt,
)


def test_kappa_is_ln2_over_24pi():
    assert np.isclose(KAPPA_INFORMATION,math.log(2)/(24*math.pi))


def test_information_generator_is_linear_source_equation():
    got=information_generator_expectation(3.0,0.25)
    expected=KAPPA_INFORMATION*3.0+0.25
    assert np.isclose(got,expected)


def test_free_phase_energy_uses_no_hidden_coefficient():
    got=free_phase_hamiltonian_expectation(
        2.0,0.1,hbar=1.5,delta_tau=0.2,rho_s=0.4
    )
    I=KAPPA_INFORMATION*2.0+0.1
    assert np.isclose(got,(1.5/0.2)*0.4*I)


def test_classical_quantum_binding_is_not_silently_promoted():
    I=information_generator_expectation(1.0,0.0)
    b=bind_classical_J_to_information_generator(
        I,1.0,0.0,provenance="fixture",assert_semiclassical_identification=False
    )
    assert b.status == "CANDIDATE_CLASSICAL_QUANTUM_BINDING"
    assert abs(b.residual)<1e-15


def test_block_metric_is_exact_direct_sum():
    gfs=np.diag([1.0,2.0])
    gd=np.array([[3.0]])
    grel=np.diag([4.0,5.0,6.0])
    G=block_diagonal_metric(gfs,gd,grel)
    assert G.shape==(6,6)
    assert np.allclose(np.diag(G),[1,2,3,4,5,6])
    assert np.allclose(G-np.diag(np.diag(G)),0.0)


def test_structure_receipt_reports_source_derived_dimension():
    r=structure_receipt(
        1.5,0.2,[np.eye(2),np.eye(1),np.eye(3)],
        hbar=1.0,delta_tau=0.5,rho_s=0.75,
    )
    assert r.metric_dimension==6
    assert r.status=="SOURCE_DERIVED_STRUCTURE"
    assert r.free_phase_energy_expectation is not None
