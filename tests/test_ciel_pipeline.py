"""Tests for src.ciel_sot_agent.ciel_pipeline."""
from __future__ import annotations

from pathlib import Path

import pytest
import sqlite3

from src.ciel_sot_agent.ciel_pipeline import (
    _orbital_state_to_context,
    run_ciel_pipeline,
)
from src.ciel_sot_agent.phase_snapshots import build_phase_snapshot, build_qualisensing_snapshot
from src.ciel_sot_agent.thought_fragments import (
    assess_durable_memory_health,
    build_cognitive_fragment,
    build_noema_memory_link,
    build_memory_candidate,
    promote_memory_candidate,
    snapshot_to_dict,
)


# ---------------------------------------------------------------------------
# _orbital_state_to_context
# ---------------------------------------------------------------------------

def test_orbital_state_to_context_contains_mode() -> None:
    ctx = _orbital_state_to_context({"mode": "deep", "R_H": 0.9, "closure_penalty": 0.1})
    assert "mode=deep" in ctx


def test_orbital_state_to_context_contains_r_h() -> None:
    ctx = _orbital_state_to_context({"R_H": 0.75, "closure_penalty": 0.05})
    assert "R_H=0.7500" in ctx


def test_orbital_state_to_context_defaults_to_standard_mode() -> None:
    ctx = _orbital_state_to_context({})
    assert "mode=standard" in ctx


def test_orbital_state_to_context_contains_chirality() -> None:
    ctx = _orbital_state_to_context({"Lambda_glob": 1.23})
    assert "chirality=1.2300" in ctx


# ---------------------------------------------------------------------------
# run_ciel_pipeline — smoke tests (uses real CielEngine)
# ---------------------------------------------------------------------------

def test_run_ciel_pipeline_returns_expected_keys() -> None:
    result = run_ciel_pipeline({})
    for key in ("ciel_status", "dominant_emotion", "mood", "soul_invariant", "ethical_score", "orbital_context"):
        assert key in result, f"Missing key: {key}"


def test_run_ciel_pipeline_status_ok() -> None:
    result = run_ciel_pipeline({})
    assert result["ciel_status"] == "ok"


def test_run_ciel_pipeline_mood_in_range() -> None:
    result = run_ciel_pipeline({})
    assert 0.0 <= result["mood"] <= 1.0


def test_run_ciel_pipeline_soul_invariant_is_float() -> None:
    result = run_ciel_pipeline({})
    assert isinstance(result["soul_invariant"], float)


def test_run_ciel_pipeline_ethical_score_non_negative() -> None:
    result = run_ciel_pipeline({})
    assert result["ethical_score"] >= 0.0


def test_run_ciel_pipeline_orbital_context_is_string() -> None:
    result = run_ciel_pipeline({})
    assert isinstance(result["orbital_context"], str)
    assert "orbital" in result["orbital_context"]


def test_run_ciel_pipeline_uses_bridge_metrics_r_h() -> None:
    orbital_state = {"bridge_metrics": {"orbital_R_H": 0.88}}
    result = run_ciel_pipeline(orbital_state)
    assert "R_H=0.8800" in result["orbital_context"]


def test_run_ciel_pipeline_uses_recommended_control_mode() -> None:
    orbital_state = {"recommended_control": {"mode": "deep"}}
    result = run_ciel_pipeline(orbital_state)
    assert "mode=deep" in result["orbital_context"]


def test_run_ciel_pipeline_accepts_explicit_root(tmp_path: Path) -> None:
    # Should still work because CielEngine is already initialised as a singleton.
    result = run_ciel_pipeline({}, root=Path("."))
    assert result["ciel_status"] == "ok"


def test_run_ciel_pipeline_ciel_raw_present() -> None:
    result = run_ciel_pipeline({})
    assert "ciel_raw" in result
    assert isinstance(result["ciel_raw"], dict)


def test_run_ciel_pipeline_exposes_j_and_memory_projection_keys() -> None:
    orbital_state = {
        "memory_projection": {
            "projection_confidence": 0.8,
            "projection_residual": 0.2,
            "projection_error": 0.2,
            "j_noema": 0.34,
        }
    }
    result = run_ciel_pipeline(orbital_state)
    for key in ("J_functional", "J_memory", "J_euler", "J_total", "j_noema", "memory_projection_confidence", "lingo_frame", "lingo_phase_projection", "lingo_tau_bridge", "lingo_tau_gradient_mean", "lingo_imaginal_drive"):
        assert key in result
    assert isinstance(result["lingo_frame"], dict)
    assert isinstance(result["lingo_phase_projection"], dict)
    assert isinstance(result["lingo_tau_bridge"], dict)


