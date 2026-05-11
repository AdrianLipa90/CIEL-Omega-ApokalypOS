"""Batch concept-card utilities for CIELingo."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

REQUIRED_LANGUAGES = {"pl", "en", "de", "fr", "es"}


def load_card(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    if path.suffix in {".yaml", ".yml"} and yaml is not None:
        return yaml.safe_load(text)
    raise ValueError(f"Unsupported card file: {path}")


def validate_language_panels(card: dict[str, Any], required: set[str] | None = None) -> list[str]:
    required = required or REQUIRED_LANGUAGES
    errors: list[str] = []
    langs = set((card.get("languages") or {}).keys())
    missing = sorted(required - langs)
    if missing:
        errors.append(f"missing languages: {missing}")
    for lang in required & langs:
        panel = card["languages"][lang]
        if not panel.get("lemma"):
            errors.append(f"{lang}: missing lemma")
        if not panel.get("operator_tags"):
            errors.append(f"{lang}: missing operator_tags")
        if panel.get("review_status") != "needs_human_validation":
            errors.append(f"{lang}: expected needs_human_validation")
    return errors


def validate_batch_dir(batch_dir: str | Path) -> dict[str, Any]:
    batch_dir = Path(batch_dir)
    cards = sorted(batch_dir.glob("*.yaml"))
    cards = [p for p in cards if not p.name.startswith("batch02_index")]
    report = {"card_count": len(cards), "errors": {}}
    for path in cards:
        card = load_card(path)
        errs = validate_language_panels(card)
        if errs:
            report["errors"][path.name] = errs
    report["passed"] = not report["errors"]
    return report
