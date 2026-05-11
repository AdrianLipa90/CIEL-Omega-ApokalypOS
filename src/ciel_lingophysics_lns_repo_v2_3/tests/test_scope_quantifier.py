from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "data" / "scope" / "scope_quantifier_negation.yaml"


def test_scope_system_loads():
    from src.lingophysics.scope_quantifier import load_scope_system
    data = load_scope_system(SCOPE)
    assert data["version"] == "1.5"
    assert "ALL" in data["dimensions"]["quantifier"]
    assert "NO" in data["dimensions"]["quantifier"]


def test_not_all_is_not_none():
    from src.lingophysics.scope_quantifier import load_scope_system, normalize_scope, scope_equivalent
    data = load_scope_system(SCOPE)
    not_all = normalize_scope("ALL", "Know", "outside_quantifier", data, domain="Human")
    none = normalize_scope("NO", "Know", "quantifier_negative", data, domain="Human")
    assert "EXISTS" in not_all.normalized
    assert "FORALL" in none.normalized
    assert not scope_equivalent(not_all, none)


def test_all_not_equivalent_to_no_under_same_domain():
    from src.lingophysics.scope_quantifier import load_scope_system, normalize_scope, scope_equivalent
    data = load_scope_system(SCOPE)
    all_not = normalize_scope("ALL", "Know", "inside_predicate", data, domain="Human")
    none = normalize_scope("NO", "Know", "quantifier_negative", data, domain="Human")
    assert scope_equivalent(all_not, none)


def test_unresolved_scope_is_legal_state():
    from src.lingophysics.scope_quantifier import load_scope_system, normalize_scope
    data = load_scope_system(SCOPE)
    expr = normalize_scope("ANY", "Move", "mystery_position", data)
    assert expr.scope_status == "unresolved"
    assert expr.normalized == "UNRESOLVED_SCOPE"


def test_scope_guard_rejects_false_equivalence():
    from src.lingophysics.scope_quantifier import load_scope_system, normalize_scope, event_equivalence_guard
    data = load_scope_system(SCOPE)
    a = normalize_scope("ALL", "Know", "outside_quantifier", data, domain="Human")
    b = normalize_scope("NO", "Know", "quantifier_negative", data, domain="Human")
    assert not event_equivalence_guard(True, True, True, a, b)


def test_scope_guard_accepts_same_normal_form():
    from src.lingophysics.scope_quantifier import load_scope_system, normalize_scope, event_equivalence_guard
    data = load_scope_system(SCOPE)
    a = normalize_scope("SOME", "Know", "inside_predicate", data, domain="Human")
    b = normalize_scope("ALL", "Know", "outside_quantifier", data, domain="Human")
    assert event_equivalence_guard(True, True, True, a, b)
