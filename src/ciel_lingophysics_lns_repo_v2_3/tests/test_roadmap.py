from pathlib import Path
import json

from src.lingophysics.roadmap import (
    gguf_is_advisory,
    load_roadmap,
    next_phase,
    planned_phases,
    validate_roadmap,
)

ROOT = Path(__file__).resolve().parents[1]


def test_stage_plan_validates():
    data = load_roadmap(ROOT / "data" / "roadmap" / "cielingo_stage_plan_v2_1.json")
    assert validate_roadmap(data) == []
    assert data["cielingo_roadmap_version"] == "2.1"
    assert len(data["phases"]) >= 7


def test_next_phase_is_current_or_planned():
    data = load_roadmap(ROOT / "data" / "roadmap" / "cielingo_stage_plan_v2_1.json")
    phase = next_phase(data)
    assert phase is not None
    assert phase["id"] == "P1"
    assert phase["status"] in {"current_patch", "planned", "research_planned", "future"}


def test_planned_phases_include_noema_and_gguf_loop():
    data = load_roadmap(ROOT / "data" / "roadmap" / "cielingo_stage_plan_v2_1.json")
    names = {p["name"] for p in planned_phases(data)}
    assert "NOEMA Retrieval and Inference Gate" in names
    assert "GGUF Teacher-Validator Learning Loop" in names


def test_gguf_policy_is_advisory_not_canonical():
    policy = json.loads((ROOT / "data" / "roadmap" / "gguf_teacher_validator_policy_v2_1.json").read_text(encoding="utf-8"))
    assert policy["gguf_role"] == "advisory_teacher_validator"
    assert gguf_is_advisory(policy)


def test_noema_gate_contains_non_claim_about_dense_gguf():
    gate = json.loads((ROOT / "data" / "roadmap" / "noema_inference_gate_policy_v2_1.json").read_text(encoding="utf-8"))
    assert "does not make dense GGUF" in gate["non_claim"]
