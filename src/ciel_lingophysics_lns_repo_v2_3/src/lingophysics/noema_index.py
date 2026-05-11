"""NOEMA index primitives for CIELingo v2.2.

The index is intentionally lightweight: it routes queries to concept/operator/
grammar cards before any model is invoked. It is not a vector database yet; it
is a deterministic seed layer that can later be backed by embeddings or graph
indices.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence
import json
import re

TOKEN_RE = re.compile(r"[\wąćęłńóśźżÄÖÜäöüßÀ-ÿ]+", re.UNICODE)


@dataclass(frozen=True)
class NoemaCard:
    id: str
    canonical_ref: str
    card_type: str
    labels: Dict[str, List[str]]
    domains: List[str]
    operator_hooks: List[str]
    relations: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    status: str = "draft"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NoemaCard":
        labels = {
            str(lang): [str(v).lower() for v in values]
            for lang, values in (data.get("labels") or {}).items()
        }
        return cls(
            id=str(data["id"]),
            canonical_ref=str(data["canonical_ref"]),
            card_type=str(data["card_type"]),
            labels=labels,
            domains=[str(x).lower() for x in data.get("domains", [])],
            operator_hooks=[str(x) for x in data.get("operator_hooks", [])],
            relations=list(data.get("relations", [])),
            confidence=float(data.get("confidence", 0.0)),
            status=str(data.get("status", "draft")),
        )

    def all_label_tokens(self) -> set[str]:
        tokens: set[str] = set()
        for values in self.labels.values():
            for label in values:
                tokens.update(tokenize(label))
        return tokens

    def has_language(self, language: str | None) -> bool:
        return language is None or language in self.labels


def tokenize(text: str) -> List[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


def load_noema_index(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def cards_from_index(index: Dict[str, Any]) -> List[NoemaCard]:
    return [NoemaCard.from_dict(card) for card in index.get("cards", [])]


def score_card(query_tokens: Sequence[str], card: NoemaCard, policy: Dict[str, Any] | None = None) -> float:
    weights = ((policy or {}).get("retrieval") or {}).get("score_weights", {})
    exact_w = float(weights.get("exact_label_match", 0.50))
    partial_w = float(weights.get("partial_label_match", 0.25))
    op_w = float(weights.get("operator_hook_match", 0.35))
    domain_w = float(weights.get("domain_match", 0.20))
    status_w = float(weights.get("status_bonus_curated_seed", 0.08))

    q = {t.lower() for t in query_tokens}
    labels = card.all_label_tokens()
    domains = set(card.domains)
    hooks = {h.lower() for h in card.operator_hooks}
    score = 0.0

    if q & labels:
        score += exact_w * len(q & labels) / max(1, len(q))
    # Partial label matching for compounds / inflected forms.
    for token in q:
        if any(token in label or label in token for label in labels if len(token) >= 3 and len(label) >= 3):
            score += partial_w / max(1, len(q))
    if q & hooks:
        score += op_w * len(q & hooks) / max(1, len(q))
    if q & domains:
        score += domain_w * len(q & domains) / max(1, len(q))
    if card.status == "curated_seed":
        score += status_w
    score += 0.10 * card.confidence
    return round(min(score, 1.0), 4)


def search_noema(
    query: str,
    index: Dict[str, Any],
    policy: Dict[str, Any] | None = None,
    language: str | None = None,
    limit: int | None = None,
) -> List[Dict[str, Any]]:
    query_tokens = tokenize(query)
    retrieval = (policy or {}).get("retrieval", {})
    min_score = float(retrieval.get("minimum_score", 0.0))
    lim = int(limit or retrieval.get("default_limit", 8))
    ranked = []
    for card in cards_from_index(index):
        if not card.has_language(language):
            continue
        score = score_card(query_tokens, card, policy)
        if score >= min_score:
            ranked.append({"id": card.id, "canonical_ref": card.canonical_ref, "card_type": card.card_type, "score": score, "confidence": card.confidence, "operator_hooks": card.operator_hooks, "domains": card.domains, "status": card.status})
    ranked.sort(key=lambda item: (item["score"], item["confidence"]), reverse=True)
    return ranked[:lim]


def compact_context_bundle(results: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = list(results)
    operators = sorted({op for item in items for op in item.get("operator_hooks", [])})
    domains = sorted({dom for item in items for dom in item.get("domains", [])})
    return {
        "selected_card_ids": [item["id"] for item in items],
        "selected_refs": [item["canonical_ref"] for item in items],
        "operator_hooks": operators,
        "domains": domains,
        "context_size": len(items),
    }
