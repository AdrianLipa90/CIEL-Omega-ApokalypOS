from __future__ import annotations

from ciel_omega.ciel.orbital_memory_loop import OrbitalLoopResult, build_runtime_policy
from ciel_omega.memory.monolith.data_types import DataVector
from ciel_omega.memory.monolith.orchestrator import UnifiedMemoryOrchestrator
from ciel_omega.memory.monolith.tmp_processor import TMPKernel


def _orbital_result(control_mode: str, severity: str) -> OrbitalLoopResult:
    return OrbitalLoopResult(
        status="ok",
        final={"R_H": 0.2, "closure_penalty": 4.9},
        state_manifest={"coherence_index": 0.8},
        health_manifest={"system_health": 0.7},
        control={"mode": control_mode, "notes": "test", "target_phase_shift": 0.0},
        rh_policy={"mode": "policy", "severity": severity},
        history_length=2,
        params={},
        diagnostics={},
        runtime_signals={},
    )


def test_build_runtime_policy_exposes_thresholds_and_write_gate():
    safe = build_runtime_policy(_orbital_result("safe", "high"))
    deep = build_runtime_policy(_orbital_result("deep", "low"))
    assert safe["durable_write_allowed"] is False
    assert safe["tmp_pass_threshold"] >= 0.82
    assert deep["durable_write_allowed"] is True
    assert deep["tmp_pass_threshold"] < safe["tmp_pass_threshold"]


def test_tmp_kernel_respects_runtime_threshold_overrides(tmp_path):
    kernel = TMPKernel(tmp_path)
    data = DataVector(
        context="runtime",
        sense="This sentence is long enough to pass ordinary TMP scoring with several words.",
        meta={"tmp_hold_threshold": 0.95, "tmp_pass_threshold": 0.99},
    )
    out = kernel.process(data)
    assert out["OUT"]["verdict"] != "PASS"
    assert out["OUT"]["thresholds"]["pass"] == 0.99


def test_promotion_respects_durable_write_gate(tmp_path):
    orchestrator = UnifiedMemoryOrchestrator(
        cfg_dir=tmp_path / "cfg",
        tsm_db=tmp_path / "tsm" / "ledger.db",
        wpm_h5=tmp_path / "wpm" / "archive.h5",
    )
    D = DataVector(
        context="runtime",
        sense="This sentence is long enough to pass ordinary TMP scoring with several words.",
        meta={"trusted_source": True},
    )
    tmp_out = {
        "OUT": {"verdict": "PASS", "bifurcation": 1, "weights": {}},
        "A1": {"D_TYPE": "text", "D_ATTR": {"length": len(str(D.D_S))}},
    }
    denied = orchestrator.promote_if_bifurcated(D, tmp_out, runtime_policy={"durable_write_allowed": False})
    allowed = orchestrator.promote_if_bifurcated(D, tmp_out, runtime_policy={"durable_write_allowed": True})
    assert denied is None
    assert allowed is not None
