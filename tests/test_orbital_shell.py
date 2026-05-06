"""Tests for the orbital shell memory model (OrbitalRecord + OrbitalShellIndex)."""
from __future__ import annotations

import math
import sys
import types
import importlib.util
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Bootstrap: load orbital_shell without triggering broken ciel_omega __init__
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
_OMEGA = _ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"

def _load_orbital_shell():
    sys.path.insert(0, str(_OMEGA))
    pkg = types.ModuleType("ciel_omega")
    pkg.__path__ = [str(_OMEGA / "ciel_omega")]
    pkg.__package__ = "ciel_omega"
    sys.modules.setdefault("ciel_omega", pkg)
    mem = types.ModuleType("ciel_omega.memory")
    mem.__path__ = [str(_OMEGA / "ciel_omega" / "memory")]
    mem.__package__ = "ciel_omega.memory"
    sys.modules.setdefault("ciel_omega.memory", mem)
    mod_path = _OMEGA / "ciel_omega" / "memory" / "orbital_shell.py"
    spec = importlib.util.spec_from_file_location("ciel_omega.memory.orbital_shell", mod_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ciel_omega.memory.orbital_shell"] = mod
    spec.loader.exec_module(mod)
    return mod

_m = _load_orbital_shell()
OrbitalRecord = _m.OrbitalRecord
OrbitalShellIndex = _m.OrbitalShellIndex
phase_distance = _m.phase_distance
compute_E_bind = _m.compute_E_bind
shell_from_E_bind = _m.shell_from_E_bind
SHELL_NAMES = _m.SHELL_NAMES
SHELL_CAPACITY = _m.SHELL_CAPACITY
G_SEM = _m.G_SEM
M_ATTRACTOR = _m.M_ATTRACTOR


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

class TestPhaseDistance:
    def test_same_phase_is_zero(self):
        assert phase_distance(1.0, 1.0) == 0.0

    def test_opposite_phases_is_pi(self):
        assert phase_distance(0.0, math.pi) == pytest.approx(math.pi, abs=1e-9)

    def test_wrap_symmetry(self):
        assert phase_distance(0.1, -0.1) == pytest.approx(phase_distance(-0.1, 0.1))


class TestComputeEBind:
    def test_negative_for_positive_r(self):
        assert compute_E_bind(0.5) < 0.0

    def test_singularity_clip(self):
        E_zero = compute_E_bind(0.0)
        assert math.isfinite(E_zero)

    def test_deeper_binding_at_smaller_r(self):
        assert compute_E_bind(0.1) < compute_E_bind(1.0)


class TestShellFromEBind:
    def test_unbound_maps_to_shell_8(self):
        assert shell_from_E_bind(0.0) == 8
        assert shell_from_E_bind(1.0) == 8

    def test_small_r_maps_to_inner_shell(self):
        E_inner = compute_E_bind(0.05)
        assert shell_from_E_bind(E_inner) <= 2

    def test_large_r_maps_to_outer_shell(self):
        E_outer = compute_E_bind(math.pi * 0.9)
        assert shell_from_E_bind(E_outer) >= 7

    def test_monotone(self):
        phis = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5]
        shells = [shell_from_E_bind(compute_E_bind(p)) for p in phis]
        assert shells == sorted(shells)


# ---------------------------------------------------------------------------
# OrbitalRecord
# ---------------------------------------------------------------------------

class TestOrbitalRecord:
    def test_from_phase_creates_valid_record(self):
        rec = OrbitalRecord.from_phase("r1", "content", 0.3, 0.0)
        assert 0 <= rec.shell <= 8
        assert rec.E_bind < 0
        assert rec.r_phase > 0
        assert rec.record_id == "r1"

    def test_attractor_at_same_phase_gives_small_r(self):
        rec = OrbitalRecord.from_phase("r2", "x", 0.5, 0.5)
        assert rec.r_phase < 1e-4

    def test_modal_hash_in_range(self):
        rec = OrbitalRecord.from_phase("r3", "x", 1.0, 0.0)
        assert 0 <= rec.modal_hash < 256


