from __future__ import annotations

from ciel_omega.ciel.engine import CielEngine
from ciel_omega.ciel.orbital_memory_loop import OrbitalLoopConfig, RuntimeOrbitalSignals, run_orbital_loop
from ciel_omega.orbital.global_pass import run_global_pass


def test_global_pass_runs_in_snapshot_layout():
    result = run_global_pass(steps=1, pass_label="pytest")
    final = result["final"]
    assert "R_H" in final
    assert "closure_penalty" in final
    assert result["steps"] == 1


def test_orbital_loop_produces_control_and_health():
    result = run_orbital_loop()
    assert result.status in {"ok", "degraded"}
    assert "mode" in result.control
    if result.status == "ok":
        assert "coherence_index" in result.state_manifest
        assert "system_health" in result.health_manifest


def test_engine_step_bridges_orbital_runtime_memory():
    engine = CielEngine()
    out = engine.step("bridge orbital runtime memory")
    assert out["status"] == "ok"
    assert "orbital" in out
    assert "runtime_policy" in out
    assert "memory_meta" in out
    assert out["memory_meta"]["orbital_control_mode"] == out["runtime_policy"]["control_mode"]
    assert out["orbital"]["status"] in {"ok", "degraded"}
    assert out["tmp_outcome"]["OUT"]["verdict"] in {"PASS", "HOLD", "FAIL"}


def test_orbital_loop_emits_rh_policy_and_control_alignment():
    result = run_orbital_loop(OrbitalLoopConfig(steps=1, write_reports=False, pass_label="pytest-loop"))
    assert result.status in {"ok", "degraded"}
    assert "mode" in result.rh_policy
    assert "severity" in result.rh_policy
    if result.status == "ok":
        assert result.control["rh_mode"] == result.rh_policy["mode"]
        assert result.control["rh_severity"] == result.rh_policy["severity"]



def test_orbital_loop_uses_runtime_signals_to_change_effective_params():
    light = run_orbital_loop(
        OrbitalLoopConfig(
            steps=2,
            write_reports=False,
            pass_label="pytest-light",
            runtime_signals=RuntimeOrbitalSignals(
                text_length=24,
                context="research",
                mood=0.55,
                ethical_score=0.75,
                soul_invariant=0.95,
                simulation_coherence=0.85,
                intention_norm=0.8,
            ),
        )
    )
    heavy = run_orbital_loop(
        OrbitalLoopConfig(
            steps=2,
            write_reports=False,
            pass_label="pytest-heavy",
            runtime_signals=RuntimeOrbitalSignals(
                text_length=420,
                context="dialogue",
                mood=0.95,
                ethical_score=0.35,
                soul_invariant=0.35,
                simulation_coherence=0.25,
                intention_norm=5.0,
            ),
        )
    )
    assert light.params != heavy.params
    assert light.final["R_H"] < heavy.final["R_H"]
    assert light.runtime_signals["context"] == "research"


def test_global_pass_exposes_sector_diagnostics():
    result = run_global_pass(steps=1, write_reports=False, pass_label="pytest-diag")
    diagnostics = result["diagnostics"]
    assert "closure_residuals" in diagnostics
    assert diagnostics["dominant_residual_sector"] in diagnostics["closure_residuals"]