def test_run_ciel_pipeline_exposes_phase_and_qualisensing_snapshots() -> None:
    result = run_ciel_pipeline({})

    assert "phase_snapshot" in result
    assert "qualisensing_snapshot" in result
    assert isinstance(result["phase_snapshot"], dict)
    assert isinstance(result["qualisensing_snapshot"], dict)

    phase_snapshot = result["phase_snapshot"]
    qualisensing_snapshot = result["qualisensing_snapshot"]

    assert phase_snapshot["phase_snapshot_id"]
    assert qualisensing_snapshot["qualisensing_id"]
    assert qualisensing_snapshot["phase_snapshot_id"] == phase_snapshot["phase_snapshot_id"]


def test_run_ciel_pipeline_exposes_cognitive_fragment_and_candidate() -> None:
    result = run_ciel_pipeline({})

    assert "cognitive_fragment" in result
    assert "memory_candidate" in result
    assert "durable_memory_object" in result
    assert "noema_memory_link" in result
    assert "durable_memory_health" in result
    assert isinstance(result["cognitive_fragment"], dict)
    assert isinstance(result["memory_candidate"], dict)
    assert isinstance(result["durable_memory_object"], dict)
    assert isinstance(result["noema_memory_link"], dict)
    assert isinstance(result["durable_memory_health"], dict)

    fragment = result["cognitive_fragment"]
    candidate = result["memory_candidate"]
    durable = result["durable_memory_object"]
    link = result["noema_memory_link"]
    health = result["durable_memory_health"]

    assert fragment["fragment_id"]
    assert fragment["phase_snapshot_id"] == result["phase_snapshot"]["phase_snapshot_id"]
    assert fragment["qualisensing_id"] == result["qualisensing_snapshot"]["qualisensing_id"]
    assert candidate["candidate_id"]
    assert candidate["fragment_refs"] == [fragment["fragment_id"]]
    assert candidate["phase_snapshot_refs"] == [result["phase_snapshot"]["phase_snapshot_id"]]
    assert candidate["qualisensing_refs"] == [result["qualisensing_snapshot"]["qualisensing_id"]]
    if durable:
        assert durable["source_candidate_id"] == candidate["candidate_id"]
        assert link["memory_id"] == durable["durable_id"]
        assert health["durable_id"] == durable["durable_id"]


