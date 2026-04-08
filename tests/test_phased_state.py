import math

import pytest

from src.ciel_sot_agent.phased_state import (
    ANCHOR_BETA,
    BETA,
    FLOW_BETA,
    FileState,
    build_states,
    compute_phase,
    f_anchor,
    f_conn,
    f_flow,
    relational_relevance,
)


def test_compute_phase_accepts_hash_fraction_in_unit_interval():
    assert math.isclose(compute_phase(0.0), 0.0)
    assert math.isclose(compute_phase(0.25), math.pi / 2)
    assert math.isclose(compute_phase(0.5), math.pi)


def test_compute_phase_rejects_out_of_range_hash_fraction():
    with pytest.raises(ValueError):
        compute_phase(-0.01)

    with pytest.raises(ValueError):
        compute_phase(1.0)


def test_compute_phase_rejects_non_finite_or_non_numeric_values():
    for value in (float("nan"), float("inf"), -float("inf")):
        with pytest.raises(ValueError):
            compute_phase(value)

    for value in ("0.25", True, None):
        with pytest.raises(TypeError):
            compute_phase(value)


def test_f_conn_accepts_non_negative_integer_connection_count():
    assert math.isclose(f_conn(0), 1.0)
    assert math.isclose(f_conn(3), 1.0 + BETA * math.log(4.0))


def test_f_conn_rejects_negative_connection_count():
    with pytest.raises(ValueError):
        f_conn(-1)


def test_f_conn_rejects_non_integer_connection_count():
    for value in (1.5, "2", True, None):
        with pytest.raises(TypeError):
            f_conn(value)


def test_relational_relevance_uses_relational_features_not_hash_fraction():
    state_a = FileState(
        path="same.py",
        size=128,
        ext="py",
        layer="src/core",
        r=3,
        h=0.11,
        provenance_weight=1.2,
        anchor_count=2,
        upstream_count=1,
        downstream_count=4,
        sector_role_weight=1.1,
    )
    state_b = FileState(
        path="same.py",
        size=128,
        ext="py",
        layer="src/core",
        r=3,
        h=0.91,
        provenance_weight=1.2,
        anchor_count=2,
        upstream_count=1,
        downstream_count=4,
        sector_role_weight=1.1,
    )

    assert math.isclose(relational_relevance(state_a), relational_relevance(state_b))


def test_relational_relevance_increases_with_anchor_and_flow_metadata():
    base = FileState(path="a.py", size=128, ext="py", layer="src/core", r=1, h=0.2)
    richer = FileState(
        path="a.py",
        size=128,
        ext="py",
        layer="src/core",
        r=1,
        h=0.2,
        anchor_count=3,
        upstream_count=2,
        downstream_count=1,
    )

    assert math.isclose(f_anchor(0), 1.0)
    assert math.isclose(f_anchor(3), 1.0 + ANCHOR_BETA * math.log(4.0))
    assert math.isclose(f_flow(2, 1), 1.0 + FLOW_BETA * math.log(4.0))
    assert relational_relevance(richer) > relational_relevance(base)


def test_relational_relevance_rejects_invalid_metadata():
    bad_anchor = FileState(path="a.py", size=128, ext="py", layer="src/core", r=1, h=0.2, anchor_count=-1)
    with pytest.raises(ValueError):
        relational_relevance(bad_anchor)

    bad_weight = FileState(path="a.py", size=128, ext="py", layer="src/core", r=1, h=0.2, provenance_weight=0.0)
    with pytest.raises(ValueError):
        relational_relevance(bad_weight)


def test_build_states_separates_identity_phase_from_selection_weight():
    entries = [
        {
            "path": "same.py",
            "size": 3,
            "content": b"abc",
            "ext": "py",
            "layer": "src/core",
            "r": 2,
            "anchor_count": 1,
            "upstream_count": 1,
            "downstream_count": 1,
            "provenance_weight": 1.1,
            "sector_role_weight": 1.0,
        },
        {
            "path": "same.py",
            "size": 3,
            "content": b"xyz",
            "ext": "py",
            "layer": "src/core",
            "r": 2,
            "anchor_count": 1,
            "upstream_count": 1,
            "downstream_count": 1,
            "provenance_weight": 1.1,
            "sector_role_weight": 1.0,
        },
    ]

    states = build_states(entries)

    assert len(states) == 2
    assert states[0].phi != states[1].phi
    assert math.isclose(states[0].selection_weight, states[1].selection_weight)
    assert math.isclose(states[0].E_raw, states[1].E_raw)
    assert math.isclose(states[0].a, states[1].a)
