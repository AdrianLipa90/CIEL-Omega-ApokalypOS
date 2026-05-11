from __future__ import annotations

from typing import Any, Dict, List


def _pluck_text(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for key in ("content", "text", "canonical_text", "canonical_action", "summary"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        if "result" in item and isinstance(item["result"], dict):
            return _pluck_text(item["result"])
    return ""


def summarize_sector_retrieval(ciel_state: Dict[str, Any], *, max_items_per_channel: int = 2) -> Dict[str, List[str]]:
    sector_memory = ciel_state.get("sector_memory") if isinstance(ciel_state.get("sector_memory"), dict) else {}
    retrieval = {}
    governed = sector_memory.get("governed_retrieval") if isinstance(sector_memory.get("governed_retrieval"), dict) else {}
    summary: Dict[str, List[str]] = {}

    ranked = governed.get("ranked") if isinstance(governed.get("ranked"), list) else []
    ranked_lines: List[str] = []
    for row in ranked[: max(1, max_items_per_channel * 2)]:
        if not isinstance(row, dict):
            continue
        txt = _pluck_text(row)
        if not txt:
            txt = str(row.get("text", "") or "").strip()
        if not txt:
            continue
        channel = str(row.get("channel", "memory"))
        hq = row.get("holonomy_quality")
        pa = row.get("phase_alignment")
        tags: List[str] = [channel]
        if isinstance(hq, (int, float)):
            tags.append(f"hq={float(hq):.2f}")
        if isinstance(pa, (int, float)):
            tags.append(f"pa={float(pa):.2f}")
        ranked_lines.append(f"[{', '.join(tags)}] {txt[:200]}")
    if ranked_lines:
        summary["ranked"] = ranked_lines

    if isinstance(governed.get("by_channel"), dict):
        retrieval = governed.get("by_channel")
    elif isinstance(sector_memory.get("retrieval"), dict):
        retrieval = sector_memory.get("retrieval")
    for channel, items in retrieval.items():
        texts: List[str] = []
        if isinstance(items, list):
            for item in items[:max_items_per_channel]:
                txt = _pluck_text(item)
                if txt:
                    texts.append(txt[:200])
        elif isinstance(items, dict):
            txt = _pluck_text(items)
            if txt:
                texts.append(txt[:200])
        if texts:
            summary[str(channel)] = texts
    return summary



def _is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _semantic_state_snippets(ciel_state: Dict[str, Any], *, max_items_per_channel: int = 2) -> List[str]:
    snippets: List[str] = []
    retrieval_summary = summarize_sector_retrieval(ciel_state, max_items_per_channel=max_items_per_channel)
    ranked = retrieval_summary.get("ranked", [])
    if ranked:
        snippets.append("Retrieved semantic memory:")
        for line in ranked[:max_items_per_channel * 2]:
            snippets.append(f"- {line}")

    for channel, items in retrieval_summary.items():
        if channel == "ranked":
            continue
        if not items:
            continue
        snippets.append(f"{channel.capitalize()} channel:")
        for item in items[:max_items_per_channel]:
            snippets.append(f"- {item}")

    sem_labels = ciel_state.get("semantic_labels")
    if isinstance(sem_labels, list) and sem_labels:
        labels = [str(x).strip() for x in sem_labels if str(x).strip()]
        if labels:
            snippets.append("Semantic labels: " + ", ".join(labels[:8]))

    memory_score = ciel_state.get("memory_score")
    if isinstance(memory_score, (int, float)):
        snippets.append(f"Memory score: {float(memory_score):.3f}")

    nonlocal_rt = ciel_state.get("nonlocal_runtime") if isinstance(ciel_state.get("nonlocal_runtime"), dict) else {}
    if nonlocal_rt:
        semantic_key = nonlocal_rt.get("semantic_key")
        coherent_fraction = nonlocal_rt.get("coherent_fraction")
        if _is_nonempty_text(semantic_key):
            snippets.append(f"Nonlocal semantic key: {semantic_key}")
        if isinstance(coherent_fraction, (int, float)):
            snippets.append(f"Nonlocal coherent fraction: {float(coherent_fraction):.3f}")

    euler_bridge = ciel_state.get("euler_bridge") if isinstance(ciel_state.get("euler_bridge"), dict) else {}
    if euler_bridge:
        mem_key = euler_bridge.get("memory_semantic_key")
        if _is_nonempty_text(mem_key):
            snippets.append(f"Euler bridge memory key: {mem_key}")

    lingo_frame = ciel_state.get("lingo_frame") if isinstance(ciel_state.get("lingo_frame"), dict) else {}
    if lingo_frame:
        summary = lingo_frame.get("summary")
        if _is_nonempty_text(summary):
            snippets.append(f"CIELingo summary: {summary}")
        concept_tokens = lingo_frame.get("concept_tokens")
        if isinstance(concept_tokens, list) and concept_tokens:
            snippets.append("CIELingo concepts: " + ", ".join(str(x) for x in concept_tokens[:6] if str(x).strip()))
        operator_tokens = lingo_frame.get("operator_tokens")
        if isinstance(operator_tokens, list) and operator_tokens:
            snippets.append("CIELingo operators: " + ", ".join(str(x) for x in operator_tokens[:6] if str(x).strip()))
        deictic_frame = lingo_frame.get("deictic_frame") if isinstance(lingo_frame.get("deictic_frame"), dict) else {}
        if deictic_frame:
            unresolved = lingo_frame.get("unresolved") if isinstance(lingo_frame.get("unresolved"), list) else []
            if unresolved:
                snippets.append("CIELingo unresolved anchors: " + ", ".join(str(x) for x in unresolved[:6]))
            anchors = deictic_frame.get("anchors") if isinstance(deictic_frame.get("anchors"), list) else []
            relative = deictic_frame.get("relative_anchors") if isinstance(deictic_frame.get("relative_anchors"), list) else []
            if anchors or relative:
                parts: List[str] = []
                for item in (anchors + relative)[:6]:
                    if not isinstance(item, dict):
                        continue
                    parts.append(f"{item.get('operator', '?')}:{item.get('resolution_state', '?')}")
                if parts:
                    snippets.append("CIELingo deictics: " + ", ".join(parts))
        noema_route = lingo_frame.get("noema_route") if isinstance(lingo_frame.get("noema_route"), dict) else {}
        if noema_route:
            confidence = noema_route.get("confidence")
            if isinstance(confidence, (int, float)):
                snippets.append(f"CIELingo NOEMA confidence: {float(confidence):.3f}")
            if bool(noema_route.get("factual_validation_required", False)):
                snippets.append("CIELingo factual validation required: true")
        phase_projection = lingo_frame.get("phase_projection") if isinstance(lingo_frame.get("phase_projection"), dict) else {}
        if phase_projection:
            target = phase_projection.get("target_phase")
            shift = phase_projection.get("target_phase_shift")
            confidence = phase_projection.get("phase_confidence")
            if isinstance(target, (int, float)):
                snippets.append(f"CIELingo phase target: {float(target):.3f}")
            if isinstance(shift, (int, float)):
                snippets.append(f"CIELingo phase shift: {float(shift):.3f}")
            if isinstance(confidence, (int, float)):
                snippets.append(f"CIELingo phase confidence: {float(confidence):.3f}")
        tau_bridge = lingo_frame.get("tau_bridge") if isinstance(lingo_frame.get("tau_bridge"), dict) else {}
        if tau_bridge:
            gradient = tau_bridge.get("tau_gradient_mean")
            imaginal_drive = tau_bridge.get("imaginal_drive")
            curvature = tau_bridge.get("tau_curvature_rms")
            if isinstance(gradient, (int, float)):
                snippets.append(f"CIELingo tau gradient: {float(gradient):.3f}")
            if isinstance(imaginal_drive, (int, float)):
                snippets.append(f"CIELingo imaginal drive: {float(imaginal_drive):.3f}")
            if isinstance(curvature, (int, float)):
                snippets.append(f"CIELingo tau curvature rms: {float(curvature):.3f}")

    runtime_policy = ciel_state.get("runtime_policy") if isinstance(ciel_state.get("runtime_policy"), dict) else {}
    if runtime_policy:
        mode = runtime_policy.get("response_strategy") or runtime_policy.get("control_mode")
        if _is_nonempty_text(mode):
            snippets.append(f"Runtime policy: {mode}")
        durable = runtime_policy.get("durable_write_allowed")
        if isinstance(durable, bool):
            snippets.append(f"Durable write allowed: {str(durable).lower()}")

    return snippets


def build_semantic_speech_context(ciel_state: Dict[str, Any], *, max_items_per_channel: int = 2, max_chars: int = 1600) -> Dict[str, Any]:
    """Build a compact speech-ready semantic brief from M3 and nearby state."""
    snippets = _semantic_state_snippets(ciel_state, max_items_per_channel=max_items_per_channel)
    text = "\n".join(snippets)
    if len(text) > max_chars:
        text = text[: max_chars - 20].rstrip() + "\n[...truncated...]"
    return {
        "text": text,
        "snippets": snippets,
        "retrieval": summarize_sector_retrieval(ciel_state, max_items_per_channel=max_items_per_channel),
    }
