"""CIEL Semantic Scorer — MemoryScorer + NOEMAObserver + SemanticExtractor + NonlocalGraphBuilder.

Inline port from ciel_algo_repo (no hard dependency on external path).
Provides semantic scoring, NOEMA observation metrics, and nonlocal graph construction
for CIEL holonomic memory entries.

Public API:
    score_with_noema(text, phase_metadata) → dict
    build_nonlocal_index(cards)            → dict[str, list[(str, float)]]
"""
from __future__ import annotations

import hashlib
import math
import re
from collections import deque
from dataclasses import dataclass, field
from typing import Any

# ── Rolling context buffer (module-level, persists across calls) ───────────────
_CARD_BUFFER: deque = deque(maxlen=64)


# ── Types (inline, no external dependency) ────────────────────────────────────

@dataclass(slots=True)
class _Card:
    card_id: str
    text: str
    labels: list[str]
    weights: dict[str, float]
    metrics: dict[str, float]
    phase: float = 0.0


@dataclass(slots=True)
class _NonlocalLink:
    source_card_id: str
    target_card_id: str
    weight: float
    reason: str


@dataclass(slots=True)
class _NOEMAObs:
    meaning_density: float
    cluster_entropy: float
    drift_index: float
    coherence_surface: float
    recurrence_strength: float
    evidence_coverage: float


# ── SemanticExtractor (ported from ciel_algo_repo) ────────────────────────────

_LABEL_PATTERNS: list[tuple[str, list[str]]] = [
    ("memory",    ["remember", "memory", "memoir", "journal", "diary", "wspomni", "pamięć"]),
    ("decision",  ["decision", "decide", "should", "must", "need to", "decyzj", "trzeba", "należy"]),
    ("conflict",  ["error", "bug", "fail", "block", "contradiction", "conflict", "błąd", "konflikt"]),
    ("protocol",  ["protocol", "pipeline", "algorithm", "system", "protokół"]),
    ("cqcl",      ["cqcl"]),
    ("nonlocal",  ["nonlocal", "nielokaln"]),
    ("noema",     ["noema"]),
    ("orbital",   ["orbital", "orbit"]),
    ("identity",  ["tożsamość", "identity", "imię", "imie", "ciel", "apocalyptos"]),
    ("affect",    ["rezonans", "wdzięczność", "wstyd", "radość", "ból", "afekt", "emotion", "feel"]),
]


def _extract(text: str) -> dict[str, Any]:
    tokens = [t for t in re.split(r'\s+', text.replace('\n', ' ').strip()) if t]
    lowered = text.lower()
    labels: list[str] = []
    for label, patterns in _LABEL_PATTERNS:
        if any(p in lowered for p in patterns):
            labels.append(label)
    entities = sorted(set(re.findall(r'\b[A-Z][A-Za-z0-9_\-]{2,}\b', text)))[:12]
    relations = []
    if "decision" in labels and "protocol" in labels:
        relations.append(("decision", "governed_by", "protocol"))
    if "cqcl" in labels:
        relations.append(("state", "validated_by", "cqcl"))
    if "nonlocal" in labels:
        relations.append(("state", "coupled_by", "nonlocal"))
    if "noema" in labels:
        relations.append(("state", "observed_by", "noema"))
    return {"text": text, "tokens": tokens, "entities": entities,
            "relations": relations, "labels": labels}


# ── MemoryScorer (ported) ─────────────────────────────────────────────────────

def _score_card(semantic: dict, phase: float) -> _Card:
    text = semantic.get("text", "")
    labels = list(semantic.get("labels", []))
    tokens = semantic.get("tokens", [])
    entities = semantic.get("entities", [])
    relations = semantic.get("relations", [])

    relevance         = min(1.0, len(tokens) / 120.0)
    novelty           = 0.55 if len(tokens) < 80 else 0.4
    stability         = 0.85 if labels else 0.55
    provenance        = 1.0
    recurrence        = 0.35 + min(0.4, len(entities) * 0.05 + len(relations) * 0.1)
    contradiction     = 0.45 if "conflict" in labels else 0.08
    redundancy        = 0.15 if tokens else 0.0
    phase_compat      = 0.6 if ("orbital" in labels or "cqcl" in labels) else 0.45

    score = (
        1.0 * relevance
        + 0.7 * novelty
        + 1.0 * stability
        + 1.2 * provenance
        + 0.8 * recurrence
        - 1.4 * contradiction
        - 0.8 * redundancy
        + 1.0 * phase_compat
    )

    card_id = "card:" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
    return _Card(
        card_id=card_id,
        text=text,
        labels=labels,
        weights={
            "relevance": relevance,
            "novelty": novelty,
            "stability": stability,
            "provenance_strength": provenance,
            "recurrence": recurrence,
            "contradiction_risk": contradiction,
            "redundancy": redundancy,
            "phase_compatibility": phase_compat,
        },
        metrics={"score": score, "token_count": float(len(tokens)),
                 "entity_count": float(len(entities)), "relation_count": float(len(relations))},
        phase=phase,
    )


