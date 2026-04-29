from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

from src.ciel_sot_agent.holonomic_normalizer import (
    HolonomicCallbacks,
    circular_barycenter,
    circular_distance,
    clip_couplings,
    holonomic_system_normalizer_v2,
    renormalize_couplings,
    symmetrize_couplings,
    wrap,
)


def test_wrap_keeps_angle_in_principal_interval() -> None:
    value = wrap(4.0)
    assert -3.141592653589793 < value <= 3.141592653589793


def test_circular_helpers_return_expected_shapes() -> None:
    phi = circular_barycenter([0.0, 1.0], [0.5, 0.5])
    assert isinstance(phi, float)
    assert circular_distance(0.0, 0.0) == 0.0


def test_coupling_postprocessing_is_stable() -> None:
    couplings = {("a", "b"): 2.0, ("b", "a"): 0.0}
    sym = symmetrize_couplings(couplings)
    clipped = clip_couplings(sym, lo=0.0, hi=1.0)
    renorm = renormalize_couplings(clipped, target_norm="l1")
    assert renorm[("a", "b")] == renorm[("b", "a")]
    assert abs(sum(abs(v) for v in renorm.values()) - 1.0) < 1e-9


def _callbacks() -> HolonomicCallbacks:
    return HolonomicCallbacks(
        closure_defect=lambda repo_states: 0.05,
        all_pairwise_tensions=lambda repo_states, couplings: [{"tension": 0.1}],
        compute_placeholder_penalty=lambda objects: 0.0,
        compute_demo_legacy_penalty=lambda objects: 0.0,
        compute_semantic_execution_seam_penalty=lambda X: 0.01,
        object_break_penalty=lambda obj: 0.0,
        seam_local_penalty=lambda X, obj: 0.0,
        local_tension=lambda X, i, j: 0.1,
        recompute_manifests_and_bridge=lambda X: X,
    )


def _state() -> SimpleNamespace:
    return SimpleNamespace(
        repo_states={"canon": {"phase": 0.0}},
        couplings={("a", "b"): 0.5, ("b", "a"): 0.3},
        orbital_final={"closure_penalty": 5.0},
        sectors={
            "affect": SimpleNamespace(phi=1.0, amplitude=1.0, decoherence=0.1, min_amplitude_floor=0.05),
            "memory": SimpleNamespace(lobes=[0.8, 1.2], lobe_weights=[0.7, 0.3], decoherence=0.1),
            "core": SimpleNamespace(phi=0.0, decoherence=0.05),
            "vocabulary": SimpleNamespace(phi=0.4, decoherence=0.02),
        },
        distortion={"lie": 0.0, "omit": 0.0, "hallucinate": 0.0, "smooth": 0.0},
        objects=[SimpleNamespace(exec_weight=1.0)],
        quality={"a": 1.0, "b": 1.0},
        thresholds={"seam_ok": 0.15},
        max_coupling=1.0,
        mode="deep",
        allow_writeback=True,
    )


def test_holonomic_normalizer_returns_state_and_sets_objective() -> None:
    X = holonomic_system_normalizer_v2(_state(), _callbacks(), max_iter=2)
    assert hasattr(X, "J")
    assert X.mode in {"safe", "standard", "deep"}
    assert isinstance(X.couplings, dict)


# ---------------------------------------------------------------------------
# wrap — additional boundary values
# ---------------------------------------------------------------------------

def test_wrap_negative_large_angle() -> None:
    import math
    value = wrap(-5.0)
    assert -math.pi < value <= math.pi


def test_wrap_pi_returns_pi() -> None:
    import math
    assert wrap(math.pi) == math.pi


def test_wrap_zero_returns_zero() -> None:
    assert wrap(0.0) == 0.0


def test_wrap_two_pi_returns_zero() -> None:
    import math
    # 2*pi wraps to 0 (or within principal interval)
    value = wrap(2 * math.pi)
    assert -math.pi < value <= math.pi


