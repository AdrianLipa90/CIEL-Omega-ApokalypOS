from __future__ import annotations

import math

from ciel_omega.ciel.engine import CielEngine
from ciel_omega.ciel.orbital_sector_memory import build_orbital_memory_event
from ciel_omega.ciel.orbital_memory_loop import OrbitalLoopConfig, RuntimeOrbitalSignals, run_orbital_loop, build_runtime_policy


def test_build_orbital_memory_event_uses_orbital_geometry():
    orbital = run_orbital_loop(
        OrbitalLoopConfig(
            steps=1,
            write_reports=False,
            pass_label="pytest-sector-memory",
            runtime_signals=RuntimeOrbitalSignals(
                text_length=120,
                context="orbital/audit",
                mood=0.6,
                ethical_score=0.8,
                soul_invariant=0.9,
                simulation_coherence=0.75,
                intention_norm=1.5,
            ),
        )
    )
    policy = build_runtime_policy(orbital)
    event = build_orbital_memory_event(
        text="trace orbital memory into sector",
        context="orbital/audit",
        mood=0.6,
        ethical_score=0.8,
        soul_invariant=0.9,
        orbital=orbital,
        runtime_policy=policy,
    )
    assert 0.0 <= event["phase"] < 2.0 * math.pi
    assert event["context"]["pipeline"] == "relation->orbital->orchestration->reduction->memory"
    assert event["context"]["dominant_residual_sector"] == orbital.diagnostics.get("dominant_residual_sector")
    assert event["result"]["response_strategy"] == policy["response_strategy"]


def test_engine_step_records_orbital_sector_memory():
    engine = CielEngine()
    out1 = engine.step("connect orbital memory with runtime traces", context="orbital/test")
    out2 = engine.step("connect orbital memory with runtime traces again", context="orbital/test")

    assert out1["status"] == "ok"
    assert "sector_memory" in out1
    assert out1["sector_memory"]["cycle"]["content"] == "connect orbital memory with runtime traces"
    assert out1["sector_memory"]["event"]["context"]["control_mode"] == out1["runtime_policy"]["control_mode"]
    assert out1["sector_memory"]["snapshot"]["counts"]["m2_episodes"] >= 1
    assert out2["sector_memory"]["snapshot"]["cycle_index"] == out1["sector_memory"]["snapshot"]["cycle_index"] + 1
    assert out2["sector_memory"]["snapshot"]["counts"]["m7_units"] >= out1["sector_memory"]["snapshot"]["counts"]["m7_units"]
