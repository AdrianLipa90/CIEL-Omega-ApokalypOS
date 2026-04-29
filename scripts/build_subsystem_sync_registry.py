#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SYNC_SCHEMA = "ciel/subsystem-sync-registry/v0.1"
SYNC_REPORT_SCHEMA = "ciel/subsystem-sync-report/v0.1"


def avg(values: list[float]) -> float:
    return round(sum(values) / len(values), 3) if values else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    defs_dir = repo_root / "integration" / "registries" / "definitions"
    export_payload = json.loads((defs_dir / "orbital_definition_registry.json").read_text(encoding="utf-8"))
    internal_payload = json.loads((defs_dir / "internal_subsystem_cards.json").read_text(encoding="utf-8"))

    export_cards = export_payload["records"]
    internal_cards = internal_payload["internal_cards"]
    export_by_id = {card["id"]: card for card in export_cards}
    internal_by_export = {card["export_card_id"]: card for card in internal_cards}

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for card in export_cards:
        grouped[card["board_card_id"]].append(card)

    subsystem_records: list[dict[str, Any]] = []
    sync_scope_counts: Counter[str] = Counter()
    sync_law_counts: Counter[str] = Counter()
    condensation_operator_counts: Counter[str] = Counter()

    for board_card_id, members in sorted(grouped.items()):
        board_card = export_by_id.get(board_card_id)
        member_ids = sorted(card["id"] for card in members if card["id"] != board_card_id)
        member_internal_ids = sorted(card["internal_card_id"] for card in members)
        orbit_counter = Counter(card["orbital_role"] for card in members)
        manybody_counter = Counter(card["manybody_role"] for card in members)
        avg_conf = avg([float(card.get("export_confidence", 0.0)) for card in members])
        avg_unc = avg([float(card.get("residual_uncertainty", 0.0)) for card in members])
        dominant_orbit = orbit_counter.most_common(1)[0][0] if orbit_counter else "UNRESOLVED"
        dominant_manybody = manybody_counter.most_common(1)[0][0] if manybody_counter else "UNKNOWN"
        board_export_result = board_card.get("export_result") if board_card else f"BOARD<{dominant_orbit}>"
        board_export_state = board_card.get("export_state") if board_card else "SUBSYSTEM_SUMMARY"
        tau_orbit = members[0].get("tau_orbit", f"tau-orbit:{board_card_id}")
        tau_system = members[0].get("tau_system", "tau-system:GLOBAL_ATTRACTOR")
        sync_law_ref = members[0].get("sync_law_ref", "sync-law:METRONOME_BOARD_COUPLING")
        condensation_operator = members[0].get("condensation_operator", "CONDENSE_HALF_CONCLUSIONS")
        board_scope = "BOARD_ROOT"
        child_scopes = sorted({card.get("sync_scope", "BOARD_MEMBER") for card in members})

        subsystem_record = {
            "sync_schema": SYNC_SCHEMA,
            "board_card_id": board_card_id,
            "board_path": board_card.get("path") if board_card else None,
            "board_horizon_id": board_card.get("horizon_id") if board_card else (members[0].get("horizon_id") if members else None),
            "tau_orbit": tau_orbit,
            "tau_system": tau_system,
            "sync_law_ref": sync_law_ref,
            "condensation_operator": condensation_operator,
            "board_sync_scope": board_scope,
            "child_sync_scopes": child_scopes,
            "child_card_ids": sorted(card["id"] for card in members),
            "member_card_ids": member_ids,
            "internal_card_ids": member_internal_ids,
            "member_count": len(member_ids),
            "card_count": len(members),
            "orbit_role_distribution": dict(sorted(orbit_counter.items())),
            "manybody_role_distribution": dict(sorted(manybody_counter.items())),
            "avg_export_confidence": avg_conf,
            "avg_residual_uncertainty": avg_unc,
            "board_export_state": board_export_state,
            "board_export_result": board_export_result,
            "dominant_orbit": dominant_orbit,
            "dominant_manybody_role": dominant_manybody,
            "private_condensate_sources": sorted(
                card["internal_card_id"] for card in members if card["id"] in internal_by_export
            ),
            "aggregation_model": "BOARD_METRONOME_COUPLING",
            "condensed_half_conclusion": {
                "result": board_export_result,
                "confidence": avg_conf,
                "uncertainty": avg_unc,
            },
        }
        subsystem_records.append(subsystem_record)
        sync_scope_counts.update(child_scopes)
        sync_law_counts.update([sync_law_ref])
        condensation_operator_counts.update([condensation_operator])

    avg_members = avg([float(r["member_count"]) for r in subsystem_records]) if subsystem_records else 0.0
    registry_payload = {
        "schema": SYNC_SCHEMA,
        "count": len(subsystem_records),
        "records": subsystem_records,
    }
    report_payload = {
        "schema": SYNC_REPORT_SCHEMA,
        "board_count": len(subsystem_records),
        "avg_members_per_board": avg_members,
        "sync_scope_counts": dict(sorted(sync_scope_counts.items())),
        "sync_law_counts": dict(sorted(sync_law_counts.items())),
        "condensation_operator_counts": dict(sorted(condensation_operator_counts.items())),
        "tau_orbit_count": len({r["tau_orbit"] for r in subsystem_records}),
        "tau_system_count": len({r["tau_system"] for r in subsystem_records}),
    }

    (defs_dir / "subsystem_sync_registry.json").write_text(json.dumps(registry_payload, indent=2), encoding="utf-8")
    (defs_dir / "subsystem_sync_report.json").write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    print(json.dumps(report_payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
