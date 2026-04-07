import math

import pytest

from src.ciel_sot_agent.phased_state import BETA, compute_phase, f_conn


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
