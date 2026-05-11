from math import pi
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_operator_algebra_index_exists():
    from src.lingophysics.operator_algebra import load_json
    data = load_json(ROOT / "data/operator_algebra/operator_algebra_index.json")
    assert data["version"] == "0.9"
    assert "containment" in data["families"]
    assert "OPERATOR_CARD" in data["required_card_types"]


def test_containment_family_encodes_duality():
    from src.lingophysics.operator_algebra import load_yaml
    fam = load_yaml(ROOT / "data/operator_families/containment.yaml")
    assert fam["duals"][0]["left"] == "Inside(x,y)"
    assert fam["duals"][0]["right"] == "Contains(y,x)"


def test_dual_composer_inside_contains():
    from src.lingophysics.operator_algebra import compose_dual
    assert compose_dual("Inside(x,y)") == "Contains(y,x)"
    assert compose_dual("Contains(x,y)") == "Inside(y,x)"


def test_euler_phase_errors():
    from src.lingophysics.operator_algebra import euler_phase_error
    assert euler_phase_error(0.0, "synonym") < 1e-9
    assert euler_phase_error(pi, "antonym") < 1e-9


def test_have_disambiguation_modes():
    from src.lingophysics.operator_disambiguation import disambiguate_have
    assert disambiguate_have("body_part")["equation"] == "HasPart(x,y)"
    assert disambiguate_have("temperature")["equation"] == "HasProperty(x,y)"
    assert disambiguate_have("problem")["equation"] == "HasState(x,y)"


def test_how_like_as_disambiguation_modes():
    from src.lingophysics.operator_disambiguation import disambiguate_how_like_as
    assert "Ask" in disambiguate_how_like_as("question_manner")["equation"]
    assert "Sim" in disambiguate_how_like_as("comparison")["equation"]
    assert "AssignRole" in disambiguate_how_like_as("role_assignment")["equation"]


def test_containment_composition_equivalence():
    from src.lingophysics.operator_composition import containment_equivalence
    res = containment_equivalence("Inside(Water,Glass)", "Contains(Glass,Water)")
    assert res.valid
    assert res.invariant == "Containment(x,y)"
