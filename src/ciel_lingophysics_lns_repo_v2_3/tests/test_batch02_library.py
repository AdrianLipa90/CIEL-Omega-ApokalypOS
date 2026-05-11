from pathlib import Path
from lingophysics.batch_library import validate_batch_dir, load_card

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "data" / "concept_cards" / "batch02_cognitive_social_36x5"


def test_batch02_has_36_yaml_cards():
    cards = [p for p in BATCH.glob("*.yaml") if not p.name.startswith("batch02_index")]
    assert len(cards) == 36


def test_batch02_language_panels_complete():
    report = validate_batch_dir(BATCH)
    assert report["card_count"] == 36
    assert report["passed"], report["errors"]


def test_batch02_cards_are_concept_cards():
    for path in BATCH.glob("*.yaml"):
        if path.name.startswith("batch02_index"):
            continue
        card = load_card(path)
        assert card["card_type"] == "CONCEPT_CARD"
        assert card["concept_id"].startswith("concept:")
        assert card["operator_hooks"]
