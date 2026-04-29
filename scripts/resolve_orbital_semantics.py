#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ORBIT_RULES = [
    ("IDENTITY", ["identity", "profile", "soul", "self", "state_geometry", "omega"]),
    ("CONSTITUTIVE", ["memory", "registry", "archive", "log", "manifest", "schema", "contract"]),
    ("DYNAMIC", ["runtime", "step", "evolve", "field", "phase", "coherence", "update", "loop"]),
    ("INTERACTION", ["client", "bridge", "adapter", "chat", "audio", "voice", "packet", "panel"]),
    ("OBSERVATION", ["ui", "view", "cockpit", "probe", "report", "diagnostic", "telemetry", "observe"]),
    ("BOUNDARY", ["policy", "guard", "boundary", "ethic", "validate", "check", "rule"]),
    ("EDUCATION", ["learn", "education", "tutorial", "curriculum", "teacher", "training"]),
]

EXPORT_CARD_SCHEMA = "ciel/orbital-export-card/v0.5"
INTERNAL_CARD_SCHEMA = "ciel/internal-subsystem-card/v0.3"
HORIZON_POLICY_SCHEMA = "ciel/horizon-policy-matrix/v0.1"
SYNC_SCHEMA = "ciel/subsystem-sync-registry/v0.1"
GLOBAL_ATTRACTOR_REF = "GLOBAL_ATTRACTOR:PRIMARY_INFORMATION_SOURCE"
TAU_SYSTEM_ID = "tau-system:GLOBAL_ATTRACTOR"
SYNC_LAW_REF = "sync-law:METRONOME_BOARD_COUPLING"
CONDENSATION_OPERATOR = "CONDENSE_HALF_CONCLUSIONS"

PARENT_ORBIT_ROLE = {
    "IDENTITY": "GLOBAL_ATTRACTOR",
    "CONSTITUTIVE": "IDENTITY",
    "DYNAMIC": "IDENTITY",
    "INTERACTION": "BOUNDARY",
    "OBSERVATION": "BOUNDARY",
    "BOUNDARY": "IDENTITY",
    "EDUCATION": "OBSERVATION",
    "UNRESOLVED": "IDENTITY",
}

INFORMATION_REGIME = {
    "IDENTITY": "LOCAL_PLUS_HORIZON",
    "CONSTITUTIVE": "LOCAL_PLUS_HORIZON",
    "DYNAMIC": "LOCAL_PLUS_HORIZON",
    "INTERACTION": "BOUNDARY_BROKER",
    "OBSERVATION": "GLOBAL_OBSERVATION",
    "BOUNDARY": "BOUNDARY_BROKER",
    "EDUCATION": "GLOBAL_OBSERVATION",
    "UNRESOLVED": "LOCAL_ONLY",
}

HORIZON_CLASS = {
    "LOCAL_ONLY": "SEALED",
    "LOCAL_PLUS_HORIZON": "POROUS",
    "BOUNDARY_BROKER": "TRANSMISSIVE",
    "GLOBAL_OBSERVATION": "OBSERVATIONAL",
}

TAU_ROLE = {
    "IDENTITY": "TAU_MEMORY",
    "CONSTITUTIVE": "TAU_MEMORY",
    "DYNAMIC": "TAU_LOCAL",
    "INTERACTION": "TAU_LOCAL",
    "OBSERVATION": "TAU_OBSERVER",
    "BOUNDARY": "TAU_BOUNDARY",
    "EDUCATION": "TAU_OBSERVER",
    "UNRESOLVED": "TAU_LOCAL",
}

MEMORY_MODE = {
    "IDENTITY": "PERSISTENT_IDENTITY",
    "CONSTITUTIVE": "PERSISTENT_MEMORY",
    "DYNAMIC": "TRANSIENT_RUNTIME",
    "INTERACTION": "TRANSIENT_INTERFACE",
    "OBSERVATION": "SNAPSHOT_OBSERVER",
    "BOUNDARY": "POLICY_CACHE",
    "EDUCATION": "CURRICULUM_SNAPSHOT",
    "UNRESOLVED": "TRANSIENT_RUNTIME",
}

