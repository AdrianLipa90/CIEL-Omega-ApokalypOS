from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DYN = ROOT / "data" / "operator_families" / "deictic_dynamic.yaml"


def test_dynamic_deictic_file_exists_and_has_core_operators():
    from src.lingophysics.dynamic_deixis import load_dynamic_deictics
    data = load_dynamic_deictics(DYN)
    assert data["version"] == "1.2"
    ids = {op["canonical_operator"] for op in data["operators"]}
    assert {"Somewhere", "Sometime", "Somehow", "Never"}.issubset(ids)


def test_polish_dynamic_surfaces_are_classified():
    from src.lingophysics.dynamic_deixis import classify_dynamic_surface
    assert classify_dynamic_surface("gdzieś") == "Somewhere"
    assert classify_dynamic_surface("kiedyś") == "Sometime"
    assert classify_dynamic_surface("jakoś") == "Somehow"
    assert classify_dynamic_surface("skądś") == "FromSomewhere"


def test_unresolved_anchor_preserves_lack_of_precision():
    from src.lingophysics.dynamic_deixis import unresolved_anchor
    a = unresolved_anchor("Somewhere")
    assert a.domain == "Place"
    assert a.resolution_state == "unresolved"
    assert "resolution" in a.equation


def test_context_can_resolve_dynamic_anchor():
    from src.lingophysics.dynamic_deixis import resolve_dynamic_anchor
    a = resolve_dynamic_anchor("Sometime", {"time": "tomorrow"})
    assert a.resolution_state == "resolved"
    assert "tomorrow" in a.equation


def test_false_precision_guard():
    from src.lingophysics.dynamic_deixis import unresolved_anchor, is_false_precision
    a = unresolved_anchor("Somehow")
    assert is_false_precision(a, rendered_as_precise=True)
