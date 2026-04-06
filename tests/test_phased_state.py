"""Tests for src/ciel_sot_agent/phased_state.py.

Covers every public function and the FileState dataclass,
including numeric bounds, edge-cases, and multi-file normalization.
"""
from __future__ import annotations

import math

import pytest

from src.ciel_sot_agent.phased_state import (
    ALPHA,
    B0,
    BETA,
    TYPE_WEIGHTS,
    LAYER_WEIGHTS,
    FileState,
    build_states,
    compute_phase,
    compute_raw_energy,
    f_conn,
    f_seed,
    f_size,
    frac64,
    normalize,
    sha256_seed,
    weight_layer,
    weight_type,
)


# ---------------------------------------------------------------------------
# sha256_seed / frac64
# ---------------------------------------------------------------------------

def test_sha256_seed_produces_32_bytes() -> None:
    seed = sha256_seed("some/path.py", 1024, b"content")
    assert isinstance(seed, bytes)
    assert len(seed) == 32


def test_sha256_seed_is_deterministic() -> None:
    a = sha256_seed("path.py", 100, b"data")
    b = sha256_seed("path.py", 100, b"data")
    assert a == b


def test_sha256_seed_differs_on_different_inputs() -> None:
    a = sha256_seed("a.py", 1, b"x")
    b = sha256_seed("b.py", 1, b"x")
    c = sha256_seed("a.py", 2, b"x")
    d = sha256_seed("a.py", 1, b"y")
    assert len({a, b, c, d}) == 4


def test_frac64_returns_value_in_unit_interval() -> None:
    seed = sha256_seed("test.py", 512, b"hello")
    h = frac64(seed)
    assert 0.0 <= h < 1.0


def test_frac64_is_deterministic() -> None:
    seed = sha256_seed("x.py", 10, b"z")
    assert frac64(seed) == frac64(seed)


# ---------------------------------------------------------------------------
# Component functions f_size, f_conn, f_seed
# ---------------------------------------------------------------------------

def test_f_size_at_zero_is_one() -> None:
    assert f_size(0) == pytest.approx(1.0)


def test_f_size_increases_monotonically() -> None:
    assert f_size(0) < f_size(100) < f_size(10_000)


def test_f_size_uses_alpha_and_b0() -> None:
    expected = 1.0 + ALPHA * math.log(1.0 + 1024 / B0)
    assert f_size(1024) == pytest.approx(expected)


def test_f_conn_at_zero_is_one() -> None:
    assert f_conn(0) == pytest.approx(1.0)


def test_f_conn_increases_monotonically() -> None:
    assert f_conn(0) < f_conn(1) < f_conn(100)


def test_f_conn_uses_beta() -> None:
    expected = 1.0 + BETA * math.log(1.0 + 5)
    assert f_conn(5) == pytest.approx(expected)


def test_f_seed_at_zero() -> None:
    assert f_seed(0.0) == pytest.approx(0.95)


def test_f_seed_at_one() -> None:
    assert f_seed(1.0) == pytest.approx(1.05)


def test_f_seed_midpoint() -> None:
    assert f_seed(0.5) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# weight_type / weight_layer
# ---------------------------------------------------------------------------

def test_weight_type_returns_known_extension() -> None:
    assert weight_type("py") == TYPE_WEIGHTS["py"]
    assert weight_type("json") == TYPE_WEIGHTS["json"]


def test_weight_type_is_case_insensitive() -> None:
    assert weight_type("PY") == weight_type("py")
    assert weight_type("MD") == weight_type("md")


def test_weight_type_unknown_extension_returns_default() -> None:
    # Unknown extension should return the default fallback (0.75)
    result = weight_type("xyz_unknown_ext")
    assert result == 0.75


def test_weight_layer_returns_known_layer() -> None:
    assert weight_layer("contracts") == LAYER_WEIGHTS["contracts"]
    assert weight_layer("tests") == LAYER_WEIGHTS["tests"]


def test_weight_layer_unknown_layer_returns_default() -> None:
    result = weight_layer("completely_unknown_layer")
    assert result == 0.90


# ---------------------------------------------------------------------------
# compute_raw_energy
# ---------------------------------------------------------------------------

def test_compute_raw_energy_is_positive() -> None:
    state = FileState(
        path="src/core/foo.py",
        size=2048,
        ext="py",
        layer="src/core",
        r=3,
        h=0.5,
    )
    energy = compute_raw_energy(state)
    assert energy > 0.0


