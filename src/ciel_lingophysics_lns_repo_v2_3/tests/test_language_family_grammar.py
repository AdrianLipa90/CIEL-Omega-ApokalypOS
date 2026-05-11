from pathlib import Path
from src.lingophysics.language_family_grammar import load_language_families, load_language_profiles, grammar_algorithm_stack
from src.lingophysics.dialect_adapter import load_dialect_policy, should_activate_adapter, dialect_requires_review
from src.lingophysics.fine_tuning_policy import load_algorithm_registry, promotion_allowed, gguf_can_canonicalize
ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ROOT / "data" / "language_families" / "language_family_grammar_profiles_v2_3.json"
PROFILES = ROOT / "data" / "language_families" / "language_profile_specialization_v2_3.json"
DIALECTS = ROOT / "data" / "dialects" / "dialect_adapter_policy_v2_3.json"
ALGORITHMS = ROOT / "data" / "grammar_algorithms" / "grammar_algorithm_registry_v2_3.json"
def test_polish_routes_to_slavic_case_stack():
    stack = grammar_algorithm_stack("pl", load_language_families(FAMILIES), load_language_profiles(PROFILES))
    assert stack["family"] == "family:slavic" and "case_gauge" in stack["modules"] and "aspect_pair_resolver" in stack["modules"] and not stack["unresolved"]
def test_english_routes_to_word_order_stack():
    stack = grammar_algorithm_stack("en", load_language_families(FAMILIES), load_language_profiles(PROFILES))
    assert stack["family"] == "family:germanic" and "word_order_role_mapper" in stack["modules"] and "auxiliary_stack_parser" in stack["modules"]
def test_unknown_language_is_explicitly_unresolved():
    stack = grammar_algorithm_stack("xx", load_language_families(FAMILIES), load_language_profiles(PROFILES))
    assert "UNRESOLVED_LANGUAGE_FAMILY" in stack["unresolved"] and "UNRESOLVED_LANGUAGE_PROFILE" in stack["unresolved"]
def test_dialect_activation_requires_explicit_or_high_confidence():
    policy = load_dialect_policy(DIALECTS)
    assert should_activate_adapter(policy, explicit_variant=True) and should_activate_adapter(policy, detector_confidence=0.91) and not should_activate_adapter(policy, detector_confidence=0.5)
def test_high_level_dialect_requires_review_or_unresolved():
    assert dialect_requires_review(load_dialect_policy(DIALECTS), "dialect:missing")
def test_gguf_never_canonicalizes_by_itself_and_promotion_thresholds_hold():
    registry = load_algorithm_registry(ALGORITHMS)
    assert gguf_can_canonicalize() is False and promotion_allowed(0.96, "reviewed_to_canonical", registry) and not promotion_allowed(0.70, "draft_to_reviewed", registry)
