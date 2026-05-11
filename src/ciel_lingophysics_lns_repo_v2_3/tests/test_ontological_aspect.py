from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONTO = ROOT / "data" / "ontological_aspect" / "koto_mono_ser_estar.yaml"


def test_ontological_aspect_loads_core_operators():
    from src.lingophysics.ontological_aspect import load_ontological_aspect, classify_ontological_surface
    data = load_ontological_aspect(ONTO)
    assert data["version"] == "1.3"
    assert classify_ontological_surface("soy", "es", data) == "SerIdentityBe"
    assert classify_ontological_surface("estoy", "es", data) == "EstarStateBe"


def test_english_be_resolves_by_complement_type():
    from src.lingophysics.ontological_aspect import load_ontological_aspect, resolve_be
    data = load_ontological_aspect(ONTO)
    assert resolve_be("is", "en", "profession", data).canonical_operator == "IdentityBe"
    assert resolve_be("is", "en", "location", data).canonical_operator == "StateBe"


def test_polish_byc_resolves_identity_and_state():
    from src.lingophysics.ontological_aspect import load_ontological_aspect, resolve_be
    data = load_ontological_aspect(ONTO)
    assert resolve_be("jest", "pl", "role", data).canonical_operator == "IdentityBe"
    assert resolve_be("jest", "pl", "condition", data).canonical_operator == "StateBe"


def test_koto_mono_are_contrastive_ontological_aspect():
    from src.lingophysics.ontological_aspect import is_koto_mono_contrast
    assert is_koto_mono_contrast("koto", "mono")
    assert is_koto_mono_contrast("こと", "物")


def test_spanish_ser_estar_are_not_flat_be():
    from src.lingophysics.ontological_aspect import load_ontological_aspect, resolve_be
    data = load_ontological_aspect(ONTO)
    assert resolve_be("ser", "es", "state", data).canonical_operator == "SerIdentityBe"
    assert resolve_be("estar", "es", "identity", data).canonical_operator == "StateBe"