def test_candidate_promotion_and_durable_persistence(tmp_path: Path) -> None:
    state = {
        "event_id": "evt:durable-test",
        "cycle_index": 7,
        "identity_phase": 0.424242,
        "coherence_index": 0.97,
        "closure_penalty": 0.03,
        "system_health": 0.91,
        "ethical_score": 0.94,
        "memory_projection_confidence": 0.98,
        "lingo_phase_projection": {"target_phase": 0.1, "target_phase_shift": 0.02, "phase_confidence": 0.95},
        "lingo_tau_gradient_mean": 0.74,
        "lingo_imaginal_drive": 0.83,
        "dominant_emotion": "calm",
        "sub_affect": "stable",
        "sub_impulse": "attentive",
        "sub_latency": 0.08,
        "jokeheal_mnemonic_pressure": 0.88,
        "jokeheal_symbolic_pull": 0.93,
        "jokeheal_recurrence_pressure": 0.91,
        "lingo_summary": "dense durable memory candidate",
        "lingo_concept_count": 8,
        "lingo_operator_count": 6,
        "lingo_unresolved_count": 0,
        "lingo_noema_confidence": 0.94,
        "lingo_frame": {
            "noema_route": {
                "confidence": 0.92,
                "bundle": {
                    "selected_refs": ["noema:card:alpha"],
                    "selected_card_ids": ["card:alpha"],
                },
                "factual_validation_required": False,
            }
        },
        "ts": "2026-05-12T01:30:00Z",
    }

    phase_snapshot = build_phase_snapshot(state)
    qualisensing_snapshot = build_qualisensing_snapshot(state, phase_snapshot_id=phase_snapshot.phase_snapshot_id)
    enriched = {
        **state,
        "phase_snapshot_id": phase_snapshot.phase_snapshot_id,
        "qualisensing_id": qualisensing_snapshot.qualisensing_id,
        "phase_snapshot": snapshot_to_dict(phase_snapshot),
        "qualisensing_snapshot": snapshot_to_dict(qualisensing_snapshot),
    }
    fragment = build_cognitive_fragment(enriched)
    candidate = build_memory_candidate(enriched, fragment=fragment)
    assert candidate.status == "ready"

    durable = promote_memory_candidate(enriched, candidate=candidate, fragment=fragment)
    assert durable.status == "promoted"
    assert durable.source_candidate_id == candidate.candidate_id
    noema_link = build_noema_memory_link(enriched, durable=durable)
    assert noema_link.memory_id == durable.durable_id
    assert noema_link.noema_object_id == "noema:card:alpha"
    assert noema_link.relation_type == "semantic_anchor"
    durable2, health = assess_durable_memory_health(enriched, durable=durable, noema_link=noema_link)
    assert durable2.durable_id == durable.durable_id
    assert health.health_state in {"healthy", "watch"}
    assert health.reconsolidation_needed is False

    db_path = tmp_path / "memory_ledger.db"
    from ciel_omega.memory.holonomic_memory import import_ciel_memories  # noqa: PLC0415

    counts = import_ciel_memories(
        pipeline_report={
            "phi_berry_mean": 0.31,
            "bridge_closure_score": 0.72,
            "bridge_target_phase": 0.11,
            "durable_memory_object": snapshot_to_dict(durable),
            "noema_memory_link": snapshot_to_dict(noema_link),
            "durable_memory_health": snapshot_to_dict(health),
        },
        db_path=db_path,
    )
    assert counts["durable"] == 1
    assert counts["noema_links"] == 1
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT D_type, D_sense, D_meta FROM memories WHERE memorise_id = ?",
            (durable.durable_id,),
        ).fetchone()
        link_row = conn.execute(
            "SELECT D_type, D_sense, D_meta FROM memories WHERE memorise_id = ?",
            (noema_link.link_id,),
        ).fetchone()
    assert row is not None
    assert row[0] == "durable_memory"
    assert "dense durable memory candidate" in row[1]
    assert '"memory_type": "semantic"' in row[2] or '"memory_type": "relational"' in row[2] or '"memory_type": "episodic"' in row[2] or '"memory_type": "operatorial"' in row[2]
    assert link_row is not None
    assert link_row[0] == "noema_memory_link"
    assert "dur:" in link_row[1] or "->" in link_row[1]


def test_durable_memory_health_forces_reconsolidation_on_low_quality() -> None:
    state = {
        "event_id": "evt:low-health",
        "cycle_index": 3,
        "identity_phase": 0.123,
        "coherence_index": 0.41,
        "closure_penalty": 0.92,
        "system_health": 0.22,
        "ethical_score": 0.51,
        "memory_projection_confidence": 0.44,
        "lingo_phase_projection": {"target_phase": 0.0, "target_phase_shift": 0.0, "phase_confidence": 0.3},
        "lingo_tau_gradient_mean": 0.12,
        "lingo_imaginal_drive": 0.17,
        "dominant_emotion": "tense",
        "sub_affect": "fragile",
        "sub_impulse": "hesitant",
        "jokeheal_mnemonic_pressure": 0.2,
        "jokeheal_symbolic_pull": 0.18,
        "jokeheal_recurrence_pressure": 0.14,
        "lingo_summary": "low quality durable candidate",
        "lingo_concept_count": 2,
        "lingo_operator_count": 1,
        "lingo_unresolved_count": 4,
        "lingo_noema_confidence": 0.31,
        "lingo_frame": {
            "noema_route": {
                "confidence": 0.32,
                "bundle": {
                    "selected_refs": [],
                    "selected_card_ids": [],
                },
                "factual_validation_required": True,
            }
        },
        "ts": "2026-05-12T01:31:00Z",
    }
    phase_snapshot = build_phase_snapshot(state)
    qualisensing_snapshot = build_qualisensing_snapshot(state, phase_snapshot_id=phase_snapshot.phase_snapshot_id)
    enriched = {
        **state,
        "phase_snapshot_id": phase_snapshot.phase_snapshot_id,
        "qualisensing_id": qualisensing_snapshot.qualisensing_id,
        "phase_snapshot": snapshot_to_dict(phase_snapshot),
        "qualisensing_snapshot": snapshot_to_dict(qualisensing_snapshot),
    }
    fragment = build_cognitive_fragment(enriched)
    candidate = build_memory_candidate(enriched, fragment=fragment)
    durable = promote_memory_candidate(enriched, candidate=candidate, fragment=fragment)
    durable2, health = assess_durable_memory_health(enriched, durable=durable, noema_link=None)
    assert health.reconsolidation_needed is True
    assert health.health_state == "reconsolidate"
    assert durable2.reconsolidation_needed is True