HORIZON_POLICY_MATRIX = {
    "SEALED": {
        "privacy_constraint": "STRICT_NONDISCLOSURE",
        "leak_channel_mode": "NO_DIRECT_LEAK",
        "leak_budget_class": "ZERO_LEAK_BUDGET",
        "allowed_visibility_transitions": ["self->local-orbit", "local-orbit->sealed-export"],
        "exportable_fields": ["export_state", "export_result", "export_confidence", "residual_uncertainty", "horizon_class", "privacy_constraint", "leak_policy", "projection_operator"],
        "sealed_fields": ["internal_candidate_states", "internal_conflict_state", "internal_superposition_state", "internal_resolution_trace", "internal_tau_local", "internal_memory_mode"],
    },
    "POROUS": {
        "privacy_constraint": "GRADIENT_LIMITED_DISCLOSURE",
        "leak_channel_mode": "HAWKING_EULER_DIFFUSIVE",
        "leak_budget_class": "MICRO_LEAK_BUDGET",
        "allowed_visibility_transitions": ["self->container", "container->local-orbit", "local-orbit->horizon-leak"],
        "exportable_fields": ["export_state", "export_result", "export_confidence", "residual_uncertainty", "horizon_class", "privacy_constraint", "leak_policy", "projection_operator", "visible_scopes"],
        "sealed_fields": ["internal_candidate_states", "internal_conflict_state", "internal_superposition_state", "internal_resolution_trace"],
    },
    "TRANSMISSIVE": {
        "privacy_constraint": "BROKER_GATED_DISCLOSURE",
        "leak_channel_mode": "HAWKING_EULER_BROKERED",
        "leak_budget_class": "BROKERED_LEAK_BUDGET",
        "allowed_visibility_transitions": ["self->container", "container->local-orbit", "local-orbit->adjacent-horizon", "adjacent-horizon->broker-leak"],
        "exportable_fields": ["export_state", "export_result", "export_confidence", "residual_uncertainty", "horizon_class", "privacy_constraint", "leak_policy", "projection_operator", "visible_scopes", "manybody_role"],
        "sealed_fields": ["internal_candidate_states", "internal_conflict_state", "internal_superposition_state", "internal_resolution_trace"],
    },
    "OBSERVATIONAL": {
        "privacy_constraint": "SNAPSHOT_SANITIZED_DISCLOSURE",
        "leak_channel_mode": "SNAPSHOT_PROJECTION",
        "leak_budget_class": "SNAPSHOT_LEAK_BUDGET",
        "allowed_visibility_transitions": ["self->container", "container->local-orbit", "local-orbit->orbit-snapshot", "orbit-snapshot->global-snapshot"],
        "exportable_fields": ["export_state", "export_result", "export_confidence", "residual_uncertainty", "horizon_class", "privacy_constraint", "leak_policy", "projection_operator", "visible_scopes", "manybody_role", "tau_role"],
        "sealed_fields": ["internal_candidate_states", "internal_conflict_state", "internal_superposition_state", "internal_resolution_trace", "internal_tau_local"],
    },
}


def score_orbit(text: str) -> tuple[str, float]:
    lowered = text.lower()
    best_orbit = "UNRESOLVED"
    best_score = 0.0
    for orbit, tokens in ORBIT_RULES:
        score = sum(1 for t in tokens if t in lowered)
        if score > best_score:
            best_orbit = orbit
            best_score = float(score)
    confidence = min(0.35 + 0.12 * best_score, 0.97) if best_score > 0 else 0.18
    return best_orbit, confidence


def semantic_role(rec: dict[str, Any], orbit: str) -> str:
    base = f"{orbit.lower()}-{rec['kind']}"
    lowered = f"{rec.get('path','')} {rec.get('qualname','')}".lower()
    if "runtime20" in lowered:
        return "omega-runtime-core"
    if "orbital_cockpit" in lowered:
        return "orbital-observation-shell"
    if "sapiens_client" in lowered:
        return "packet-memory-bridge"
    if "gguf" in lowered:
        return "gguf-language-bridge"
    if "audio" in lowered:
        return f"audio-{rec['kind']}"
    return base


