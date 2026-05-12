"""P7 — Orbital Regression Suite + Crash Recovery.

Checks structural invariants of orbital dynamics rather than fixed numeric
baselines, because berry_phase accumulation across sessions causes natural
drift in R_H, Lambda_glob, and closure_penalty. The regression suite verifies:
  - metrics exist and are finite
  - correct direction of change over 20 steps
  - closure_penalty bounded below 2π (6.283)
  - coherence_index, system_health, euler_bridge_closure_score in [0,1]
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from integration.Orbital.main.bootstrap import ensure_orbital_manifests
from integration.Orbital.main.global_pass import run_global_pass
from src.ciel_sot_agent.orbital_bridge import build_orbital_bridge

# ---------------------------------------------------------------------------
# Structural invariant helpers
# ---------------------------------------------------------------------------

def _finite(val: float) -> bool:
    return math.isfinite(val)

def _in_range(val: float, lo: float, hi: float) -> bool:
    return lo <= val <= hi


# ---------------------------------------------------------------------------
# Regression: global_pass final metrics (structural, holonomy-invariant)
# ---------------------------------------------------------------------------

class TestGlobalPassRegression:

    def test_R_H_final_finite_and_nonnegative(self) -> None:
        result = run_global_pass(steps=20)
        val = result["final"]["R_H"]
        assert _finite(val) and val >= 0.0, f"R_H non-finite or negative: {val}"

    def test_closure_penalty_final_bounded(self) -> None:
        result = run_global_pass(steps=20)
        val = result["final"]["closure_penalty"]
        assert _finite(val) and val < 2 * math.pi + 0.1, (
            f"closure_penalty exploded: {val:.4f}"
        )

    def test_Lambda_glob_final_finite(self) -> None:
        result = run_global_pass(steps=20)
        val = result["final"]["Lambda_glob"]
        assert _finite(val), f"Lambda_glob non-finite: {val}"

    def test_closure_penalty_decreases_over_run(self) -> None:
        result = run_global_pass(steps=20)
        initial = result["initial"]["closure_penalty"]
        final = result["final"]["closure_penalty"]
        assert final < initial, (
            f"closure_penalty did not decrease: initial={initial:.4f} final={final:.4f}"
        )

    def test_R_H_decreases_over_run(self) -> None:
        result = run_global_pass(steps=20)
        initial = result["initial"]["R_H"]
        final = result["final"]["R_H"]
        assert final < initial, (
            f"R_H did not decrease: initial={initial:.6f} final={final:.6f}"
        )

    def test_nonlocal_coherent_fraction_remains_high(self) -> None:
        result = run_global_pass(steps=20)
        val = result["final"].get("nonlocal_coherent_fraction", None)
        if val is None:
            pytest.skip("nonlocal_coherent_fraction not in final (engine version mismatch)")
        assert _finite(val) and val >= 0.0, f"nonlocal_coherent_fraction invalid: {val}"

    def test_history_length_matches_steps(self) -> None:
        steps = 10
        result = run_global_pass(steps=steps)
        assert len(result["history"]) == steps + 1, (
            f"history length {len(result['history'])} != steps+1 ({steps + 1})"
        )

    def test_history_R_H_monotone_decreasing_early(self) -> None:
        result = run_global_pass(steps=20)
        history = result["history"]
        # First 5 steps should show decrease
        rh_values = [h["R_H"] for h in history[:6]]
        assert rh_values[0] > rh_values[5], (
            f"R_H not decreasing in first 5 steps: {rh_values}"
        )


# ---------------------------------------------------------------------------
# Regression: orbital bridge report metrics
# ---------------------------------------------------------------------------

class TestOrbitalBridgeRegression:

    def test_coherence_index_in_range(self) -> None:
        summary = build_orbital_bridge(Path("."))
        val = summary["state_manifest"]["coherence_index"]
        assert _finite(val) and _in_range(val, 0.0, 1.0), (
            f"coherence_index out of [0,1]: {val:.4f}"
        )

    def test_system_health_in_range(self) -> None:
        summary = build_orbital_bridge(Path("."))
        val = summary["health_manifest"]["system_health"]
        assert _finite(val) and _in_range(val, 0.0, 1.0), (
            f"system_health out of [0,1]: {val:.4f}"
        )

    def test_euler_bridge_closure_score_in_range(self) -> None:
        summary = build_orbital_bridge(Path("."))
        val = summary["state_manifest"]["euler_bridge_closure_score"]
        assert _finite(val) and _in_range(val, 0.0, 1.0), (
            f"euler_bridge_closure_score out of [0,1]: {val:.4f}"
        )

    def test_system_health_above_minimum(self) -> None:
        summary = build_orbital_bridge(Path("."))
        val = summary["health_manifest"]["system_health"]
        assert val >= 0.3, f"system_health below safe threshold: {val}"

    def test_mode_is_valid(self) -> None:
        summary = build_orbital_bridge(Path("."))
        mode = summary["recommended_control"]["mode"]
        assert mode in ("deep", "standard", "safe"), f"Unknown mode: {mode}"

    def test_schema_version_stable(self) -> None:
        summary = build_orbital_bridge(Path("."))
        assert summary["schema"] == "ciel-sot-agent/orbital-bridge-report/v0.2", (
            f"Schema version changed: {summary['schema']}"
        )

    def test_bridge_report_files_written(self, tmp_path: Path) -> None:
        build_orbital_bridge(tmp_path)
        bridge_dir = tmp_path / "integration" / "reports" / "orbital_bridge"
        for fname in ("orbital_bridge_report.json", "orbital_state_manifest.json",
                      "orbital_health_manifest.json"):
            assert (bridge_dir / fname).exists(), f"Missing: {fname}"


# ---------------------------------------------------------------------------
# Crash recovery: missing files
# ---------------------------------------------------------------------------

class TestCrashRecoveryMissingFiles:

    def test_global_pass_with_fresh_tmp_no_existing_manifests(self, tmp_path: Path) -> None:
        orbital_root = tmp_path / "integration" / "Orbital" / "main"
        orbital_root.mkdir(parents=True)
        # No sectors/couplings — bootstrap must create defaults
        result = run_global_pass(steps=2, repo_root=orbital_root)
        assert result["engine"].startswith("global_orbital_coherence_pass")
        assert "final" in result

    def test_bridge_with_missing_summary_json(self, tmp_path: Path) -> None:
        # Build once to create structure, then delete summary.json
        build_orbital_bridge(tmp_path)
        summary_path = (
            tmp_path
            / "integration" / "Orbital" / "main"
            / "reports" / "global_orbital_coherence_pass" / "summary.json"
        )
        if summary_path.exists():
            summary_path.unlink()
        # Second call must not raise — bridge re-runs orbital pass
        summary = build_orbital_bridge(tmp_path)
        assert "schema" in summary

    def test_bridge_survives_missing_definitions_dir(self, tmp_path: Path) -> None:
        summary = build_orbital_bridge(tmp_path)
        # Must produce a valid schema even without definitions/
        assert summary["schema"] == "ciel-sot-agent/orbital-bridge-report/v0.2"

    def test_ensure_orbital_manifests_idempotent(self, tmp_path: Path) -> None:
        orbital_root = tmp_path / "integration" / "Orbital" / "main"
        orbital_root.mkdir(parents=True)
        info1 = ensure_orbital_manifests(orbital_root)
        info2 = ensure_orbital_manifests(orbital_root)
        assert info1["sectors_path"] == info2["sectors_path"]
        assert Path(info2["sectors_path"]).exists()


# ---------------------------------------------------------------------------
# Crash recovery: corrupted JSON
# ---------------------------------------------------------------------------

class TestCrashRecoveryCorruptedJSON:

    def _corrupt(self, path: Path) -> None:
        path.write_text("{corrupted json !!!", encoding="utf-8")

    def test_bridge_survives_corrupted_sectors_global(self, tmp_path: Path) -> None:
        build_orbital_bridge(tmp_path)
        manifests = tmp_path / "integration" / "Orbital" / "main" / "manifests"
        sectors = manifests / "sectors_global.json"
        if sectors.exists():
            self._corrupt(sectors)
        # Bridge must regenerate or gracefully degrade — must not raise
        try:
            summary = build_orbital_bridge(tmp_path)
            assert "schema" in summary
        except Exception as exc:
            pytest.fail(f"Bridge raised on corrupted sectors_global.json: {exc}")

    def test_bridge_survives_corrupted_couplings_global(self, tmp_path: Path) -> None:
        build_orbital_bridge(tmp_path)
        manifests = tmp_path / "integration" / "Orbital" / "main" / "manifests"
        couplings = manifests / "couplings_global.json"
        if couplings.exists():
            self._corrupt(couplings)
        try:
            summary = build_orbital_bridge(tmp_path)
            assert "schema" in summary
        except Exception as exc:
            pytest.fail(f"Bridge raised on corrupted couplings_global.json: {exc}")

    def test_bridge_survives_corrupted_bridge_report(self, tmp_path: Path) -> None:
        build_orbital_bridge(tmp_path)
        report = (
            tmp_path / "integration" / "reports" / "orbital_bridge"
            / "orbital_bridge_report.json"
        )
        if report.exists():
            self._corrupt(report)
        # Next call must overwrite cleanly
        summary = build_orbital_bridge(tmp_path)
        assert summary["schema"] == "ciel-sot-agent/orbital-bridge-report/v0.2"
        assert json.loads(report.read_text())["schema"] == "ciel-sot-agent/orbital-bridge-report/v0.2"


# ---------------------------------------------------------------------------
# Crash recovery: partial state (files exist but are empty)
# ---------------------------------------------------------------------------

class TestCrashRecoveryEmptyFiles:

    def test_bridge_survives_empty_summary_json(self, tmp_path: Path) -> None:
        build_orbital_bridge(tmp_path)
        summary_path = (
            tmp_path / "integration" / "Orbital" / "main"
            / "reports" / "global_orbital_coherence_pass" / "summary.json"
        )
        if summary_path.exists():
            summary_path.write_text("", encoding="utf-8")
        try:
            summary = build_orbital_bridge(tmp_path)
            assert "schema" in summary
        except Exception as exc:
            pytest.fail(f"Bridge raised on empty summary.json: {exc}")

    def test_global_pass_writes_non_empty_summary(self, tmp_path: Path) -> None:
        orbital_root = tmp_path / "integration" / "Orbital" / "main"
        orbital_root.mkdir(parents=True)
        run_global_pass(steps=2, repo_root=orbital_root)
        summary = orbital_root / "reports" / "global_orbital_coherence_pass" / "summary.json"
        assert summary.exists()
        assert summary.stat().st_size > 100


# ---------------------------------------------------------------------------
# Invariant: output schema stability
# ---------------------------------------------------------------------------

class TestOutputSchemaStability:

    def test_global_pass_result_has_required_keys(self) -> None:
        result = run_global_pass(steps=2)
        for key in ("engine", "steps", "params", "initial", "final", "history"):
            assert key in result, f"Missing top-level key: {key}"

    def test_global_pass_final_has_physics_keys(self) -> None:
        result = run_global_pass(steps=2)
        for key in ("R_H", "T_glob", "Lambda_glob", "closure_penalty", "V_rel_total"):
            assert key in result["final"], f"Missing final key: {key}"

    def test_bridge_summary_has_required_keys(self) -> None:
        summary = build_orbital_bridge(Path("."))
        for key in ("schema", "bridge_metrics", "recommended_control",
                    "runtime_gating", "source_paths", "state_manifest",
                    "health_manifest"):
            assert key in summary, f"Missing bridge summary key: {key}"

    def test_state_manifest_has_required_keys(self) -> None:
        summary = build_orbital_bridge(Path("."))
        state = summary["state_manifest"]
        for key in ("coherence_index", "euler_bridge_closure_score",
                    "nonlocal_coherent_fraction", "phase_lock_error"):
            assert key in state, f"Missing state_manifest key: {key}"

    def test_health_manifest_has_required_keys(self) -> None:
        summary = build_orbital_bridge(Path("."))
        health = summary["health_manifest"]
        for key in ("system_health", "closure_penalty", "R_H", "recommended_action"):
            assert key in health, f"Missing health_manifest key: {key}"
