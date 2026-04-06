from __future__ import annotations

import cmath
import json
import math
from pathlib import Path

import pytest

from src.ciel_sot_agent.repo_phase import (
    RepositoryState,
    all_pairwise_tensions,
    build_sync_report,
    closure_defect,
    load_couplings,
    load_registry,
    pairwise_tension,
    weighted_euler_vector,
)


def test_closure_defect_zero_for_aligned_states() -> None:
    states = [
        RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'x', 'u'),
        RepositoryState('b', 'B', 0.0, 0.5, 2.0, 'x', 'u'),
    ]
    assert abs(closure_defect(states)) < 1e-12


def test_pairwise_tension_nonnegative() -> None:
    a = RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'x', 'u')
    b = RepositoryState('b', 'B', 1.0, 0.5, 1.0, 'x', 'u')
    assert pairwise_tension(a, b, 0.8) >= 0.0


def test_build_sync_report_smoke(tmp_path: Path) -> None:
    registry = {
        'repositories': [
            {'key': 'a', 'identity': 'A', 'phi': 0.0, 'spin': 0.5, 'mass': 1.0, 'role': 'r', 'upstream': 'u'},
            {'key': 'b', 'identity': 'B', 'phi': 0.0, 'spin': 0.5, 'mass': 1.0, 'role': 'r', 'upstream': 'u'},
        ]
    }
    couplings = {'couplings': {'a': {'b': 1.0}, 'b': {'a': 1.0}}}
    reg_path = tmp_path / 'registry.json'
    coup_path = tmp_path / 'couplings.json'
    reg_path.write_text(json.dumps(registry), encoding='utf-8')
    coup_path.write_text(json.dumps(couplings), encoding='utf-8')
    report = build_sync_report(reg_path, coup_path)
    assert report['repository_count'] == 2
    assert abs(report['closure_defect']) < 1e-12
    assert len(report['pairwise_tensions']) == 2


# ---------------------------------------------------------------------------
# load_registry / load_couplings
# ---------------------------------------------------------------------------

def test_load_registry_reads_all_fields(tmp_path: Path) -> None:
    data = {
        'repositories': [
            {'key': 'r1', 'identity': 'Repo1', 'phi': 1.5, 'spin': 0.4, 'mass': 2.0, 'role': 'lead', 'upstream': 'https://github.com/x'},
        ]
    }
    path = tmp_path / 'reg.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    states = load_registry(path)
    assert 'r1' in states
    s = states['r1']
    assert s.key == 'r1'
    assert s.identity == 'Repo1'
    assert s.phi == pytest.approx(1.5)
    assert s.spin == pytest.approx(0.4)
    assert s.mass == pytest.approx(2.0)
    assert s.role == 'lead'
    assert s.upstream == 'https://github.com/x'


def test_load_registry_empty_repositories(tmp_path: Path) -> None:
    path = tmp_path / 'reg.json'
    path.write_text('{"repositories": []}', encoding='utf-8')
    states = load_registry(path)
    assert states == {}


def test_load_couplings_parses_nested_map(tmp_path: Path) -> None:
    data = {'couplings': {'a': {'b': 0.7, 'c': 0.3}, 'b': {'a': 0.7}}}
    path = tmp_path / 'coup.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    couplings = load_couplings(path)
    assert couplings['a']['b'] == pytest.approx(0.7)
    assert couplings['a']['c'] == pytest.approx(0.3)
    assert couplings['b']['a'] == pytest.approx(0.7)


def test_load_couplings_empty(tmp_path: Path) -> None:
    path = tmp_path / 'coup.json'
    path.write_text('{"couplings": {}}', encoding='utf-8')
    assert load_couplings(path) == {}


# ---------------------------------------------------------------------------
# weighted_euler_vector
# ---------------------------------------------------------------------------

def test_weighted_euler_vector_aligned_gives_real_sum() -> None:
    states = [
        RepositoryState('a', 'A', 0.0, 0.5, 2.0, 'x', 'u'),
        RepositoryState('b', 'B', 0.0, 0.5, 3.0, 'x', 'u'),
    ]
    vec = weighted_euler_vector(states)
    # All phi=0, so e^{i*0}=1; total = 2+3=5
    assert vec == pytest.approx(5.0 + 0j)


def test_weighted_euler_vector_opposite_phases_cancel() -> None:
    # mass 1 at phi=0 and mass 1 at phi=pi should give ~0
    states = [
        RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'x', 'u'),
        RepositoryState('b', 'B', math.pi, 0.5, 1.0, 'x', 'u'),
    ]
    vec = weighted_euler_vector(states)
    assert abs(vec) < 1e-12


def test_weighted_euler_vector_empty_is_zero() -> None:
    assert weighted_euler_vector([]) == 0j


# ---------------------------------------------------------------------------
# closure_defect — additional edge cases
# ---------------------------------------------------------------------------

def test_closure_defect_misaligned_states_is_positive() -> None:
    states = [
        RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'x', 'u'),
        RepositoryState('b', 'B', math.pi, 0.5, 1.0, 'x', 'u'),
    ]
    defect = closure_defect(states)
    assert defect > 0.0