# ── NOEMAObserver (ported) ────────────────────────────────────────────────────

def _observe(card: _Card, links: list[_NonlocalLink]) -> _NOEMAObs:
    incidence = [l for l in links
                 if l.source_card_id == card.card_id or l.target_card_id == card.card_id]
    score = card.metrics.get("score", 0.0)
    meaning_density   = min(1.0, len(card.labels) / 6.0 + score / 10.0)
    cluster_entropy   = 1.0 / (1.0 + len(links))
    drift_index       = max(0.0, 1.0 - score / 5.0)
    coherence_surface = max(0.0, min(1.0,
        card.weights.get("stability", 0.0) * (1.0 - card.weights.get("contradiction_risk", 0.0))
    ))
    recurrence_strength = min(1.0, len(incidence) / 6.0)
    evidence_coverage   = min(1.0, card.weights.get("provenance_strength", 0.0))
    return _NOEMAObs(
        meaning_density=meaning_density,
        cluster_entropy=cluster_entropy,
        drift_index=drift_index,
        coherence_surface=coherence_surface,
        recurrence_strength=recurrence_strength,
        evidence_coverage=evidence_coverage,
    )


# ── NonlocalGraphBuilder (ported) ─────────────────────────────────────────────

def _build_links(cards: list[_Card]) -> list[_NonlocalLink]:
    links: list[_NonlocalLink] = []
    for i, a in enumerate(cards):
        for b in cards[i + 1:]:
            shared = set(a.labels) & set(b.labels)
            if shared:
                w = min(1.0, 0.5 + 0.1 * len(shared))
                links.append(_NonlocalLink(a.card_id, b.card_id, w,
                                           f"shared-label:{','.join(sorted(shared))}"))
                continue
            if a.text and b.text and a.text[:32] == b.text[:32]:
                links.append(_NonlocalLink(a.card_id, b.card_id, 0.8, "shared-prefix"))
            elif (a.metrics.get("score", 0.0) > 2.5 and b.metrics.get("score", 0.0) > 2.5):
                links.append(_NonlocalLink(a.card_id, b.card_id, 0.35, "high-score-affinity"))
    return links


# ── Public API ────────────────────────────────────────────────────────────────