# ---------------------------------------------------------------------------
# OrbitalShellIndex
# ---------------------------------------------------------------------------

class TestOrbitalShellIndex:
    def _make_idx(self) -> OrbitalShellIndex:
        return OrbitalShellIndex(attractor_phase=0.0)

    def test_insert_returns_none_when_not_full(self):
        idx = self._make_idx()
        rec = OrbitalRecord.from_phase("r1", "x", 1.0, 0.0)
        assert idx.insert(rec) is None

    def test_insert_evicts_loosest_when_full(self):
        idx = self._make_idx()
        # Shell K (0) has capacity 2 — insert 3 records at similar phases
        recs = [OrbitalRecord.from_phase(f"r{i}", "x", 0.05 + i * 0.001, 0.0) for i in range(3)]
        results = [idx.insert(r) for r in recs]
        evicted = [r for r in results if r is not None]
        assert len(evicted) >= 1

    def test_get_by_id(self):
        idx = self._make_idx()
        rec = OrbitalRecord.from_phase("unique_id", "data", 1.5, 0.0)
        idx.insert(rec)
        found = idx.get("unique_id")
        assert found is not None
        assert found.record_id == "unique_id"

    def test_get_missing_returns_none(self):
        idx = self._make_idx()
        assert idx.get("nonexistent") is None

    def test_retrieve_returns_at_most_n(self):
        idx = self._make_idx()
        for i in range(6):
            rec = OrbitalRecord.from_phase(f"r{i}", "x", 0.5 + i * 0.3, 0.0)
            idx.insert(rec)
        results = idx.retrieve(phi_query=0.6, n=3)
        assert len(results) <= 3

    def test_retrieve_no_duplicates(self):
        idx = self._make_idx()
        for i in range(8):
            idx.insert(OrbitalRecord.from_phase(f"r{i}", "x", 0.1 * i, 0.0))
        results = idx.retrieve(phi_query=0.3, n=5)
        ids = [r.record_id for r in results]
        assert len(ids) == len(set(ids))

    def test_shell_summary_counts_correct(self):
        idx = self._make_idx()
        for phi in [0.1, 1.0, 2.5]:
            idx.insert(OrbitalRecord.from_phase(f"r{phi}", "x", phi, 0.0))
        summary = idx.shell_summary()
        total = sum(v["count"] for v in summary.values())
        assert total == 3

    def test_shell_capacity_not_exceeded(self):
        idx = self._make_idx()
        # Flood every shell with far more records than capacity
        for i in range(50):
            phi = (i / 50.0) * math.pi * 1.9
            idx.insert(OrbitalRecord.from_phase(f"flood_{i}", "x", phi, 0.0))
        summary = idx.shell_summary()
        for shell_idx, cap in SHELL_CAPACITY.items():
            name = SHELL_NAMES[shell_idx]
            assert summary[name]["count"] <= cap, f"Shell {name} over capacity"

    def test_pauli_exclusion_condenses_duplicate(self):
        idx = self._make_idx()
        # Two records at identical phase → same modal_hash → one condenses inward
        rec_a = OrbitalRecord.from_phase("pa", "x", 1.0, 0.0)
        rec_b = OrbitalRecord.from_phase("pb", "y", 1.0, 0.0)
        idx.insert(rec_a)
        idx.insert(rec_b)
        # At least one must be condensed or on a different shell
        a = idx.get("pa")
        b = idx.get("pb")
        if a and b:
            assert a.shell != b.shell or a.condensed or b.condensed

    def test_retrieve_prefers_shell_matching_query_energy(self):
        idx = self._make_idx()
        inner = OrbitalRecord.from_phase("inner", "x", 0.1, 0.0)   # K shell
        outer = OrbitalRecord.from_phase("outer", "x", 2.8, 0.0)   # S shell
        idx.insert(inner)
        idx.insert(outer)
        results_inner = idx.retrieve(phi_query=0.15, n=1)
        results_outer = idx.retrieve(phi_query=2.7, n=1)
        assert results_inner[0].record_id == "inner"
        assert results_outer[0].record_id == "outer"
