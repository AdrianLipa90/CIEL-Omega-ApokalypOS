"""Regression tests for source-derived canonical information backreaction."""
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.canonical_information_backreaction import (
    CanonicalRelationalState,
    HamiltonianGeometry,
    covariant_momentum,
    phase_velocity,
    hamiltonian,
    hamilton_equations,
    curvature_tensor,
    covariant_momentum_rate_flat_metric,
)


def _geom(A=None,dA=None,gradV=None,dG=None):
    n=2
    return HamiltonianGeometry(
        g_inv=np.eye(n),
        A=np.zeros(n) if A is None else np.asarray(A,dtype=float),
        d_g_inv=np.zeros((n,n,n)) if dG is None else np.asarray(dG,dtype=float),
        d_A=np.zeros((n,n)) if dA is None else np.asarray(dA,dtype=float),
        grad_V=np.zeros(n) if gradV is None else np.asarray(gradV,dtype=float),
        V=0.0,
    )


def test_zero_phase_momentum_reduces_to_standard_potential_force():
    s=CanonicalRelationalState(q=np.array([0.2,-0.1]),p=np.array([1.0,2.0]),J=0.0,J0_phase_offset=0.0,I_phi=2.0)
    g=_geom(A=[5.0,-7.0],dA=[[3.0,4.0],[2.0,1.0]],gradV=[0.3,-0.4])
    qdot,pdot=hamilton_equations(s,g)
    assert np.allclose(qdot,s.p)
    assert np.allclose(pdot,-g.grad_V)


def test_minimal_coupling_is_exactly_p_minus_JA():
    s=CanonicalRelationalState(q=np.zeros(2),p=np.array([3.0,-2.0]),J=2.5,J0_phase_offset=0.5,I_phi=4.0)
    g=_geom(A=[0.4,-0.2])
    Pi=covariant_momentum(s,g)
    assert np.allclose(Pi,np.array([2.0,-1.5]))
    assert np.allclose(hamilton_equations(s,g)[0],Pi)
    assert phase_velocity(s)==0.5
    expected_phase=(2.0**2)/(2*4.0)
    expected_rel=0.5*np.dot(Pi,Pi)
    assert np.isclose(hamiltonian(s,g),expected_phase+expected_rel)


def test_flat_metric_covariant_momentum_rate_is_J_curvature_v_minus_gradV():
    dA=np.array([[0.0,2.0],[0.0,0.0]])
    s=CanonicalRelationalState(q=np.zeros(2),p=np.array([1.0,0.5]),J=3.0,J0_phase_offset=0.0,I_phi=1.0)
    g=_geom(A=[0.0,0.0],dA=dA,gradV=[0.2,-0.1])
    qdot,_=hamilton_equations(s,g)
    F=curvature_tensor(dA)
    got=covariant_momentum_rate_flat_metric(s,g)
    expected=s.J*(F@qdot)-g.grad_V
    assert np.allclose(got,expected)


def test_connection_with_zero_curvature_is_pure_gauge_for_covariant_force():
    dA=np.array([[1.0,0.4],[0.4,-0.3]])
    s=CanonicalRelationalState(q=np.zeros(2),p=np.array([0.7,-1.1]),J=1.2,J0_phase_offset=0.0,I_phi=2.0)
    g=_geom(A=[0.0,0.0],dA=dA,gradV=[-0.2,0.6])
    F=curvature_tensor(dA)
    assert np.allclose(F,0.0)
    got=covariant_momentum_rate_flat_metric(s,g)
    assert np.allclose(got,-g.grad_V)


def test_scalar_phase_offset_is_not_vector_residual_current():
    s=CanonicalRelationalState(q=np.zeros(2),p=np.zeros(2),J=1.0,J0_phase_offset=0.25,I_phi=2.0)
    assert np.isscalar(s.J0_phase_offset)
    assert np.isclose(phase_velocity(s),0.375)