def test_closure_defect_single_state_is_zero() -> None:
    states = [RepositoryState('a', 'A', 0.42, 0.5, 1.0, 'x', 'u')]
    assert closure_defect(states) == pytest.approx(0.0)


def test_closure_defect_empty_states_returns_one() -> None:
    assert closure_defect([]) == pytest.approx(1.0)


def test_closure_defect_all_zero_mass_returns_one() -> None:
    states = [
        RepositoryState('a', 'A', 0.0, 0.5, 0.0, 'x', 'u'),
        RepositoryState('b', 'B', 0.0, 0.5, 0.0, 'x', 'u'),
    ]
    assert closure_defect(states) == pytest.approx(1.0)


def test_closure_defect_in_unit_interval() -> None:
    states = [
        RepositoryState('a', 'A', 0.1, 0.5, 1.0, 'x', 'u'),
        RepositoryState('b', 'B', 2.5, 0.5, 1.5, 'x', 'u'),
        RepositoryState('c', 'C', -1.2, 0.5, 0.8, 'x', 'u'),
    ]
    defect = closure_defect(states)
    assert 0.0 <= defect <= 1.0


# ---------------------------------------------------------------------------
# pairwise_tension — additional cases
# ---------------------------------------------------------------------------

def test_pairwise_tension_same_phase_is_zero() -> None:
    a = RepositoryState('a', 'A', 1.0, 0.5, 1.0, 'x', 'u')
    b = RepositoryState('b', 'B', 1.0, 0.5, 1.0, 'x', 'u')
    assert pairwise_tension(a, b, 1.0) == pytest.approx(0.0)


def test_pairwise_tension_pi_offset_is_maximum() -> None:
    a = RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'x', 'u')
    b = RepositoryState('b', 'B', math.pi, 0.5, 1.0, 'x', 'u')
    # coupling * (1 - cos(pi)) = 1.0 * 2 = 2.0
    assert pairwise_tension(a, b, 1.0) == pytest.approx(2.0)


def test_pairwise_tension_scales_with_coupling() -> None:
    a = RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'x', 'u')
    b = RepositoryState('b', 'B', math.pi / 2, 0.5, 1.0, 'x', 'u')
    assert pairwise_tension(a, b, 2.0) == pytest.approx(2.0 * pairwise_tension(a, b, 1.0))


# ---------------------------------------------------------------------------
# all_pairwise_tensions
# ---------------------------------------------------------------------------

def test_all_pairwise_tensions_skips_missing_states() -> None:
    states = {'a': RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'x', 'u')}
    couplings = {'a': {'b': 0.9}}  # 'b' not in states
    rows = all_pairwise_tensions(states, couplings)
    assert rows == []


def test_all_pairwise_tensions_correct_row_structure() -> None:
    states = {
        'a': RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'x', 'u'),
        'b': RepositoryState('b', 'B', 0.5, 0.5, 1.0, 'x', 'u'),
    }
    couplings = {'a': {'b': 0.8}}
    rows = all_pairwise_tensions(states, couplings)
    assert len(rows) == 1
    row = rows[0]
    assert row['source'] == 'a'
    assert row['target'] == 'b'
    assert row['coupling'] == pytest.approx(0.8)
    assert row['tension'] >= 0.0


def test_all_pairwise_tensions_sorted_by_source_target() -> None:
    states = {
        'a': RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'x', 'u'),
        'b': RepositoryState('b', 'B', 1.0, 0.5, 1.0, 'x', 'u'),
        'c': RepositoryState('c', 'C', 2.0, 0.5, 1.0, 'x', 'u'),
    }
    couplings = {'b': {'a': 0.5, 'c': 0.3}, 'a': {'c': 0.2}}
    rows = all_pairwise_tensions(states, couplings)
    keys = [(r['source'], r['target']) for r in rows]
    assert keys == sorted(keys)


def test_all_pairwise_tensions_empty_couplings_returns_empty() -> None:
    states = {'a': RepositoryState('a', 'A', 0.0, 0.5, 1.0, 'x', 'u')}
    assert all_pairwise_tensions(states, {}) == []


# ---------------------------------------------------------------------------
# build_sync_report — additional assertions
# ---------------------------------------------------------------------------

def test_build_sync_report_euler_vector_keys(tmp_path: Path) -> None:
    registry = {'repositories': [
        {'key': 'x', 'identity': 'X', 'phi': 0.0, 'spin': 0.5, 'mass': 1.0, 'role': 'r', 'upstream': 'u'},
    ]}
    couplings = {'couplings': {}}
    reg = tmp_path / 'r.json'
    coup = tmp_path / 'c.json'
    reg.write_text(json.dumps(registry), encoding='utf-8')
    coup.write_text(json.dumps(couplings), encoding='utf-8')
    report = build_sync_report(reg, coup)
    vec = report['weighted_euler_vector']
    assert 'real' in vec and 'imag' in vec and 'abs' in vec
