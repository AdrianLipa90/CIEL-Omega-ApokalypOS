from pathlib import Path
from src.lingophysics.repo_coherence import (
    classify_path,
    count_by_type,
    load_coherence_summary,
    required_path_status,
    yaml_json_pair_audit,
)

ROOT = Path(__file__).resolve().parents[1]


def test_required_v16_files_exist():
    statuses = required_path_status(ROOT)
    assert all(status == "PASS" for status in statuses.values()), statuses


def test_card_type_classification_keeps_concepts_and_operators_separate():
    assert classify_path("data/concept_cards/water.yaml") == "CONCEPT_CARD"
    assert classify_path("data/operator_cards/core_operators_5lang.yaml") == "OPERATOR_CARD"
    assert classify_path("data/scope/scope_quantifier_negation.yaml") == "SCOPE_CARD"


def test_coherence_summary_has_no_integrity_blockers():
    summary = load_coherence_summary(ROOT)
    assert summary["integrity_blockers"] == 0
    assert summary["schema_count"] >= 1


def test_repository_contains_all_core_layers():
    counts = count_by_type(ROOT)
    for required_type in ["CONCEPT_CARD", "OPERATOR_CARD", "GRAMMAR_CARD", "CASE_GAUGE_CARD", "TAME_CARD", "SCOPE_CARD", "SOURCE", "TEST"]:
        assert counts.get(required_type, 0) > 0, required_type


def test_yaml_json_audit_is_explicit_even_when_not_perfect():
    audit = yaml_json_pair_audit(ROOT)
    assert audit["yaml_count"] > 0
    assert audit["json_count"] > 0
    assert "missing_json_count" in audit