def container_card_id(rec: dict[str, Any]) -> str | None:
    if rec.get("kind") == "file":
        return None
    return f"file:{rec['path']}"


def derive_board_card_id(rec: dict[str, Any]) -> str:
    return rec["id"] if rec.get("kind") == "file" else f"file:{rec['path']}"


def derive_tau_local(card_id: str) -> str:
    return f"tau-local:{card_id}"


def derive_tau_orbit(board_card_id: str) -> str:
    return f"tau-orbit:{board_card_id}"


def derive_sync_scope(rec: dict[str, Any]) -> str:
    return "BOARD_ROOT" if rec.get("kind") == "file" else "BOARD_MEMBER"


def derive_lagrange_roles(rec: dict[str, Any]) -> list[str]:
    lowered = f"{rec.get('path','')} {rec.get('qualname','')} {rec.get('semantic_role','')}".lower()
    roles: list[str] = []
    if any(token in lowered for token in ["bridge", "adapter", "client", "packet", "panel", "gateway", "router"]):
        roles.append("TRANSFER_NODE")
    if any(token in lowered for token in ["report", "probe", "view", "telemetry", "observe", "cockpit"]):
        roles.append("OBSERVATION_POINT")
    if any(token in lowered for token in ["registry", "manifest", "schema", "index", "anchor"]):
        roles.append("ANCHOR_POINT")
    if any(token in lowered for token in ["guard", "policy", "validate", "check", "rule", "boundary"]):
        roles.append("BOUNDARY_GATE")
    return sorted(set(roles))


def derive_manybody_role(rec: dict[str, Any], orbit: str, lagrange_roles: list[str]) -> str:
    if rec.get("kind") == "file":
        return "SUBSYSTEM_BOARD"
    if "TRANSFER_NODE" in lagrange_roles:
        return "TRANSFER_NODE"
    if orbit == "OBSERVATION":
        return "OBSERVER"
    if orbit == "BOUNDARY":
        return "BOUNDARY_GATE"
    return "OSCILLATOR"


def derive_subsystem_kind(rec: dict[str, Any]) -> str:
    return "BOARD" if rec.get("kind") == "file" else "NODE"


def derive_horizon_id(rec: dict[str, Any]) -> str:
    return f"horizon:{rec['path']}"


def derive_visible_scopes(regime: str, rec: dict[str, Any]) -> list[str]:
    base = ["self"]
    if rec.get("kind") != "file":
        base.append("container")
    if regime == "LOCAL_ONLY":
        base.append("local-orbit")
    elif regime == "LOCAL_PLUS_HORIZON":
        base.extend(["local-orbit", "horizon-leak"])
    elif regime == "BOUNDARY_BROKER":
        base.extend(["local-orbit", "adjacent-horizon", "broker-leak"])
    elif regime == "GLOBAL_OBSERVATION":
        base.extend(["local-orbit", "orbit-snapshot", "global-snapshot"])
    return base


def derive_leak_policy(regime: str) -> str:
    return {"LOCAL_ONLY": "SEALED", "LOCAL_PLUS_HORIZON": "HAWKING_EULER", "BOUNDARY_BROKER": "HAWKING_EULER_BROKERED", "GLOBAL_OBSERVATION": "SNAPSHOT_ONLY"}.get(regime, "SEALED")


def derive_projection_operator(horizon_class: str, leak_policy: str) -> str:
    return f"Π_H[{horizon_class}|{leak_policy}]"


def derive_export_state(manybody_role: str, horizon_class: str) -> str:
    if manybody_role == "SUBSYSTEM_BOARD":
        return "SUBSYSTEM_SUMMARY"
    if manybody_role == "TRANSFER_NODE":
        return "BROKERED_INTERFACE"
    if manybody_role == "BOUNDARY_GATE":
        return "POLICY_GATED_EXPORT"
    if manybody_role == "OBSERVER":
        return "OBSERVATION_SNAPSHOT"
    return "LOCAL_HALF_CONCLUSION" if horizon_class != "SEALED" else "SEALED_EXPORT"


