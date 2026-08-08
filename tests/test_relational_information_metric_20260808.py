"""Regression tests for local TIR Hessian relational metric."""
import math
import numpy as np

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.relational_information_metric import (
    KAPPA_INFORMATION, global_phase_projector, local_relational_metric,
    local_relational_metric_pseudoinverse, quadratic_action, exact_overlap_action,
    single_coordinate_quadratic_coefficient, metric_receipt,
)


def test_projector_removes_global_phase_mode():
    P=global_phase_projector(36)
    one=np.ones(36)
    assert np.allclose(P@one,0.0,atol=1e-14)
    assert np.allclose(P@P,P,atol=1e-14)


def test_metric_has_one_u1_zero_mode_and_positive_horizontal_spectrum():
    g=local_relational_metric(36)
    vals=np.linalg.eigvalsh(g)
    assert abs(vals[0]) < 1e-14
    assert np.all(vals[1:] > 0)
    assert np.allclose(vals[1:],2*KAPPA_INFORMATION/36,rtol=1e-12,atol=1e-14)


def test_single_coordinate_coefficient_matches_preregistered_receipt():
    c=single_coordinate_quadratic_coefficient(36)
    assert np.isclose(c,KAPPA_INFORMATION*35/(36**2))
    assert np.isclose(c,0.00024827179801127847)


def test_quadratic_action_matches_exact_action_to_second_order():
    d=36
    direction=np.zeros(d); direction[0]=1.0
    for eps in (1e-4,3e-5,1e-5):
        x=eps*direction
        exact=exact_overlap_action(x)
        quad=quadratic_action(x)
        assert abs(exact-quad)/quad < 1e-6


def test_pseudoinverse_is_inverse_on_horizontal_subspace():
    d=12
    P=global_phase_projector(d)
    g=local_relational_metric(d)
    gi=local_relational_metric_pseudoinverse(d)
    assert np.allclose(g@gi,P,atol=1e-12)
    assert np.allclose(gi@g,P,atol=1e-12)


def test_receipt_preserves_failed_direct_kepler_status():
    r=metric_receipt(36)
    assert r.rank==35 and r.nullity==1
    assert r.kepler_direct_status=="FAIL_FOR_1_OVER_R__LOCAL_QUADRATIC_PASS"