# ---------------------------------------------------------------------------
# circular_barycenter — additional cases
# ---------------------------------------------------------------------------

def test_circular_barycenter_uniform_single_angle() -> None:
    import math
    phi = circular_barycenter([math.pi / 4], [1.0])
    assert phi == pytest.approx(math.pi / 4)


def test_circular_barycenter_identical_angles_returns_that_angle() -> None:
    import math
    # Two identical angles: result should equal that angle
    result = circular_barycenter([1.0, 1.0], [0.5, 0.5])
    assert result == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# circular_distance
# ---------------------------------------------------------------------------

def test_circular_distance_antipodal() -> None:
    import math
    d = circular_distance(0.0, math.pi)
    assert d == pytest.approx(math.pi)


def test_circular_distance_symmetric() -> None:
    d1 = circular_distance(0.3, 1.1)
    d2 = circular_distance(1.1, 0.3)
    assert d1 == pytest.approx(d2)


# ---------------------------------------------------------------------------
# renormalize_couplings — additional norms and edge cases
# ---------------------------------------------------------------------------

def test_renormalize_couplings_l2_norm() -> None:
    import math
    couplings = {("a", "b"): 3.0, ("b", "a"): 4.0}
    renorm = renormalize_couplings(couplings, target_norm="l2")
    # l2 norm of [3,4] = 5; each value divided by 5
    expected_sum_sq = (3.0 / 5.0) ** 2 + (4.0 / 5.0) ** 2
    assert abs(expected_sum_sq - 1.0) < 1e-9
    assert renorm[("a", "b")] == pytest.approx(3.0 / 5.0)
    assert renorm[("b", "a")] == pytest.approx(4.0 / 5.0)


def test_renormalize_couplings_invalid_norm_raises() -> None:
    couplings = {("a", "b"): 1.0}
    with pytest.raises(ValueError, match="unsupported target_norm"):
        renormalize_couplings(couplings, target_norm="linf")


def test_renormalize_couplings_empty_returns_empty() -> None:
    assert renormalize_couplings({}) == {}


def test_renormalize_couplings_all_zero_returns_originals() -> None:
    couplings = {("a", "b"): 0.0, ("b", "a"): 0.0}
    result = renormalize_couplings(couplings, target_norm="l1")
    assert result == couplings


# ---------------------------------------------------------------------------
# holonomic_system_normalizer_v2 — mode switching
# ---------------------------------------------------------------------------

def _callbacks_with_distortion() -> HolonomicCallbacks:
    """Callbacks that push the state into 'safe' mode by injecting a lie."""
    return HolonomicCallbacks(
        closure_defect=lambda repo_states: 0.05,
        all_pairwise_tensions=lambda repo_states, couplings: [{"tension": 0.1}],
        compute_placeholder_penalty=lambda objects: 0.0,
        compute_demo_legacy_penalty=lambda objects: 0.0,
        compute_semantic_execution_seam_penalty=lambda X: 0.01,
        object_break_penalty=lambda obj: 0.0,
        seam_local_penalty=lambda X, obj: 0.0,
        local_tension=lambda X, i, j: 0.1,
        recompute_manifests_and_bridge=lambda X: X,
    )


def test_holonomic_normalizer_safe_mode_on_lie() -> None:
    s = _state()
    s.distortion = {"lie": 1.0, "omit": 0.0, "hallucinate": 0.0, "smooth": 0.0}
    X = holonomic_system_normalizer_v2(s, _callbacks_with_distortion(), max_iter=1)
    assert X.mode == "safe"
    assert X.allow_writeback is False


def test_holonomic_normalizer_j_is_nonnegative() -> None:
    X = holonomic_system_normalizer_v2(_state(), _callbacks(), max_iter=3)
    assert float(X.J) >= 0.0


def test_holonomic_normalizer_couplings_clipped() -> None:
    X = holonomic_system_normalizer_v2(_state(), _callbacks(), max_iter=2)
    for v in X.couplings.values():
        assert 0.0 <= v <= 1.0
