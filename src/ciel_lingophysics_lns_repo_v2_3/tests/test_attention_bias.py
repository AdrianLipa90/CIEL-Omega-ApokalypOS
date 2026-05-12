from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "data" / "transformer_features" / "attention_bias_rules.yaml"
TENSOR = ROOT / "data" / "transformer_features" / "sample_feature_tensor_water_glass.json"


def test_attention_bias_rules_load():
    from src.lingophysics.attention_bias import load_bias_rules
    rules = load_bias_rules(RULES)
    assert rules["version"] == "1.9"
    assert rules["weights"]["operator_argument_link"] > 0


def test_attention_bias_matrix_has_operator_concept_links():
    from src.lingophysics.attention_bias import load_bias_rules, build_attention_bias_matrix, has_positive_structural_bias
    from src.lingophysics.transformer_features import load_feature_tensor, tokens_from_tensor
    rules = load_bias_rules(RULES)
    tokens = tokens_from_tensor(load_feature_tensor(TENSOR))
    matrix = build_attention_bias_matrix(tokens, rules)
    assert len(matrix) == len(tokens)
    assert has_positive_structural_bias(matrix)
    # token 2 is Inside operator, token 0 is Water concept
    assert matrix[2][0] > 0
