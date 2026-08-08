"""Regression tests for TIR relational Hessian geometry."""
import numpy as np
import pytest

from src.CIEL_OMEGA_COMPLETE_SYSTEM.ciel_omega.vocabulary.relational_information_metric import (
    KAPPA_INFORMATION, global_phase_projector, local_relational_metric,
    local_relational_metric_pseudoinverse, quadratic_action, exact_overlap_action,
    exact_action_hessian, overlap_R_gradient_hessian, hessian_signature,
    regional_relational_metric_pseudoinverse, regional_metric_receipt,
    NonRiemannianRelationalRegion,
    single_coordinate_quadratic_coefficient, metric_receipt,
)


def test_projector_removes_global_phase_mode():
    P=global_phase_projector(36); one=np.ones(36)
    assert np.allclose(P@one,0.0,atol=1e-14)
    assert np.allclose(P@P,P,atol=1e-14)


def test_metric_has_one_u1_zero_mode_and_positive_horizontal_spectrum():
    g=local_relational_metric(36); vals=np.linalg.eigvalsh(g)
    assert abs(vals[0]) < 1e-14
    assert np.all(vals[1:] > 0)
    assert np.allclose(vals[1:],2*KAPPA_INFORMATION/36,rtol=1e-12,atol=1e-14)


def test_exact_hessian_at_coherence_equals_local_metric():
    d=9
    H=exact_action_hessian(np.zeros(d))
    assert np.allclose(H,local_relational_metric(d),atol=1e-14)


def test_exact_R_gradient_and_hessian_are_global_phase_invariant():
    x=np.array([0.2,-0.7,1.1,0.4,-1.0])
    R,g,HR=overlap_R_gradient_hessian(x)
    assert abs(np.sum(g)) < 1e-13
    H=exact_action_hessian(x)
    assert np.linalg.norm(H@np.ones(x.size)) < 1e-12
    shifted=x+2.345
    R2,g2,HR2=overlap_R_gradient_hessian(shifted)
    assert np.isclose(R,R2)
    assert np.allclose(g,g2,atol=1e-14)
    assert np.allclose(HR,HR2,atol=1e-14)


def test_global_action_hessian_can_be_indefinite_away_from_coherence():
    x=np.array([0.86055566,-1.44647274,-2.88414841,-3.03774646,1.96833496,2.59341978])
    s=hessian_signature(x)
    assert s.overlap_R > 0
    assert s.negative_count >= 1
    assert s.interpretation=="ACTION_HESSIAN_INDEFINITE__NOT_GLOBAL_RIEMANNIAN_METRIC"
    assert s.global_phase_residual < 1e-11
    assert not regional_metric_receipt(x).usable_as_hamiltonian_metric
    with pytest.raises(NonRiemannianRelationalRegion):
        regional_relational_metric_pseudoinverse(x)


def test_near_coherence_hessian_is_riemannian_on_horizontal_quotient():
    x=np.array([0.02,0.0,0.0,0.0,0.0])
    s=hessian_signature(x)
    assert s.negative_count==0
    assert s.positive_count==x.size-1
    assert s.interpretation=="RIEMANNIAN_ON_HORIZONTAL_QUOTIENT"
    gi=regional_relational_metric_pseudoinverse(x)
    H=exact_action_hessian(x)
    P=global_phase_projector(x.size)
    assert np.allclose(H@gi,P,atol=1e-9)
    assert regional_metric_receipt(x).status=="REGIONAL_METRIC_ADMITTED"


def test_single_coordinate_coefficient_matches_preregistered_receipt():
    c=single_coordinate_quadratic_coefficient(36)
    assert np.isclose(c,KAPPA_INFORMATION*35/(36**2))
    assert np.isclose(c,0.00024827179801127847)


def test_quadratic_action_matches_exact_action_to_second_order():
    d=36; direction=np.zeros(d); direction[0]=1.0
    for eps in (1e-4,3e-5,1e-5):
        x=eps*direction; exact=exact_overlap_action(x); quad=quadratic_action(x)
        assert abs(exact-quad)/quad < 1e-6


def test_pseudoinverse_is_inverse_on_horizontal_subspace():
    d=12; P=global_phase_projector(d); g=local_relational_metric(d); gi=local_relational_metric_pseudoinverse(d)
    assert np.allclose(g@gi,P,atol=1e-12)
    assert np.allclose(gi@g,P,atol=1e-12)


def test_receipt_preserves_failed_direct_kepler_and_global_hessian_status():
    r=metric_receipt(36)
    assert r.rank==35 and r.nullity==1
    assert r.kepler_direct_status=="FAIL_FOR_1_OVER_R__LOCAL_QUADRATIC_PASS"
    assert r.global_extension_status=="EXACT_GLOBAL_ACTION_HESSIAN_DERIVED__RIEMANNIAN_ONLY_WHERE_HORIZONTAL_POSITIVE"
