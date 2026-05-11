from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TENSOR = ROOT / "data" / "transformer_features" / "sample_feature_tensor_water_glass.json"


def test_validator_accepts_preserved_invariants():
    from src.lingophysics.transformer_features import load_feature_tensor
    from src.lingophysics.ciel_validator_loop import validate_output_against_tensor
    tensor = load_feature_tensor(TENSOR)
    result = validate_output_against_tensor(tensor, tensor["validator_expectations"])
    assert result.accepted
    assert result.status == "ACCEPT"


def test_validator_rejects_missing_dual():
    from src.lingophysics.transformer_features import load_feature_tensor
    from src.lingophysics.ciel_validator_loop import validate_output_against_tensor, repair_plan
    tensor = load_feature_tensor(TENSOR)
    observed = ["operator_inside_present", "theme_container_roles_present"]
    result = validate_output_against_tensor(tensor, observed)
    assert not result.accepted
    assert "dual_contains_preserved" in result.missing_expectations
    assert "repair:dual_contains_preserved" in repair_plan(result)