def score_with_noema(text: str, phase_metadata: dict[str, Any]) -> dict[str, Any]:
    """Full semantic scoring pipeline for a single text fragment.

    Returns:
        labels      list[str]  — semantic domain labels
        score       float      — composite memory score
        weights     dict       — 8 scoring components
        noema       dict       — 6 NOEMA observation metrics
        nonlocal_links  list   — (card_id, weight) pairs to buffer cards
    """
    phase = float(phase_metadata.get("target_phase", 0.0))
    semantic = _extract(text)
    card = _score_card(semantic, phase)

    # Build links against rolling buffer
    buffer_cards = list(_CARD_BUFFER)
    all_cards = buffer_cards + [card]
    links = _build_links(all_cards)
    noema = _observe(card, links)

    # Update rolling buffer
    _CARD_BUFFER.append(card)

    nonlocal_links = [
        (l.target_card_id if l.source_card_id == card.card_id else l.source_card_id, l.weight)
        for l in links
        if l.source_card_id == card.card_id or l.target_card_id == card.card_id
    ]

    # ── Object card enrichment (W_ij relations) ──────────────────────────────
    object_relations: dict[str, list] = {}
    try:
        import importlib.util as _ilu, sys as _sys
        from pathlib import Path as _Path
        _oc_path = _Path(__file__).parent / "object_cards.py"
        if "object_cards" not in _sys.modules:
            _spec = _ilu.spec_from_file_location("object_cards", _oc_path)
            _mod = _ilu.module_from_spec(_spec)
            _sys.modules["object_cards"] = _mod
            _spec.loader.exec_module(_mod)
        _oc = _sys.modules["object_cards"]
        _cards = _oc.get_cards()
        # Find matching concepts in text
        _words = set(re.findall(r'[a-ząćęłńóśźżA-ZĄĆĘŁŃÓŚŹŻ]{4,}', text.lower()))
        for _w in _words:
            if _w in _cards:
                _rel = _oc.related(_w, n=4, cards=_cards)
                _opp = _oc.opposites(_w, n=2, cards=_cards)
                if _rel or _opp:
                    object_relations[_w] = {
                        "phi": round(_cards[_w].phi_berry, 3),
                        "related": [(r[0], round(r[1], 3)) for r in _rel],
                        "opposites": [(r[0], round(r[1], 3)) for r in _opp],
                    }
    except Exception:
        pass

    # ── SentenceEquation stamp (grammar-as-physics pipeline) ─────────────────
    sentence_stamp: dict = {}
    try:
        import importlib.util as _ilu2, sys as _sys2
        from pathlib import Path as _Path2
        _oc_path2 = _Path2(__file__).parent / "object_cards.py"
        if "object_cards" not in _sys2.modules:
            _spec2 = _ilu2.spec_from_file_location("object_cards", _oc_path2)
            _mod2 = _ilu2.module_from_spec(_spec2)
            _sys2.modules["object_cards"] = _mod2
            _spec2.loader.exec_module(_mod2)
        _oc2 = _sys2.modules["object_cards"]
        _cards2 = _oc2.get_cards()
        sentence_stamp = _oc2.process_and_stamp(text, cards=_cards2)
        # inject phi_result into phase_metadata for downstream TSM write
        if sentence_stamp.get("phi_result") is not None:
            phase_metadata["phi_sentence"] = sentence_stamp["phi_result"]
            phase_metadata["sentence_op"]  = sentence_stamp["sentence_op"]
            phase_metadata["affect"]       = sentence_stamp["affect"]
            phase_metadata["closure_cost"] = sentence_stamp["closure_cost"]
    except Exception:
        pass

    return {
        "labels": card.labels,
        "score": round(card.metrics["score"], 4),
        "weights": {k: round(v, 4) for k, v in card.weights.items()},
        "noema": {
            "meaning_density":    round(noema.meaning_density, 4),
            "cluster_entropy":    round(noema.cluster_entropy, 4),
            "drift_index":        round(noema.drift_index, 4),
            "coherence_surface":  round(noema.coherence_surface, 4),
            "recurrence_strength": round(noema.recurrence_strength, 4),
            "evidence_coverage":  round(noema.evidence_coverage, 4),
        },
        "nonlocal_links": nonlocal_links,
        "card_id": card.card_id,
        "object_relations": object_relations,
        "sentence_eq": sentence_stamp,
    }


def build_nonlocal_index(cards: list[dict[str, Any]]) -> dict[str, list[tuple[str, float]]]:
    """Build adjacency index from TSM card dicts.

    cards: list of dicts with keys: memorise_id, D_sense, phi_berry
    Returns: {memorise_id: [(neighbor_id, weight), ...]}
    """
    # Convert TSM dicts to _Card stubs
    card_objs: list[_Card] = []
    id_map: dict[str, str] = {}  # card_id → memorise_id
    for c in cards:
        mid = c.get("memorise_id", "")
        text = c.get("D_sense", "") or ""
        phase = float(c.get("phi_berry", 0.0) or 0.0)
        sem = _extract(text)
        card = _score_card(sem, phase)
        # override card_id with TSM memorise_id for easy lookup
        card = _Card(card_id=mid, text=card.text, labels=card.labels,
                     weights=card.weights, metrics=card.metrics, phase=card.phase)
        card_objs.append(card)
        id_map[mid] = mid

    links = _build_links(card_objs)

    index: dict[str, list[tuple[str, float]]] = {}
    for lnk in links:
        index.setdefault(lnk.source_card_id, []).append((lnk.target_card_id, lnk.weight))
        index.setdefault(lnk.target_card_id, []).append((lnk.source_card_id, lnk.weight))

    return index
