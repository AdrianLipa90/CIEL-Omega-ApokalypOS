from __future__ import annotations

from src.ciel_sot_agent.noema_file_sense import build_registry, filter_entries


def test_build_registry_contains_semantic_classification() -> None:
    registry = build_registry()

    assert registry["schema"] == "ciel/noema-file-sense-registry/v0.2"
    assert registry["count"] > 0
    assert registry["counts"]["by_location"]
    assert any(entry["location"] == "src" for entry in registry["entries"])
    assert all("file_type" in entry for entry in registry["entries"][:10])
    assert "annotated_entries" in registry["counts"]


def test_build_registry_includes_audit_annotations_for_noncanonical_findings() -> None:
    registry = build_registry()
    entries = {entry["path"]: entry for entry in registry["entries"]}

    xlsx_entry = entries["integration/db/ciel_cards.xlsx"]
    assert "broken_xlsx_surface" in xlsx_entry["audit_flags"]
    assert xlsx_entry["lifecycle_status"] == "annotated_only"

    spreadsheet_entry = entries["src/ciel_sot_agent/spreadsheet_db.py"]
    assert "depends_on_broken_xlsx_surface" in spreadsheet_entry["audit_flags"]
    assert spreadsheet_entry["audit_comment"]


def test_filter_entries_can_find_generated_integration_assets() -> None:
    registry = build_registry()

    matches = filter_entries(
        registry,
        location="integration",
        status="generated",
        limit=20,
    )

    assert matches
    assert all(item["location"] == "integration" for item in matches)
    assert all(item["lifecycle_status"] == "generated" for item in matches)
