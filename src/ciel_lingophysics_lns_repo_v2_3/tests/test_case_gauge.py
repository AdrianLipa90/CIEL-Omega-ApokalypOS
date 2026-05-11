from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[1]
GAUGE = ROOT / "data" / "case_systems" / "slavic_case_gauge.yaml"


def test_case_gauge_file_exists_and_has_polish_cases():
    from src.lingophysics.case_gauge import load_case_gauge
    data = load_case_gauge(GAUGE)
    assert data["version"] == "1.1"
    cases = {row["ud"] for row in data["case_roles"]}
    assert {"Nom", "Acc", "Gen", "Dat", "Ins", "Loc", "Voc"}.issubset(cases)


def test_polish_case_maps_to_english_strategy():
    from src.lingophysics.case_gauge import load_case_gauge, map_polish_case_to_language
    data = load_case_gauge(GAUGE)
    acc = map_polish_case_to_language("Acc", "en", data)
    assert acc.operator == "DirectPatient(x)"
    assert "object" in acc.strategy.lower()


def test_genitive_is_not_single_preposition_mapping():
    from src.lingophysics.case_gauge import load_case_gauge, map_polish_case_to_language
    data = load_case_gauge(GAUGE)
    gen = map_polish_case_to_language("Gen", "en", data)
    assert "of" in gen.strategy
    assert "from" in gen.strategy
    assert gen.loss_risk >= 0.35


def test_decode_case_role():
    from src.lingophysics.case_gauge import decode_case_role
    assert decode_case_role("Ins") == "InstrumentMeansComitativeRole(x)"
    assert decode_case_role("Voc") == "Address(x)"


def test_reconstruction_costs_german_bridge_lower_than_english_for_dative():
    from src.lingophysics.case_gauge import reconstruction_cost
    assert reconstruction_cost("Dat", "de") < reconstruction_cost("Dat", "en")


def test_case_mapping_csv_has_seven_rows():
    path = ROOT / "data" / "case_mappings" / "pl_case_to_5lang_surface_strategies.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert len(rows) == 7
    assert any(r["ud"] == "Loc" and "about" in r["en_strategy"] for r in rows)
