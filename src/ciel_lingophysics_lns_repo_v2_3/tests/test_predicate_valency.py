from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAMES = ROOT / "data" / "event_frames" / "predicate_valency_frames.yaml"


def test_event_frames_load_and_give_requires_three_roles():
    from src.lingophysics.predicate_valency import load_event_frames, required_roles
    data = load_event_frames(FRAMES)
    assert data["version"] == "1.3"
    assert required_roles("Give", data) == ["Agent", "Theme", "Recipient"]


def test_valency_validation_detects_missing_recipient():
    from src.lingophysics.predicate_valency import load_event_frames, validate_roles
    data = load_event_frames(FRAMES)
    check = validate_roles("Give", ["Agent", "Theme"], data)
    assert not check.valid
    assert "Recipient" in check.missing_roles


def test_polish_case_intersects_with_frame_not_absolute_mapping():
    from src.lingophysics.predicate_valency import load_event_frames, role_for_polish_case
    data = load_event_frames(FRAMES)
    assert role_for_polish_case("Give", "Dat", data) == ["Recipient"]
    assert role_for_polish_case("Fear", "Gen", data) == ["Stimulus"]


def test_transduction_strategy_for_english_give():
    from src.lingophysics.predicate_valency import load_event_frames, transduction_strategy
    data = load_event_frames(FRAMES)
    s = transduction_strategy("Give", "en", data)
    assert "give" in s and "Recipient" in s


def test_contains_inside_dual_equation_is_preserved():
    from src.lingophysics.predicate_valency import load_event_frames, frame_equation
    data = load_event_frames(FRAMES)
    assert "Inside" in frame_equation("ContainsInsideDual", data)