def derive_export_result(rec: dict[str, Any], manybody_role: str, orbit: str) -> str:
    if manybody_role == "SUBSYSTEM_BOARD":
        return f"BOARD<{orbit}>"
    if manybody_role == "TRANSFER_NODE":
        return "BROKERED_TRANSFER_RESULT"
    if manybody_role == "BOUNDARY_GATE":
        return "BOUNDARY_FILTER_RESULT"
    if manybody_role == "OBSERVER":
        return "OBSERVATION_RESULT"
    if orbit == "IDENTITY":
        return "IDENTITY_SUMMARY"
    if orbit == "CONSTITUTIVE":
        return "MEMORY_SUMMARY"
    return "LOCAL_RESULT"


def derive_export_confidence(orbital_confidence: float, leak_policy: str) -> float:
    penalty = {"SEALED": 0.08, "HAWKING_EULER": 0.12, "HAWKING_EULER_BROKERED": 0.10, "SNAPSHOT_ONLY": 0.15}.get(leak_policy, 0.12)
    return round(max(0.05, min(0.99, orbital_confidence - penalty)), 3)


def derive_internal_card_id(export_card_id: str) -> str:
    return f"internal:{export_card_id}"


def derive_internal_candidate_states(rec: dict[str, Any], manybody_role: str, orbit: str) -> list[str]:
    base = [f"{orbit}_LOCAL_CANDIDATE", f"{manybody_role}_CANDIDATE"]
    if manybody_role == "TRANSFER_NODE":
        base.append("BROKER_NEGOTIATION_PENDING")
    elif manybody_role == "BOUNDARY_GATE":
        base.append("POLICY_REVIEW_PENDING")
    elif manybody_role == "OBSERVER":
        base.append("SNAPSHOT_SELECTION_PENDING")
    else:
        base.append("LOCAL_REDUCTION_PENDING")
    return base


def derive_internal_conflict_state(horizon_class: str, manybody_role: str) -> str:
    if manybody_role in {"TRANSFER_NODE", "BOUNDARY_GATE"}:
        return "HIGH"
    if horizon_class in {"TRANSMISSIVE", "POROUS"}:
        return "MEDIUM"
    return "LOW"


def derive_internal_superposition_state(rec: dict[str, Any]) -> str:
    return "BOARD_AGGREGATION_ACTIVE" if rec.get("kind") == "file" else "LOCAL_SUPERPOSITION_ACTIVE"


def derive_internal_resolution_trace(manybody_role: str, leak_policy: str) -> list[str]:
    trace = ["LOCAL_ACCUMULATION", "LOCAL_SELECTION"]
    if manybody_role == "SUBSYSTEM_BOARD":
        trace.append("SUBSYSTEM_AGGREGATION")
    trace.append(f"HORIZON_PROJECTION<{leak_policy}>")
    return trace


