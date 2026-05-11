from pathlib import Path
from src.lingophysics.card_ontology import (
    card_type_specs,
    classify_repository_files,
    infer_card_type_from_path,
    load_card_ontology,
    required_path_status,
    validate_payload_shape,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v17_required_ontology_files_exist():
    statuses = required_path_status(ROOT)
    assert all(status == "PASS" for status in statuses.values()), statuses


def test_ontology_defines_core_card_types():
    ontology = load_card_ontology(ROOT)
    for typ in ["CONCEPT_CARD", "OPERATOR_CARD", "CASE_GAUGE_CARD", "EVENT_FRAME", "TAME_CARD", "SCOPE_CARD", "JSON_FALLBACK"]:
        assert typ in ontology["card_types"]


def test_path_inference_separates_masses_from_forces():
    specs = card_type_specs(ROOT)
    assert infer_card_type_from_path("data/concept_cards/water.yaml", specs) == "CONCEPT_CARD"
    assert infer_card_type_from_path("data/operator_cards/core_operators_5lang.yaml", specs) == "OPERATOR_CARD"
    assert infer_card_type_from_path("data/event_frames/predicate_valency_frames.yaml", specs) == "EVENT_FRAME"
    assert infer_card_type_from_path("data/scope/scope_quantifier_negation.yaml", specs) == "SCOPE_CARD"


def test_concept_card_cannot_be_primary_operator():
    specs = card_type_specs(ROOT)
    result = validate_payload_shape("CONCEPT_CARD", {"concept_id": "water", "formal_modes": []}, specs)
    assert "CONCEPT_CARD_WITH_PRIMARY_OPERATOR_MODES" in result["errors"]


def test_operator_card_without_arity_is_warning_not_silent():
    specs = card_type_specs(ROOT)
    result = validate_payload_shape("OPERATOR_CARD", {"operator_id": "op:test"}, specs)
    assert "OPERATOR_CARD_WITHOUT_ARITY_OR_FORMAL_MODES" in result["warnings"]


def test_repository_classification_counts_ontology_layer():
    counts = classify_repository_files(ROOT)
    assert counts.get("CONCEPT_CARD", 0) > 0
    assert counts.get("OPERATOR_CARD", 0) > 0
    assert counts.get("ROOT_OR_MISC", 0) >= 1
