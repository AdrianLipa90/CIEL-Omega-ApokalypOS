"""NOEMA router for CIELingo v2.2."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json

from .noema_index import compact_context_bundle, load_noema_index, search_noema, tokenize

UNRESOLVED_MARKERS = {
    "somewhere", "sometime", "somehow", "gdzieś", "kiedyś", "jakoś",
    "not", "nie", "none", "żaden", "nikt", "unresolved"
}
FACTUAL_MARKERS = {"fact", "source", "prove", "dowód", "źródło", "fakt", "czy naprawdę", "verify"}


def load_routing_policy(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def detect_unresolved(query: str) -> List[str]:
    tokens = set(tokenize(query))
    found: List[str] = []
    if tokens & UNRESOLVED_MARKERS:
        found.append("unresolved_anchor_or_scope")
    if "?" in query:
        found.append("question_operator")
    return found


def requires_factual_validation(query: str) -> bool:
    lower = query.lower()
    return any(marker in lower for marker in FACTUAL_MARKERS)


def route_query(query: str, index: Dict[str, Any], policy: Dict[str, Any], language: str | None = None) -> Dict[str, Any]:
    results = search_noema(query, index, policy=policy, language=language)
    bundle = compact_context_bundle(results)
    unresolved = detect_unresolved(query)
    confidence = 0.0
    if results:
        confidence = sum(item["score"] for item in results[:3]) / min(3, len(results))
        # Penalize unresolved anchors because they need later binding.
        confidence = max(0.0, confidence - 0.10 * len(unresolved))
    route = {
        "query": query,
        "language": language,
        "retrieved": results,
        "bundle": bundle,
        "unresolved": unresolved,
        "confidence": round(confidence, 4),
        "factual_validation_required": requires_factual_validation(query),
    }
    return route


def route_query_from_files(query: str, index_path: str | Path, policy_path: str | Path, language: str | None = None) -> Dict[str, Any]:
    return route_query(query, load_noema_index(index_path), load_routing_policy(policy_path), language=language)
