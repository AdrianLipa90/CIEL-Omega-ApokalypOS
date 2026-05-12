from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from typing import Any, Mapping


def _get(src: Mapping[str, Any] | None, key: str, default: Any = None) -> Any:
    if not isinstance(src, Mapping):
        return default
    return src.get(key, default)


def _listify(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if value:
        return [str(value)]
    return []


@dataclass(frozen=True)
class CognitiveFragment:
    fragment_id: str
    event_id: str | None
    phase_snapshot_id: str
    qualisensing_id: str
    fragment_type: str
    semantic_operator: str
    target_relation: str
    unresolved_tension: float
    activation_weight: float
    decay_rate: float
    promotion_score: float
    source_memory_refs: list[str] = field(default_factory=list)
    source_noema_refs: list[str] = field(default_factory=list)
    status: str = "active"
    ts_created: str = ""
    ts_updated: str = ""


@dataclass(frozen=True)
class MemoryCandidate:
    candidate_id: str
    origin_event_ids: list[str]
    phase_snapshot_refs: list[str]
    qualisensing_refs: list[str]
    fragment_refs: list[str]
    density_score: float
    recurrence_score: float
    relational_centrality: float
    phase_alignment_score: float
    consolidation_priority: float
    candidate_type: str
    status: str = "pending"
    ts_created: str = ""


@dataclass(frozen=True)
class DurableMemoryObject:
    durable_id: str
    source_candidate_id: str
    memory_type: str
    summary: str
    semantic_summary: str
    affective_signature: str
    phase_anchor: str
    qualisensing_residue: str
    provenance_refs: list[str]
    noema_refs: list[str]
    timeline_refs: list[str]
    crosslink_refs: list[str]
    consolidation_confidence: float
    reconsolidation_needed: bool
    status: str = "durable"
    ts_created: str = ""
    ts_updated: str = ""


@dataclass(frozen=True)
class NoemaMemoryLink:
    link_id: str
    memory_id: str
    noema_object_id: str
    relation_type: str
    link_weight: float
    activation_policy: str
    provenance_refs: list[str]
    ts: str


@dataclass(frozen=True)
class DurableMemoryHealth:
    health_id: str
    durable_id: str
    health_score: float
    stability_score: float
    system_health: float
    coherence_index: float
    closure_penalty: float
    noema_confidence: float
    reconsolidation_needed: bool
    health_state: str
    health_reason: str
    ts: str


def build_cognitive_fragment(state: Mapping[str, Any]) -> CognitiveFragment:
    phase = _get(state, "phase_snapshot", {}) if isinstance(_get(state, "phase_snapshot", {}), Mapping) else {}
    quali = _get(state, "qualisensing_snapshot", {}) if isinstance(_get(state, "qualisensing_snapshot", {}), Mapping) else {}
    unresolved_count = int(_get(state, "lingo_unresolved_count", 0) or 0)
    concept_count = int(_get(state, "lingo_concept_count", 0) or 0)
    operator_count = int(_get(state, "lingo_operator_count", 0) or 0)
    noema_conf = float(_get(state, "lingo_noema_confidence", 0.0) or 0.0)
    emotional_pull = float(_get(quali, "field_confidence", _get(state, "memory_projection_confidence", 0.0)) or 0.0)
    phase_conf = float(_get(phase, "lingo_phase_confidence", 0.0) or 0.0)
    unresolved_tension = min(1.0, 0.25 * unresolved_count + max(0.0, 0.35 - noema_conf))
    activation_weight = max(0.0, 0.5 * emotional_pull + 0.3 * phase_conf + 0.2 * min(1.0, concept_count / 8.0))
    decay_rate = max(0.05, 1.0 - activation_weight)
    promotion_score = max(0.0, 0.45 * activation_weight + 0.25 * (1.0 - unresolved_tension) + 0.15 * min(1.0, operator_count / 6.0) + 0.15 * noema_conf)

    if unresolved_count >= 3:
        fragment_type = "unresolved_question"
        semantic_operator = "resolve"
        target_relation = "tension"
    elif concept_count >= 5:
        fragment_type = "semantic_projection"
        semantic_operator = "project"
        target_relation = "meaning"
    else:
        fragment_type = "active_relation"
        semantic_operator = "link"
        target_relation = "context"

    ts = str(_get(state, "ts", "") or "")
    cycle_index = int(_get(state, "cycle_index", 0) or 0)
    identity_phase = int(float(_get(state, "identity_phase", 0.0) or 0.0) * 1_000_000)
    quali_id = str(_get(state, "qualisensing_id", "") or "")
    phase_id = str(_get(state, "phase_snapshot_id", "") or "")
    fragment_id = f"frag:{cycle_index}:{identity_phase}:{fragment_type}"
    return CognitiveFragment(
        fragment_id=fragment_id,
        event_id=str(_get(state, "event_id", "") or "") or None,
        phase_snapshot_id=phase_id,
        qualisensing_id=quali_id,
        fragment_type=fragment_type,
        semantic_operator=semantic_operator,
        target_relation=target_relation,
        unresolved_tension=round(unresolved_tension, 4),
        activation_weight=round(activation_weight, 4),
        decay_rate=round(decay_rate, 4),
        promotion_score=round(promotion_score, 4),
        source_memory_refs=_listify(_get(state, "source_memory_refs", [])),
        source_noema_refs=_listify(_get(state, "source_noema_refs", [])),
        status="active" if promotion_score < 0.75 else "promoted",
        ts_created=ts,
        ts_updated=ts,
    )


def build_memory_candidate(state: Mapping[str, Any], *, fragment: CognitiveFragment) -> MemoryCandidate:
    phase = _get(state, "phase_snapshot", {}) if isinstance(_get(state, "phase_snapshot", {}), Mapping) else {}
    quali = _get(state, "qualisensing_snapshot", {}) if isinstance(_get(state, "qualisensing_snapshot", {}), Mapping) else {}
    phase_alignment = max(0.0, min(1.0, float(_get(phase, "coherence_index", _get(state, "coherence_index", 0.0)) or 0.0)))
    recurrence = max(0.0, min(1.0, float(_get(quali, "recurrence_pressure", _get(state, "jokeheal_recurrence_pressure", 0.0)) or 0.0)))
    relational = max(0.0, min(1.0, float(_get(state, "jokeheal_symbolic_pull", 0.0) or 0.0)))
    density = max(0.0, min(1.0, 0.5 * fragment.activation_weight + 0.25 * recurrence + 0.25 * relational))
    consolidation_priority = max(0.0, min(1.0, 0.45 * density + 0.35 * phase_alignment + 0.20 * fragment.promotion_score))
    candidate_type = "episodic"
    if fragment.fragment_type == "semantic_projection":
        candidate_type = "semantic"
    elif fragment.fragment_type == "unresolved_question":
        candidate_type = "operatorial"
    elif relational > 0.6:
        candidate_type = "relational"
    origin_event_id = str(_get(state, "event_id", "") or "") or None
    cycle_index = int(_get(state, "cycle_index", 0) or 0)
    candidate_id = f"cand:{cycle_index}:{fragment.fragment_type}:{int(density * 1000)}"
    return MemoryCandidate(
        candidate_id=candidate_id,
        origin_event_ids=[origin_event_id] if origin_event_id else [],
        phase_snapshot_refs=[str(_get(state, "phase_snapshot_id", "") or "")] if _get(state, "phase_snapshot_id", "") else [],
        qualisensing_refs=[str(_get(state, "qualisensing_id", "") or "")] if _get(state, "qualisensing_id", "") else [],
        fragment_refs=[fragment.fragment_id],
        density_score=round(density, 4),
        recurrence_score=round(recurrence, 4),
        relational_centrality=round(relational, 4),
        phase_alignment_score=round(phase_alignment, 4),
        consolidation_priority=round(consolidation_priority, 4),
        candidate_type=candidate_type,
        status="pending" if consolidation_priority < 0.75 else "ready",
        ts_created=str(_get(state, "ts", "") or ""),
    )


def promote_memory_candidate(
    state: Mapping[str, Any],
    *,
    candidate: MemoryCandidate,
    fragment: CognitiveFragment,
) -> DurableMemoryObject:
    confidence = round(max(0.0, min(1.0, candidate.consolidation_priority)), 4)
    phase_id = str(_get(state, "phase_snapshot_id", "") or candidate.phase_snapshot_refs[0] if candidate.phase_snapshot_refs else "")
    quali_id = str(_get(state, "qualisensing_id", "") or candidate.qualisensing_refs[0] if candidate.qualisensing_refs else "")
    emotion = str(_get(state, "dominant_emotion", "") or "")
    sub_affect = str(_get(state, "sub_affect", "") or "")
    summary = str(_get(state, "lingo_summary", "") or _get(state, "ciel_status", "cognitive memory") or "cognitive memory")
    semantic_summary = f"{fragment.fragment_type}:{fragment.semantic_operator}:{fragment.target_relation}"
    durable_id = f"dur:{candidate.candidate_id}"
    return DurableMemoryObject(
        durable_id=durable_id,
        source_candidate_id=candidate.candidate_id,
        memory_type=candidate.candidate_type,
        summary=summary,
        semantic_summary=semantic_summary,
        affective_signature=f"{emotion}|{sub_affect}".strip("|"),
        phase_anchor=phase_id,
        qualisensing_residue=quali_id,
        provenance_refs=[r for r in [str(_get(state, "event_id", "") or "")] if r],
        noema_refs=list(dict.fromkeys([*candidate.qualisensing_refs, *fragment.source_noema_refs])),
        timeline_refs=[str(_get(state, "phase_snapshot_id", "") or "")] if _get(state, "phase_snapshot_id", "") else [],
        crosslink_refs=list(dict.fromkeys([fragment.fragment_id, candidate.candidate_id])),
        consolidation_confidence=confidence,
        reconsolidation_needed=confidence < 0.75,
        status="promoted" if confidence >= 0.75 else "durable_pending",
        ts_created=str(_get(state, "ts", "") or ""),
        ts_updated=str(_get(state, "ts", "") or ""),
    )


def build_noema_memory_link(
    state: Mapping[str, Any],
    *,
    durable: DurableMemoryObject,
) -> NoemaMemoryLink:
    noema_route = _get(state, "lingo_frame", {}) if isinstance(_get(state, "lingo_frame", {}), Mapping) else {}
    route = _get(noema_route, "noema_route", {}) if isinstance(_get(noema_route, "noema_route", {}), Mapping) else {}
    bundle = _get(route, "bundle", {}) if isinstance(_get(route, "bundle", {}), Mapping) else {}
    selected_refs = _listify(_get(bundle, "selected_refs", []))
    selected_cards = _listify(_get(bundle, "selected_card_ids", []))
    noema_object_id = selected_refs[0] if selected_refs else (selected_cards[0] if selected_cards else f"noema:route:{_get(state, 'cycle_index', 0) or 0}")
    confidence = float(_get(route, "confidence", 0.0) or 0.0)
    relation_type = "semantic_anchor" if confidence >= 0.6 else "context_anchor"
    activation_policy = "phase_resonant" if durable.status == "promoted" else "phase_pending"
    ts = str(_get(state, "ts", "") or "")
    link_id = f"link:{durable.durable_id}:{noema_object_id}"
    provenance_refs = [r for r in [str(_get(state, "event_id", "") or ""), durable.source_candidate_id] if r]
    return NoemaMemoryLink(
        link_id=link_id,
        memory_id=durable.durable_id,
        noema_object_id=noema_object_id,
        relation_type=relation_type,
        link_weight=round(max(0.0, min(1.0, confidence * durable.consolidation_confidence or confidence)), 4),
        activation_policy=activation_policy,
        provenance_refs=provenance_refs,
        ts=ts,
    )


def assess_durable_memory_health(
    state: Mapping[str, Any],
    *,
    durable: DurableMemoryObject,
    noema_link: NoemaMemoryLink | None = None,
) -> tuple[DurableMemoryObject, DurableMemoryHealth]:
    system_health = max(0.0, min(1.0, float(_get(state, "system_health", 0.0) or 0.0)))
    coherence_index = max(0.0, min(1.0, float(_get(state, "coherence_index", 0.0) or 0.0)))
    closure_penalty = max(0.0, float(_get(state, "closure_penalty", 0.0) or 0.0))
    noema_confidence = max(0.0, min(1.0, float(_get(state, "lingo_noema_confidence", 0.0) or 0.0)))
    link_weight = max(0.0, min(1.0, float((noema_link.link_weight if noema_link else 0.0) or 0.0)))

    stability_score = max(
        0.0,
        min(
            1.0,
            0.40 * durable.consolidation_confidence
            + 0.25 * system_health
            + 0.20 * coherence_index
            + 0.10 * link_weight
            + 0.05 * max(0.0, 1.0 - min(1.0, closure_penalty)),
        ),
    )
    needs_recon = (
        durable.reconsolidation_needed
        or stability_score < 0.72
        or system_health < 0.50
        or coherence_index < 0.78
        or closure_penalty > 0.55
        or noema_confidence < 0.60
        or link_weight < 0.50
    )
    if stability_score >= 0.82 and not needs_recon:
        state_label = "healthy"
    elif stability_score >= 0.72:
        state_label = "watch"
    else:
        state_label = "reconsolidate"

    reasons: list[str] = []
    if system_health < 0.50:
        reasons.append("system_health_low")
    if coherence_index < 0.78:
        reasons.append("coherence_low")
    if closure_penalty > 0.55:
        reasons.append("closure_stress_high")
    if noema_confidence < 0.60:
        reasons.append("noema_confidence_low")
    if link_weight < 0.50:
        reasons.append("noema_link_weak")
    if durable.consolidation_confidence < 0.75:
        reasons.append("candidate_confidence_low")

    health = DurableMemoryHealth(
        health_id=f"health:{durable.durable_id}",
        durable_id=durable.durable_id,
        health_score=round(stability_score, 4),
        stability_score=round(stability_score, 4),
        system_health=round(system_health, 4),
        coherence_index=round(coherence_index, 4),
        closure_penalty=round(closure_penalty, 4),
        noema_confidence=round(noema_confidence, 4),
        reconsolidation_needed=needs_recon,
        health_state=state_label,
        health_reason=";".join(reasons) if reasons else "stable",
        ts=str(_get(state, "ts", "") or ""),
    )

    updated_durable = replace(
        durable,
        reconsolidation_needed=needs_recon,
        status="reconsolidate" if needs_recon else ("watch" if state_label == "watch" else durable.status),
        ts_updated=str(_get(state, "ts", "") or durable.ts_updated),
    )
    return updated_durable, health


def snapshot_to_dict(snapshot: CognitiveFragment | MemoryCandidate | DurableMemoryObject | NoemaMemoryLink | DurableMemoryHealth) -> dict[str, Any]:
    return asdict(snapshot)
