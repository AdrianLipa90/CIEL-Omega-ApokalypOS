from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAME = ROOT / "data" / "tame" / "tame_operator_system.yaml"


def test_tame_loads_dimensions():
    from src.lingophysics.tame import load_tame
    data = load_tame(TAME)
    assert data["version"] == "1.4"
    assert set(data["dimensions"]) == {"tense", "aspect", "mood", "modality", "evidentiality"}


def test_tame_signature_phase_and_assertion_force():
    from src.lingophysics.tame import load_tame, encode_tame_signature
    data = load_tame(TAME)
    sig = encode_tame_signature("Past", "Perfective", "Indicative", "Reportative", data)
    assert sig.tense == "Past"
    assert sig.assertion_force < 1.0
    assert sig.evidentiality == "Reportative"


def test_event_equivalence_guard_rejects_mood_mismatch():
    from src.lingophysics.tame import load_tame, encode_tame_signature, event_equivalence_guard
    data = load_tame(TAME)
    a = encode_tame_signature("Present", "Imperfective", "Indicative", "Direct", data)
    b = encode_tame_signature("Present", "Imperfective", "Conditional", "Direct", data)
    assert not event_equivalence_guard(True, True, True, a, b)


def test_direct_evidentiality_can_be_verification_candidate():
    from src.lingophysics.tame import load_tame, encode_tame_signature, evidentiality_allows_verification
    data = load_tame(TAME)
    direct = encode_tame_signature("Present", "Imperfective", "Indicative", "Direct", data)
    reported = encode_tame_signature("Present", "Imperfective", "Indicative", "Reportative", data)
    assert evidentiality_allows_verification(direct)
    assert not evidentiality_allows_verification(reported)
