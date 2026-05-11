from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import sys
import math

import numpy as np

from .paths import resolve_project_root
from .jokeheal_atlas import build_mnemonic_atlas


_LINGO_ROOT_SUBPATH = Path("src") / "ciel_lingophysics_lns_repo_v2_3" / "src"
_STOPWORDS = {
    "a", "an", "and", "are", "as", "be", "because", "by", "do", "does", "for",
    "from", "have", "has", "i", "if", "in", "is", "it", "its", "me", "my", "of",
    "on", "or", "our", "the", "their", "then", "there", "this", "that", "to",
    "we", "what", "when", "where", "which", "who", "why", "you",
    "albo", "bo", "by", "czy", "dla", "do", "gdy", "gdyż", "i", "jeśli", "jak",
    "jest", "lub", "na", "nie", "o", "od", "po", "przez", "się", "to", "tu",
    "w", "we", "z", "za", "że",
}
_RELATIVE_DEICTICS = {
    "here": ("space", "Here"),
    "there": ("space", "There"),
    "now": ("time", "Now"),
    "then": ("time", "Then"),
    "this": ("discourse", "This"),
    "that": ("discourse", "That"),
    "tu": ("space", "Here"),
    "tutaj": ("space", "Here"),
    "tam": ("space", "There"),
    "teraz": ("time", "Now"),
    "wtedy": ("time", "Then"),
}
_FUNCTION_WORDS = {
    "and", "or", "if", "then", "because", "when", "while", "how", "what", "where",
    "who", "why", "to", "of", "in", "on", "for", "with", "without", "not",
    "i", "lub", "albo", "jeśli", "gdy", "kiedy", "jak", "czy", "dlaczego", "gdzie",
    "po", "przed", "do", "z", "w", "na", "nad", "pod", "przez",
}
_PHASE_TARGETS = {
    "Here": 0.0,
    "Now": 0.0,
    "This": 0.0,
    "There": math.pi,
    "Then": math.pi,
    "That": math.pi,
    "Somewhere": math.pi / 2.0,
    "Sometime": math.pi / 2.0,
    "Somehow": math.pi / 2.0,
    "Anywhere": 3.0 * math.pi / 2.0,
    "Anytime": 3.0 * math.pi / 2.0,
    "Never": math.pi,
}


def _ensure_lingophysics_on_path(root: Path) -> Path:
    lingo_src = (root / _LINGO_ROOT_SUBPATH).resolve()
    if lingo_src.exists():
        lingo_str = str(lingo_src)
        if lingo_str not in sys.path:
            sys.path.insert(0, lingo_str)
    return lingo_src


def _normalize_tokens(text: str) -> List[str]:
    try:
        from lingophysics.noema_index import tokenize  # noqa: PLC0415

        return tokenize(text)
    except Exception:
        return [tok.lower() for tok in text.split() if tok.strip()]


