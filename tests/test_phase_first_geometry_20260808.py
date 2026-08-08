"""Regression tests for source-derived phase-first geometry blocks."""
import math
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.phase_first_geometry import (
    fubini_study_metric,
    fubini_study_inverse_metric,
    berry_connection,
    berry_connection_derivatives,
    berry_curvature_matrix,
    poincare_disk_metric,
    poincare_disk_inverse_metric,
    direct_sum_metric,
    direct_sum_inverse_metric,
    build_source_hamiltonian_geometry,
)


def test_fubini_study_metric_matches_source_normalization():
    theta=math.pi/3
    g=fubini_study_metric(theta)
    expected=np.diag([0.25,0.25*(math.sin(theta)**2)])
    assert np.allclose(g,expected)
    assert np.allclose(g@fubini_study_inverse_metric(theta),np.eye(2))


def test_berry_connection_derivative_matches_curvature():
    theta=1.1
    dA=berry_connection_derivatives(theta)
    F=dA-dA.T
    assert np.allclose(F,berry_curvature_matrix(theta))
    assert np.isclose(F[0,1],0.5*math.sin(theta))


def test_poincare_metric_inverse_exact_inside_disk():
    u,v=0.2,-0.3
    g=poincare_disk_metric(u,v)
    gi=poincare_disk_inverse_metric(u,v)
    assert np.allclose(g@gi,np.eye(2))


def test_direct_sum_metric_uses_source_blocks_plus_relational_block():
    theta=0.9; u=0.1; v=0.2
    grel=np.diag([2.0,3.0])
    G=direct_sum_metric(theta,u,v,grel)
    Gi=direct_sum_inverse_metric(theta,u,v,np.linalg.inv(grel))
    assert G.shape==(6,6)
    assert np.allclose(G@Gi,np.eye(6))


def test_builder_injects_berry_connection_without_inventing_extra_connection():
    theta=0.8; u=0.1; v=-0.2
    grel_inv=np.eye(1)
    drel=np.zeros((1,1,1))
    grad=np.zeros(5)
    geom=build_source_hamiltonian_geometry(theta,u,v,grel_inv,drel,grad)
    assert geom.g_inv.shape==(5,5)
    assert np.allclose(geom.A[:2],berry_connection(theta))
    assert np.allclose(geom.A[2:],0.0)
    assert np.allclose(geom.d_A[:2,:2],berry_connection_derivatives(theta))


def test_extra_connection_is_explicit_addition():
    theta=0.8; u=0.1; v=-0.2
    grel_inv=np.eye(1); drel=np.zeros((1,1,1)); grad=np.zeros(5)
    extra=np.array([0.0,0.0,0.1,-0.2,0.3])
    dextra=np.zeros((5,5)); dextra[2,3]=0.4
    geom=build_source_hamiltonian_geometry(theta,u,v,grel_inv,drel,grad,A_extra=extra,d_A_extra=dextra)
    assert np.allclose(geom.A[2:],extra[2:])
    assert np.isclose(geom.d_A[2,3],0.4)
