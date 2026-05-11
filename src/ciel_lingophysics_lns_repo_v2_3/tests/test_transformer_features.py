from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "transformer_features" / "feature_spec.yaml"
TENSOR = ROOT / "data" / "transformer_features" / "sample_feature_tensor_water_glass.json"


def test_feature_spec_loads():
    from src.lingophysics.transformer_features import load_feature_spec
    spec = load_feature_spec(SPEC)
    assert spec["version"] == "1.9"
    assert "card_type" in spec["feature_groups"]
    assert "OPERATOR_CARD" in spec["feature_groups"]["card_type"]["labels"]


def test_sample_tensor_encodes_concept_and_operator():
    from src.lingophysics.transformer_features import load_feature_spec, load_feature_tensor, encode_tensor
    spec = load_feature_spec(SPEC)
    tensor = load_feature_tensor(TENSOR)
    encoded = encode_tensor(tensor, spec)
    assert len(encoded) == 4
    assert encoded[0]["card_type"] == "CONCEPT_CARD"
    assert encoded[2]["operator_id"] == "op:inside"
    assert encoded[0]["concept_mass"] > 0


def test_invariant_expectations_are_extracted():
    from src.lingophysics.transformer_features import load_feature_tensor, invariant_expectation_set
    tensor = load_feature_tensor(TENSOR)
    expectations = invariant_expectation_set(tensor)
    assert "operator_inside_present" in expectations
    assert "dual_contains_preserved" in expectations
