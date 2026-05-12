import json
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parents[1]


def test_water_card_has_language_surfaces():
    data = json.loads((ROOT / "data/concept_cards/water.json").read_text(encoding="utf-8"))
    assert "pl" in data["languages"]
    assert "en" in data["languages"]
    assert len(data["languages"]["pl"]["forms"]) >= 4
    assert len(data["languages"]["en"]["contexts"]) >= 2


def test_euler_antonym_phase_constraint_declared():
    data = json.loads((ROOT / "data/concept_cards/water.json").read_text(encoding="utf-8"))
    assert "exp(i*Δφ)+1" in data["cross_language"]["antonym_phase_constraint"]


def test_heatmap_matrix_square():
    rows = (ROOT / "data/heatmaps/grammar_operator_distance.csv").read_text(encoding="utf-8").splitlines()
    header = rows[0].split(",")[1:]
    assert len(rows) - 1 == len(header)