def test_compute_raw_energy_increases_with_size() -> None:
    def make(size: int) -> FileState:
        return FileState(path="x.py", size=size, ext="py", layer="src/core", r=0, h=0.5)

    assert compute_raw_energy(make(100)) < compute_raw_energy(make(10_000))


def test_compute_raw_energy_increases_with_connections() -> None:
    def make(r: int) -> FileState:
        return FileState(path="x.py", size=1000, ext="py", layer="src/core", r=r, h=0.5)

    assert compute_raw_energy(make(0)) < compute_raw_energy(make(10))


# ---------------------------------------------------------------------------
# normalize
# ---------------------------------------------------------------------------

def test_normalize_sets_e_norm_that_sums_to_one() -> None:
    states = [
        FileState(path=f"f{i}.py", size=100 * (i + 1), ext="py", layer="src/core", r=0, h=0.5)
        for i in range(4)
    ]
    for s in states:
        s.E_raw = float(s.size)

    normalize(states)

    total = sum(s.E_norm for s in states)
    assert total == pytest.approx(1.0)


def test_normalize_sets_amplitude_as_sqrt_of_e_norm() -> None:
    states = [
        FileState(path="a.py", size=100, ext="py", layer="src/core", r=0, h=0.5),
        FileState(path="b.py", size=300, ext="py", layer="src/core", r=0, h=0.5),
    ]
    states[0].E_raw = 1.0
    states[1].E_raw = 3.0

    normalize(states)

    for s in states:
        assert s.a == pytest.approx(math.sqrt(s.E_norm))


def test_normalize_no_op_when_total_is_zero() -> None:
    states = [
        FileState(path="z.py", size=0, ext="py", layer="src/core", r=0, h=0.0)
    ]
    states[0].E_raw = 0.0
    normalize(states)
    # Should not raise; E_norm remains 0
    assert states[0].E_norm == 0.0


# ---------------------------------------------------------------------------
# compute_phase
# ---------------------------------------------------------------------------

def test_compute_phase_maps_zero_to_zero() -> None:
    assert compute_phase(0.0) == 0.0


def test_compute_phase_maps_one_to_two_pi() -> None:
    assert compute_phase(1.0) == pytest.approx(2 * math.pi)


def test_compute_phase_output_within_0_to_2pi() -> None:
    for h in [0.0, 0.25, 0.5, 0.75, 1.0]:
        phi = compute_phase(h)
        assert 0.0 <= phi <= 2 * math.pi + 1e-12


# ---------------------------------------------------------------------------
# build_states — integration of the full pipeline
# ---------------------------------------------------------------------------

def _make_entry(path: str, size: int = 500, ext: str = "py", layer: str = "src/core", r: int = 2) -> dict:
    return {"path": path, "size": size, "ext": ext, "layer": layer, "r": r, "content": path.encode()}


def test_build_states_returns_correct_count() -> None:
    entries = [_make_entry(f"file{i}.py", size=100 * (i + 1)) for i in range(5)]
    states = build_states(entries)
    assert len(states) == 5


def test_build_states_e_norm_sums_to_one() -> None:
    entries = [_make_entry(f"f{i}.py") for i in range(3)]
    states = build_states(entries)
    total = sum(s.E_norm for s in states)
    assert total == pytest.approx(1.0)


def test_build_states_phases_within_0_to_2pi() -> None:
    entries = [_make_entry(f"f{i}.py") for i in range(4)]
    states = build_states(entries)
    for s in states:
        assert 0.0 <= s.phi <= 2 * math.pi + 1e-12


def test_build_states_amplitude_is_sqrt_of_e_norm() -> None:
    entries = [_make_entry(f"f{i}.py") for i in range(3)]
    states = build_states(entries)
    for s in states:
        assert s.a == pytest.approx(math.sqrt(s.E_norm))


def test_build_states_single_entry_has_full_norm() -> None:
    states = build_states([_make_entry("only.py")])
    assert states[0].E_norm == pytest.approx(1.0)
    assert states[0].a == pytest.approx(1.0)


def test_build_states_uses_r_default_zero() -> None:
    entry = {"path": "x.py", "size": 100, "ext": "py", "layer": "src/core", "content": b"x"}
    # No 'r' key — should default to 0
    states = build_states([entry])
    assert states[0].r == 0


def test_build_states_paths_are_preserved() -> None:
    entries = [_make_entry("alpha/beta.json", ext="json", layer="contracts")]
    states = build_states(entries)
    assert states[0].path == "alpha/beta.json"
    assert states[0].ext == "json"
    assert states[0].layer == "contracts"
