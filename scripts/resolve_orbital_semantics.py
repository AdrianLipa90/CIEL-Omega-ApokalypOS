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

EXPORT_CARD_SCHEMA = "ciel/orbital-export-card/v0.3"
INTERNAL_CARD_SCHEMA = "ciel/internal-subsystem-card/v0.1"
GLOBAL_ATTRACTOR_REF = "GLOBAL_ATTRACTOR:PRIMARY_INFORMATION_SOURCE"

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
    return {
        "LOCAL_ONLY": "SEALED",
        "LOCAL_PLUS_HORIZON": "HAWKING_EULER",
        "BOUNDARY_BROKER": "HAWKING_EULER_BROKERED",
        "GLOBAL_OBSERVATION": "SNAPSHOT_ONLY",
    }.get(regime, "SEALED")


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
    penalty = {
        "SEALED": 0.08,
        "HAWKING_EULER": 0.12,
        "HAWKING_EULER_BROKERED": 0.1,
        "SNAPSHOT_ONLY": 0.15,
    }.get(leak_policy, 0.12)
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
    for rec in records:
        text = " ".join([
            rec.get("path", ""),
            rec.get("name", ""),
            rec.get("qualname", ""),
            rec.get("doc", ""),
            rec.get("signature", ""),
        ])
        orbit, confidence = score_orbit(text)
        regime = INFORMATION_REGIME.get(orbit, "LOCAL_ONLY")
        semantic = semantic_role(rec, orbit)
        lagrange = derive_lagrange_roles(rec | {"semantic_role": semantic})
        manybody = derive_manybody_role(rec, orbit, lagrange)
        subsystem_kind = derive_subsystem_kind(rec)
        horizon_id = derive_horizon_id(rec)
        horizon_class = HORIZON_CLASS.get(regime, "SEALED")
        leak_policy = derive_leak_policy(regime)
        visible_scopes = derive_visible_scopes(regime, rec)
        tau_role = TAU_ROLE.get(orbit, "TAU_LOCAL")
        export_confidence = derive_export_confidence(round(confidence, 3), leak_policy)
        internal_id = derive_internal_card_id(rec["id"])
        projection_operator = derive_projection_operator(horizon_class, leak_policy)

        export_card = rec | {
            "card_schema": EXPORT_CARD_SCHEMA,
            "global_attractor_ref": GLOBAL_ATTRACTOR_REF,
            "orbital_role": orbit,
            "orbital_confidence": round(confidence, 3),
            "semantic_role": semantic,
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
            "lagrange_roles": lagrange,
            "internal_card_id": internal_id,
            "projection_operator": projection_operator,
            "export_state": derive_export_state(manybody, horizon_class),
            "export_result": derive_export_result(rec, manybody, orbit),
            "export_confidence": export_confidence,
            "residual_uncertainty": round(max(0.0, 1.0 - export_confidence), 3),
        }
        export_cards.append(export_card)

        internal_card = {
            "internal_card_schema": INTERNAL_CARD_SCHEMA,
            "internal_card_id": internal_id,
            "owner_card_id": rec["id"],
            "owner_horizon_id": horizon_id,
            "container_card_id": export_card["container_card_id"],
            "subsystem_kind": subsystem_kind,
            "manybody_role": manybody,
            "internal_visibility": "PRIVATE_SUBSYSTEM_ONLY",
            "internal_candidate_states": derive_internal_candidate_states(rec, manybody, orbit),
            "internal_conflict_state": derive_internal_conflict_state(horizon_class, manybody),
            "internal_superposition_state": derive_internal_superposition_state(rec),
            "internal_resolution_trace": derive_internal_resolution_trace(manybody, leak_policy),
            "internal_tau_local": f"tau-local:{rec['id']}",
            "internal_memory_mode": MEMORY_MODE.get(orbit, "TRANSIENT_RUNTIME"),
            "projection_operator": projection_operator,
            "export_card_id": rec["id"],
        }
        internal_cards.append(internal_card)
        orbit_counts[orbit] = orbit_counts.get(orbit, 0) + 1

    out_dir = repo_root / "integration" / "registries" / "definitions"
    reg_path = out_dir / "orbital_definition_registry.json"
    internal_path = out_dir / "internal_subsystem_cards.json"
    report_path = out_dir / "orbital_assignment_report.json"
    reg_payload = {
        "schema": "ciel/orbital-definition-registry-enriched/v0.3",
        "card_schema": EXPORT_CARD_SCHEMA,
        "internal_card_schema": INTERNAL_CARD_SCHEMA,
        "global_attractor_ref": GLOBAL_ATTRACTOR_REF,
        "count": len(export_cards),
        "records": export_cards,
    }
    internal_payload = {
        "schema": "ciel/internal-subsystem-card-registry/v0.1",
        "internal_card_schema": INTERNAL_CARD_SCHEMA,
        "count": len(internal_cards),
        "internal_cards": internal_cards,
    }
    report_payload = {
        "schema": "ciel/orbital-assignment-report/v0.3",
        "card_schema": EXPORT_CARD_SCHEMA,
        "internal_card_schema": INTERNAL_CARD_SCHEMA,
        "count": len(export_cards),
        "export_card_count": len(export_cards),
        "internal_card_count": len(internal_cards),
        "orbit_counts": orbit_counts,
        "unresolved": orbit_counts.get("UNRESOLVED", 0),
        "information_regime_counts": count_values(export_cards, "information_regime"),
        "horizon_class_counts": count_values(export_cards, "horizon_class"),
        "tau_role_counts": count_values(export_cards, "tau_role"),
        "manybody_role_counts": count_values(export_cards, "manybody_role"),
        "lagrange_role_counts": count_list_values(export_cards, "lagrange_roles"),
        "projection_operator_counts": count_values(export_cards, "projection_operator"),
        "export_state_counts": count_values(export_cards, "export_state"),
        "internal_memory_mode_counts": count_values(internal_cards, "internal_memory_mode"),
        "internal_conflict_state_counts": count_values(internal_cards, "internal_conflict_state"),
        "internal_visibility_counts": count_values(internal_cards, "internal_visibility"),
    }
    reg_path.write_text(json.dumps(reg_payload, indent=2), encoding="utf-8")
    internal_path.write_text(json.dumps(internal_payload, indent=2), encoding="utf-8")
    report_path.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    print(json.dumps(report_payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
