"""Regression tests for source-derived ABE/Euler phase connection."""
import math
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.abe_euler_connection import (
    SPIN_HALF, aharonov_bohm_connection, euler_connection, total_abe_connection,
    berry_euler_curvature, closure_defect, exact_closure, empirical_closure,
    covariant_quantum_momentum_terms,
)


def test_spin_half_euler_connection():
    w=np.array([2.0,-4.0])
    assert np.allclose(euler_connection(w),[1.0,-2.0])
    assert SPIN_HALF==0.5


def test_abe_sum_is_exact_component_sum():
    ab=np.array([1.0,2.0]); b=np.array([0.2,-0.1]); e=np.array([-0.3,0.4])
    assert np.allclose(total_abe_connection(ab,b,e),ab+b+e)


def test_ab_normalization_uses_qe_over_hbar_only():
    A=np.array([3.0,-1.0])
    got=aharonov_bohm_connection(A,q_e=2.0,hbar=4.0)
    assert np.allclose(got,0.5*A)


def test_berry_euler_curvature_adds_half_euler_curvature():
    F=np.array([[0.0,2.0],[-2.0,0.0]])
    R=np.array([[0.0,4.0],[-4.0,0.0]])
    assert np.allclose(berry_euler_curvature(F,R),F+0.5*R)


def test_exact_closure_has_no_hidden_tolerance():
    eps=closure_defect(phi_ab=0.0,phi_berry=0.0,euler_curvature_integral=4*math.pi,theta_information=0.0,D=1)
    assert eps==0.0
    assert exact_closure(defect=eps)
    assert empirical_closure(defect=1e-4,epsilon_star=None) is None
    assert empirical_closure(defect=1e-4,epsilon_star=1e-3) is True


def test_intention_trace_stays_separate_from_abe_connection():
    A=np.array([1.0,-2.0]); I=np.array([0.25,0.5])
    conn,intent=covariant_quantum_momentum_terms(hbar=2.0,alpha_s=3.0,A_abe=A,lambda_s=4.0,intention_trace=I)
    assert np.allclose(conn,-6.0*A)
    assert np.allclose(intent,-4.0*I)