def count_values(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rec in records:
        value = rec.get(key)
        if value is None:
            continue
        counts[str(value)] = counts.get(str(value), 0) + 1
    return counts


def count_list_values(records: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rec in records:
        for value in rec.get(key, []) or []:
            counts[str(value)] = counts.get(str(value), 0) + 1
    return counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    in_path = repo_root / "integration" / "registries" / "definitions" / "definition_registry.json"
    raw = json.loads(in_path.read_text(encoding="utf-8"))
    records = raw["records"]

    export_cards: list[dict[str, Any]] = []
    internal_cards: list[dict[str, Any]] = []
    orbit_counts: dict[str, int] = {}
    board_ids: set[str] = set()
    for rec in records:
        text = " ".join([rec.get("path", ""), rec.get("name", ""), rec.get("qualname", ""), rec.get("doc", ""), rec.get("signature", "")])
        orbit, confidence = score_orbit(text)
        regime = INFORMATION_REGIME.get(orbit, "LOCAL_ONLY")
        semantic = semantic_role(rec, orbit)
        lagrange = derive_lagrange_roles(rec | {"semantic_role": semantic})
        manybody = derive_manybody_role(rec, orbit, lagrange)
        subsystem_kind = derive_subsystem_kind(rec)
        board_card_id = derive_board_card_id(rec)
        board_ids.add(board_card_id)
        horizon_id = derive_horizon_id(rec)
        horizon_class = HORIZON_CLASS.get(regime, "SEALED")
        leak_policy = derive_leak_policy(regime)
        visible_scopes = derive_visible_scopes(regime, rec)
        tau_role = TAU_ROLE.get(orbit, "TAU_LOCAL")
        tau_local = derive_tau_local(rec["id"])
        tau_orbit = derive_tau_orbit(board_card_id)
        export_confidence = derive_export_confidence(round(confidence, 3), leak_policy)
        internal_id = derive_internal_card_id(rec["id"])
        projection_operator = derive_projection_operator(horizon_class, leak_policy)
        policy = HORIZON_POLICY_MATRIX[horizon_class]
        sync_scope = derive_sync_scope(rec)

        export_card = rec | {
            "card_schema": EXPORT_CARD_SCHEMA,
            "sync_schema": SYNC_SCHEMA,
            "global_attractor_ref": GLOBAL_ATTRACTOR_REF,
            "orbital_role": orbit,
            "orbital_confidence": round(confidence, 3),
            "semantic_role": semantic,
            "board_card_id": board_card_id,
            "container_card_id": container_card_id(rec),
            "subsystem_kind": subsystem_kind,
            "manybody_role": manybody,
            "parent_orbital_role": PARENT_ORBIT_ROLE.get(orbit, "IDENTITY"),
            "horizon_id": horizon_id,
            "horizon_class": horizon_class,
            "information_regime": regime,
            "visible_scopes": visible_scopes,
            "leak_policy": leak_policy,
            "tau_role": tau_role,
            "tau_local": tau_local,
            "tau_orbit": tau_orbit,
            "tau_system": TAU_SYSTEM_ID,
            "sync_scope": sync_scope,
            "sync_law_ref": SYNC_LAW_REF,
            "condensation_operator": CONDENSATION_OPERATOR,
            "lagrange_roles": lagrange,
            "internal_card_id": internal_id,
            "projection_operator": projection_operator,
            "privacy_constraint": policy["privacy_constraint"],
            "leak_channel_mode": policy["leak_channel_mode"],
            "leak_budget_class": policy["leak_budget_class"],
            "allowed_visibility_transitions": policy["allowed_visibility_transitions"],
            "export_state": derive_export_state(manybody, horizon_class),
            "export_result": derive_export_result(rec, manybody, orbit),
            "export_confidence": export_confidence,
            "residual_uncertainty": round(max(0.0, 1.0 - export_confidence), 3),
            "policy_table_ref": f"horizon-policy:{horizon_class}",
        }
        export_cards.append(export_card)

        internal_card = {
            "internal_card_schema": INTERNAL_CARD_SCHEMA,
            "sync_schema": SYNC_SCHEMA,
            "internal_card_id": internal_id,
            "owner_card_id": rec["id"],
            "owner_horizon_id": horizon_id,
            "board_card_id": board_card_id,
            "container_card_id": export_card["container_card_id"],
            "subsystem_kind": subsystem_kind,
            "manybody_role": manybody,
            "internal_visibility": "PRIVATE_SUBSYSTEM_ONLY",
            "internal_candidate_states": derive_internal_candidate_states(rec, manybody, orbit),
            "internal_conflict_state": derive_internal_conflict_state(horizon_class, manybody),
            "internal_superposition_state": derive_internal_superposition_state(rec),
            "internal_resolution_trace": derive_internal_resolution_trace(manybody, leak_policy),
            "internal_tau_local": tau_local,
            "internal_tau_orbit": tau_orbit,
            "internal_tau_system": TAU_SYSTEM_ID,
            "sync_scope": sync_scope,
            "sync_law_ref": SYNC_LAW_REF,
            "condensation_operator": CONDENSATION_OPERATOR,
            "internal_memory_mode": MEMORY_MODE.get(orbit, "TRANSIENT_RUNTIME"),
            "projection_operator": projection_operator,
            "export_card_id": rec["id"],
            "privacy_constraint": policy["privacy_constraint"],
            "horizon_transition_profile": horizon_class,
            "exportable_fields": policy["exportable_fields"],
            "sealed_fields": policy["sealed_fields"],
            "policy_table_ref": f"horizon-policy:{horizon_class}",
        }
        internal_cards.append(internal_card)
        orbit_counts[orbit] = orbit_counts.get(orbit, 0) + 1

    out_dir = repo_root / "integration" / "registries" / "definitions"
    reg_path = out_dir / "orbital_definition_registry.json"
    internal_path = out_dir / "internal_subsystem_cards.json"
    report_path = out_dir / "orbital_assignment_report.json"
    policy_path = out_dir / "horizon_policy_matrix.json"
    reg_payload = {
        "schema": "ciel/orbital-definition-registry-enriched/v0.5",
        "card_schema": EXPORT_CARD_SCHEMA,
        "internal_card_schema": INTERNAL_CARD_SCHEMA,
        "horizon_policy_schema": HORIZON_POLICY_SCHEMA,
        "sync_schema": SYNC_SCHEMA,
        "global_attractor_ref": GLOBAL_ATTRACTOR_REF,
        "count": len(export_cards),
        "unique_boards": len(board_ids),
        "records": export_cards,
    }
    internal_payload = {
        "schema": "ciel/internal-subsystem-card-registry/v0.3",
        "internal_card_schema": INTERNAL_CARD_SCHEMA,
        "horizon_policy_schema": HORIZON_POLICY_SCHEMA,
        "sync_schema": SYNC_SCHEMA,
        "count": len(internal_cards),
        "internal_cards": internal_cards,
    }
    report_payload = {
        "schema": "ciel/orbital-assignment-report/v0.5",
        "card_schema": EXPORT_CARD_SCHEMA,
        "internal_card_schema": INTERNAL_CARD_SCHEMA,
        "horizon_policy_schema": HORIZON_POLICY_SCHEMA,
        "sync_schema": SYNC_SCHEMA,
        "count": len(export_cards),
        "export_card_count": len(export_cards),
        "internal_card_count": len(internal_cards),
        "board_count": len(board_ids),
        "orbit_counts": orbit_counts,
        "unresolved": orbit_counts.get("UNRESOLVED", 0),
        "information_regime_counts": count_values(export_cards, "information_regime"),
        "horizon_class_counts": count_values(export_cards, "horizon_class"),
        "tau_role_counts": count_values(export_cards, "tau_role"),
        "sync_scope_counts": count_values(export_cards, "sync_scope"),
        "manybody_role_counts": count_values(export_cards, "manybody_role"),
        "lagrange_role_counts": count_list_values(export_cards, "lagrange_roles"),
        "projection_operator_counts": count_values(export_cards, "projection_operator"),
        "privacy_constraint_counts": count_values(export_cards, "privacy_constraint"),
        "leak_channel_mode_counts": count_values(export_cards, "leak_channel_mode"),
        "leak_budget_class_counts": count_values(export_cards, "leak_budget_class"),
        "export_state_counts": count_values(export_cards, "export_state"),
        "transition_profile_counts": count_values(internal_cards, "horizon_transition_profile"),
        "internal_memory_mode_counts": count_values(internal_cards, "internal_memory_mode"),
        "internal_conflict_state_counts": count_values(internal_cards, "internal_conflict_state"),
        "internal_visibility_counts": count_values(internal_cards, "internal_visibility"),
    }
    policy_payload = {"schema": HORIZON_POLICY_SCHEMA, "classes": HORIZON_POLICY_MATRIX}
    reg_path.write_text(json.dumps(reg_payload, indent=2), encoding="utf-8")
    internal_path.write_text(json.dumps(internal_payload, indent=2), encoding="utf-8")
    report_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    policy_path.write_text(json.dumps(policy_payload, indent=2), encoding="utf-8")
    print(json.dumps(report_payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
