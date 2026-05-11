import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_operator_library_has_core_dual_pair():
    data = json.loads((ROOT / "data/operator_cards/core_operators_5lang.json").read_text(encoding="utf-8"))
    ops = {op["id"]: op for op in data["operator_cards"]}
    assert ops["op:core:inside"]["dual"] == "op:core:contain"
    assert ops["op:core:contain"]["dual"] == "op:core:inside"


def test_operator_library_has_five_language_surfaces():
    data = json.loads((ROOT / "data/operator_cards/core_operators_5lang.json").read_text(encoding="utf-8"))
    for op in data["operator_cards"]:
        assert set(op["surfaces"].keys()) == {"pl", "en", "de", "fr", "es"}
        assert all(op["surfaces"][lang]["forms"] for lang in op["surfaces"])


def test_how_operator_is_polyfunctional():
    data = json.loads((ROOT / "data/operator_cards/core_operators_5lang.json").read_text(encoding="utf-8"))
    how = next(op for op in data["operator_cards"] if op["id"] == "op:core:how")
    eq = " ".join(how["equations"])
    assert "How(T)" in eq
    assert "Like(x,y)" in eq
    assert "As(x,y)" in eq


def test_operator_card_type_classifier():
    from src.lingophysics.operator_card import classify_word_card
    assert classify_word_card("NOUN") == "CONCEPT_CARD"
    assert classify_word_card("ADP") == "OPERATOR_CARD"
    assert classify_word_card("PART") == "OPERATOR_CARD"
