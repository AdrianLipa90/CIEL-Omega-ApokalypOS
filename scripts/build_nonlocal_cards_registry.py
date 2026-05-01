#!/usr/bin/env python3
"""Build nonlocal_cards_registry.json + .csv from docs/object_cards/nonlocal/*.md.

Single source of truth: the .md files.
The script parses each NL-*.md and extracts card_id, name, class,
active_status, anchors, role, input_from, output_to, authority_rule,
horizon_relation.  Fields missing from a card get empty-string defaults.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


CARDS_DIR = Path("docs/object_cards/nonlocal")
OUT_JSON  = Path("integration/registries/definitions/nonlocal_cards_registry.json")
OUT_CSV   = Path("integration/registries/definitions/nonlocal_cards_registry.csv")


def _strip(s: str) -> str:
    return s.strip(" `'\"\t")


def _parse_card(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    card: dict = {
        "card_id":         "",
        "name":            "",
        "class":           "",
        "active_status":   "",
        "anchors":         [],
        "role":            "",
        "input_from":      "",
        "output_to":       "",
        "authority_rule":  "",
        "horizon_relation":"",
    }

    # card_id from filename (NL-XXX-NNNN.md) — authoritative
    m = re.match(r"(NL-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+)", path.stem)
    if not m:
        return None
    card["card_id"] = m.group(1)

    current_section = ""
    in_anchors = False
    authority_lines: list[str] = []
    collecting_authority_rule = False

    for line in lines:
        stripped = line.strip()

        # Section headers
        if stripped.startswith("## "):
            current_section = stripped[3:].lower()
            in_anchors = False
            collecting_authority_rule = False
            continue
        if stripped.startswith("### "):
            sub = stripped[4:].lower()
            collecting_authority_rule = (sub == "authority rule" or current_section == "authority rule")
            in_anchors = False
            continue

        # Identity block
        if current_section == "identity":
            if "**card_id:**" in line:
                card["card_id"] = _strip(line.split("**card_id:**")[-1])
            elif "**name:**" in line:
                card["name"] = _strip(line.split("**name:**")[-1])
            elif "**class:**" in line:
                card["class"] = _strip(line.split("**class:**")[-1])
            elif "**active_status:**" in line:
                card["active_status"] = _strip(line.split("**active_status:**")[-1])

        # Anchors block — bullet list
        elif current_section == "anchors":
            if stripped.startswith("- "):
                card["anchors"].append(_strip(stripped[2:]))

        # Role — first non-empty paragraph line
        elif current_section == "role":
            if stripped and not card["role"]:
                card["role"] = stripped

        # Flow block
        elif current_section == "flow":
            if "**input_from:**" in line:
                card["input_from"] = _strip(line.split("**input_from:**")[-1])
            elif "**output_to:**" in line:
                card["output_to"] = _strip(line.split("**output_to:**")[-1])

        # Authority rule — single-line label or paragraph
        elif current_section == "authority rule" or collecting_authority_rule:
            if stripped and not stripped.startswith("#"):
                authority_lines.append(stripped)

        # Horizon relation
        elif current_section == "horizon relation":
            if stripped and not card["horizon_relation"]:
                card["horizon_relation"] = stripped

    if authority_lines and not card["authority_rule"]:
        card["authority_rule"] = " ".join(authority_lines)

    # Title fallback for name
    if not card["name"]:
        for line in lines:
            if line.startswith("# "):
                parts = line[2:].split("—", 1)
                if len(parts) == 2:
                    card["name"] = parts[1].strip()
                break

    return card


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()
    repo_root = Path(args.repo_root).resolve()

    cards_dir = repo_root / CARDS_DIR
    out_json  = repo_root / OUT_JSON
    out_csv   = repo_root / OUT_CSV
    out_json.parent.mkdir(parents=True, exist_ok=True)

    cards = []
    for md in sorted(cards_dir.glob("NL-*.md")):
        parsed = _parse_card(md)
        if parsed and parsed["card_id"]:
            cards.append(parsed)

    cards.sort(key=lambda c: c["card_id"])

    payload = {
        "schema":  "ciel/nonlocal-cards-registry/v0.2",
        "count":   len(cards),
        "records": cards,
    }
    out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    fieldnames = ["card_id","name","class","active_status","anchors",
                  "role","input_from","output_to","authority_rule","horizon_relation"]
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for rec in cards:
            row = rec.copy()
            row["anchors"] = ";".join(rec["anchors"])
            writer.writerow(row)

    print(json.dumps({
        "ok":    True,
        "count": len(cards),
        "cards": [c["card_id"] for c in cards],
        "json":  str(out_json.relative_to(repo_root)).replace("\\", "/"),
        "csv":   str(out_csv.relative_to(repo_root)).replace("\\", "/"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