def _detect_deictic_frame(tokens: List[str], *, deictic_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    try:
        from lingophysics.dynamic_deixis import (  # noqa: PLC0415
            classify_dynamic_surface,
            is_false_precision,
            resolve_dynamic_anchor,
        )
    except Exception:
        classify_dynamic_surface = None  # type: ignore[assignment]
        is_false_precision = None  # type: ignore[assignment]
        resolve_dynamic_anchor = None  # type: ignore[assignment]

    anchors: List[Dict[str, Any]] = []
    unresolved: List[str] = []
    false_precision_risk = 0.0
    for token in tokens:
        classified = classify_dynamic_surface(token) if classify_dynamic_surface else None
        if not classified:
            continue
        try:
            anchor = resolve_dynamic_anchor(classified, context=deictic_context or {}) if resolve_dynamic_anchor else None
        except Exception:
            anchor = None
        if anchor is None:
            continue
        anchor_dict = {
            "surface": token,
            "operator": anchor.operator,
            "domain": anchor.domain,
            "variable": anchor.variable,
            "equation": anchor.equation,
            "resolution_state": anchor.resolution_state,
            "false_precision_risk": float(anchor.false_precision_risk),
        }
        if anchor.resolution_state != "resolved":
            unresolved.append(anchor.operator)
        if is_false_precision and is_false_precision(anchor, rendered_as_precise=False):
            false_precision_risk = max(false_precision_risk, float(anchor.false_precision_risk))
        anchors.append(anchor_dict)

    relative: List[Dict[str, Any]] = []
    for token in tokens:
        info = _RELATIVE_DEICTICS.get(token)
        if not info:
            continue
        domain, operator = info
        relative.append(
            {
                "surface": token,
                "operator": operator,
                "domain": domain,
                "resolution_state": "relative_anchor",
                "false_precision_risk": 0.25,
            }
        )

    return {
        "anchors": anchors,
        "relative_anchors": relative,
        "unresolved": list(dict.fromkeys(unresolved)),
        "false_precision_risk": round(false_precision_risk, 4),
        "anchor_count": len(anchors) + len(relative),
    }


def _detect_operator_tokens(tokens: List[str]) -> List[str]:
    operators: List[str] = []
    for token in tokens:
        if token in _FUNCTION_WORDS:
            operators.append(token)
            continue
        if token.endswith(("ing", "ed")) and len(token) > 4:
            operators.append(token)
    return operators


def _detect_concept_tokens(tokens: List[str]) -> List[str]:
    concepts: List[str] = []
    for token in tokens:
        if len(token) < 3 or token in _STOPWORDS or token in _FUNCTION_WORDS:
            continue
        concepts.append(token)
    return concepts


def _route_noema(text: str, *, language: str | None, noema_index: Dict[str, Any] | None, noema_policy: Dict[str, Any] | None) -> Dict[str, Any]:
    try:
        from lingophysics.noema_router import detect_unresolved, requires_factual_validation, route_query  # noqa: PLC0415
    except Exception:
        detect_unresolved = None  # type: ignore[assignment]
        requires_factual_validation = None  # type: ignore[assignment]
        route_query = None  # type: ignore[assignment]

    if noema_index and noema_policy and route_query:
        route = route_query(text, noema_index, noema_policy, language=language)
    else:
        unresolved = detect_unresolved(text) if detect_unresolved else []
        factual = requires_factual_validation(text) if requires_factual_validation else False
        confidence = max(0.0, 0.62 - 0.12 * len(unresolved) - (0.12 if factual else 0.0))
        route = {
            "query": text,
            "language": language,
            "retrieved": [],
            "bundle": {
                "selected_card_ids": [],
                "selected_refs": [],
                "operator_hooks": [],
                "domains": [],
                "context_size": 0,
            },
            "unresolved": unresolved,
            "confidence": round(confidence, 4),
            "factual_validation_required": factual,
        }
    return route


def render_lingo_summary(frame: Dict[str, Any], *, max_items: int = 4) -> str:
    concepts = ", ".join(frame.get("concept_tokens", [])[:max_items])
    operators = ", ".join(frame.get("operator_tokens", [])[:max_items])
    deictic_bits = []
    for item in (frame.get("deictic_frame", {}).get("anchors", []) or [])[:max_items]:
        deictic_bits.append(f"{item.get('operator')}:{item.get('resolution_state')}")
    for item in (frame.get("deictic_frame", {}).get("relative_anchors", []) or [])[:max_items]:
        deictic_bits.append(f"{item.get('operator')}:{item.get('surface')}")
    unresolved = ", ".join(frame.get("unresolved", [])[:max_items])
    route = frame.get("noema_route", {})
    conf = float(route.get("confidence", frame.get("projection_confidence", 0.0)) or 0.0)
    factual = "yes" if route.get("factual_validation_required") else "no"
    atlas = frame.get("mnemonic_atlas", {}) if isinstance(frame.get("mnemonic_atlas"), dict) else {}
    mnemonic_pressure = float(atlas.get("mnemonic_pressure", 0.0) or 0.0)
    return (
        f"CIELingo|concepts={concepts or '-'}|operators={operators or '-'}"
        f"|deictic={';'.join(deictic_bits) or '-'}|unresolved={unresolved or '-'}"
        f"|factual={factual}|noema_conf={conf:.3f}|mnemonic_pressure={mnemonic_pressure:.3f}"
    )


def compute_phase_projection(frame: Dict[str, Any]) -> Dict[str, Any]:
    """Project deictic structure onto a phase target without changing the field."""
    deictic_frame = frame.get("deictic_frame") if isinstance(frame.get("deictic_frame"), dict) else {}
    anchors = (deictic_frame.get("anchors") or []) if isinstance(deictic_frame.get("anchors"), list) else []
    relative = (deictic_frame.get("relative_anchors") or []) if isinstance(deictic_frame.get("relative_anchors"), list) else []

    phase_terms: list[tuple[float, float]] = []
    for item in [*anchors, *relative]:
        if not isinstance(item, dict):
            continue
        operator = str(item.get("operator", ""))
        angle = _PHASE_TARGETS.get(operator)
        if angle is None:
            continue
        weight = 1.0
        if item.get("resolution_state") == "resolved":
            weight += 0.5
        if item.get("resolution_state") == "relative_anchor":
            weight += 0.2
        weight *= max(0.1, 1.0 - float(item.get("false_precision_risk", 0.0) or 0.0))
        phase_terms.append((angle, weight))

    if phase_terms:
        vec = sum(w * complex(math.cos(a), math.sin(a)) for a, w in phase_terms)
        if abs(vec) < 1e-12:
            target = 0.0
        else:
            target = float(math.atan2(vec.imag, vec.real) % (2.0 * math.pi))
    else:
        target = 0.0

    unresolved_count = len(frame.get("unresolved", []) or [])
    confidence = float(frame.get("projection_confidence", 0.0) or 0.0)
    confidence = max(0.0, min(1.0, confidence - 0.04 * unresolved_count + 0.05 * bool(phase_terms)))
    shift = math.atan2(math.sin(target), math.cos(target))
    return {
        "target_phase": round(target, 6),
        "target_phase_shift": round(shift, 6),
        "phase_confidence": round(confidence, 4),
        "phase_anchor_count": len(phase_terms),
        "phase_domain_count": len({str(item.get("domain")) for item in [*anchors, *relative] if isinstance(item, dict) and item.get("domain")}),
    }


def compute_tau_bridge(frame: Dict[str, Any]) -> Dict[str, Any]:
    """Derive a tau-gradient / imaginal drive profile from semantic phase projection."""
    tokens = frame.get("tokens", []) if isinstance(frame.get("tokens"), list) else []
    n = max(2, len(tokens))
    phase_projection = frame.get("phase_projection") if isinstance(frame.get("phase_projection"), dict) else {}
    target_phase = float(phase_projection.get("target_phase", 0.0) or 0.0)
    phase_confidence = float(phase_projection.get("phase_confidence", 0.0) or 0.0)
    semantic_density = float(frame.get("cqcl_hint", {}).get("semantic_density", 0.0) or 0.0)
    deictic_density = float(frame.get("cqcl_hint", {}).get("deictic_density", 0.0) or 0.0)
    mnemonic_atlas = frame.get("mnemonic_atlas", {}) if isinstance(frame.get("mnemonic_atlas"), dict) else {}
    mnemonic_pressure = float(mnemonic_atlas.get("mnemonic_pressure", 0.0) or 0.0)
    symbolic_pull = float(mnemonic_atlas.get("symbolic_pull", 0.0) or 0.0)
    unresolved_count = len(frame.get("unresolved", []) or [])

    tau_axis = np.linspace(0.0, 1.0, n, dtype=float)
    imaginal_drive = (
        0.30 * semantic_density
        + 0.22 * deictic_density
        + 0.16 * (1.0 - phase_confidence)
        + 0.10 * min(1.0, unresolved_count / 4.0)
        + 0.12 * mnemonic_pressure
        + 0.10 * symbolic_pull
    )
    imaginal_drive = float(max(0.0, min(1.0, imaginal_drive)))

    curvature_gain = imaginal_drive * (0.35 + 0.35 * (1.0 - phase_confidence))
    tau_profile = target_phase * tau_axis + curvature_gain * np.sin(np.pi * tau_axis)
    tau_gradient = np.gradient(tau_profile)
    tau_curvature = np.gradient(tau_gradient)
    tau_gradient_mean = float(np.mean(tau_gradient))
    tau_gradient_rms = float(np.sqrt(np.mean(np.square(tau_gradient))))
    tau_curvature_rms = float(np.sqrt(np.mean(np.square(tau_curvature))))
    potential_strength = float(np.clip(0.5 * imaginal_drive + 0.5 * (1.0 - phase_confidence), 0.0, 1.0))

    return {
        "tau_axis": [round(float(x), 6) for x in tau_axis.tolist()],
        "tau_profile": [round(float(x), 6) for x in tau_profile.tolist()],
        "tau_gradient": [round(float(x), 6) for x in tau_gradient.tolist()],
        "tau_curvature": [round(float(x), 6) for x in tau_curvature.tolist()],
        "tau_gradient_mean": round(tau_gradient_mean, 6),
        "tau_gradient_rms": round(tau_gradient_rms, 6),
        "tau_curvature_rms": round(tau_curvature_rms, 6),
        "imaginal_drive": round(imaginal_drive, 4),
        "phase_potential_strength": round(potential_strength, 4),
        "semantic_density": round(semantic_density, 4),
        "deictic_density": round(deictic_density, 4),
        "mnemonic_pressure": round(mnemonic_pressure, 4),
        "symbolic_pull": round(symbolic_pull, 4),
    }


def build_lingo_frame(
    text: str,
    *,
    ciel_state: Dict[str, Any] | None = None,
    language: str | None = None,
) -> Dict[str, Any]:
    """Compile a deterministic CIELingo frame for CQCL and Orbital routing."""
    ciel_state = ciel_state or {}
    root = resolve_project_root(Path(__file__))
    _ensure_lingophysics_on_path(root)

    tokens = _normalize_tokens(text)
    concept_tokens = _detect_concept_tokens(tokens)
    operator_tokens = _detect_operator_tokens(tokens)
    deictic_context = ciel_state.get("deictic_context") if isinstance(ciel_state.get("deictic_context"), dict) else {}
    deictic_frame = _detect_deictic_frame(tokens, deictic_context=deictic_context)
    noema_index = ciel_state.get("noema_index") if isinstance(ciel_state.get("noema_index"), dict) else None
    noema_policy = ciel_state.get("noema_policy") if isinstance(ciel_state.get("noema_policy"), dict) else None
    route = _route_noema(text, language=language or ciel_state.get("language"), noema_index=noema_index, noema_policy=noema_policy)
    mnemonic_atlas = build_mnemonic_atlas()

    unresolved = list(dict.fromkeys([
        *deictic_frame.get("unresolved", []),
        *(route.get("unresolved", []) or []),
    ]))
    if deictic_frame.get("relative_anchors"):
        unresolved.extend([item["operator"] for item in deictic_frame["relative_anchors"] if item.get("resolution_state") == "relative_anchor"])
        unresolved = list(dict.fromkeys(unresolved))

    projection_confidence = float(route.get("confidence", 0.0))
    projection_confidence -= 0.05 * len(unresolved)
    projection_confidence -= 0.04 * len(deictic_frame.get("anchors", []))
    projection_confidence = max(0.0, min(1.0, projection_confidence + 0.03 * bool(concept_tokens)))

    composition_valid = bool(concept_tokens) and bool(operator_tokens or deictic_frame.get("anchors") or deictic_frame.get("relative_anchors"))
    dialect_variant = ciel_state.get("dialect_variant")
    dialect_review_required = bool(ciel_state.get("dialect_review_required", False))

    frame = {
        "text": text,
        "tokens": tokens,
        "concept_tokens": concept_tokens,
        "operator_tokens": operator_tokens,
        "deictic_frame": deictic_frame,
        "unresolved": unresolved,
        "composition_valid": composition_valid,
        "projection_confidence": round(projection_confidence, 4),
        "factual_validation_required": bool(route.get("factual_validation_required", False)),
        "dialect_variant": dialect_variant,
        "dialect_review_required": dialect_review_required,
        "noema_route": route,
        "mnemonic_atlas": mnemonic_atlas,
        "cqcl_hint": {
            "semantic_density": round(min(1.0, len(concept_tokens) / max(1, len(tokens))), 4),
            "operator_density": round(min(1.0, len(operator_tokens) / max(1, len(tokens))), 4),
            "deictic_density": round(min(1.0, deictic_frame.get("anchor_count", 0) / max(1, len(tokens))), 4),
            "confidence": round(projection_confidence, 4),
        },
    }
    frame["phase_projection"] = compute_phase_projection(frame)
    frame["tau_bridge"] = compute_tau_bridge(frame)
    frame["summary"] = render_lingo_summary(frame)
    return frame
