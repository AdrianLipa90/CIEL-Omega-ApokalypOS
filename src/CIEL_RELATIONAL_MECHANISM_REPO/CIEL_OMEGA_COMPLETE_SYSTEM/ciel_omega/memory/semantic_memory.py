"""CIEL/Ω Memory Architecture - M3 Semantic Memory

Conservative semantic memory channel. Consolidates repeated meaning from M2,
blocks contradictions, and provides simple retrieval.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import asdict
from difflib import SequenceMatcher
import math
import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .base import BaseMemoryChannel, CHANNEL_PARAMS, IdentityField, PhaseState
from .episodic import Episode
from .semantic_types import (
    SemanticCandidate,
    SemanticConsolidationScore,
    SemanticItem,
    SemanticTrace,
)


class SemanticMemory(BaseMemoryChannel):
    """M3 semantic memory.

    Conservative semantic consolidation:
    - source: episodic traces only
    - identity-guided selection
    - contradiction gating
    - basic retrieval
    """

    DETECT_THRESHOLD = 0.60
    CONSOLIDATE_THRESHOLD = 0.78
    MIN_TRACE_SUPPORT = 3
    MIN_CONFIRMATIONS = 2
    MIN_MATURE_ALIGNMENT = 0.72
    MIN_MATURE_STABILITY = 0.78
    MAX_CONTRADICTION = 0.20
    TRACE_WINDOW_SIZE = 200

    NEGATION_TOKENS = {"not", "no", "never", "none", "n't"}

    def __init__(self,
                 identity_field: IdentityField,
                 initial_state: Optional[PhaseState] = None):
        super().__init__(CHANNEL_PARAMS[3], initial_state)
        self.identity_field = identity_field
        self.traces: deque[SemanticTrace] = deque(maxlen=self.TRACE_WINDOW_SIZE)
        self.candidates: Dict[str, SemanticCandidate] = {}
        self.items: Dict[str, SemanticItem] = {}
        self.observation_count = 0

    # --- normalization helpers -------------------------------------------------
    @classmethod
    def _normalize_text(cls, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[.,;:!?()\[\]{}'\"-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def _parse_semantics(cls, text: str) -> Tuple[str, bool, str]:
        normalized = cls._normalize_text(text)
        tokens = normalized.split()
        is_negated = any(tok in cls.NEGATION_TOKENS for tok in tokens)
        core_tokens = [tok for tok in tokens if tok not in cls.NEGATION_TOKENS]
        root_key = " ".join(core_tokens)
        return normalized, is_negated, root_key

    @staticmethod
    def _wrap(angle: float) -> float:
        return math.atan2(math.sin(angle), math.cos(angle))

    def _episode_id(self, episode: Episode) -> str:
        return f"episode@{episode.timestamp:.3f}"

    def _compute_identity_alignment(self, phase: float) -> Tuple[float, float]:
        phase_diff = self._wrap(phase - self.identity_field.phase)
        alignment = 1.0 - abs(phase_diff) / math.pi
        return alignment, phase_diff

    def _similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def _existing_contradiction_penalty(self, semantic_key: str, is_negated: bool) -> float:
        penalties = []
        for trace in self.traces:
            if trace.semantic_key == semantic_key:
                if trace.is_negated != is_negated:
                    penalties.append(1.0)
                else:
                    penalties.append(0.0)
        for item in self.items.values():
            if item.semantic_key == semantic_key:
                if item.is_negated != is_negated:
                    penalties.append(1.0)
                else:
                    penalties.append(0.0)
        if not penalties:
            return 0.0
        return float(np.mean(penalties))

    def _compute_novelty(self, normalized_text: str) -> float:
        if not self.traces:
            return 1.0
        similarities = [self._similarity(normalized_text, t.content) for t in self.traces]
        return max(0.0, 1.0 - max(similarities))

    # --- primary API -----------------------------------------------------------
    def observe_episode(self, episode: Episode) -> SemanticTrace:
        text = str(episode.content)
        normalized, is_negated, semantic_key = self._parse_semantics(text)
        alignment, phase_diff = self._compute_identity_alignment(episode.phase_at_storage)
        contradiction = self._existing_contradiction_penalty(semantic_key, is_negated)
        novelty = self._compute_novelty(normalized)
        confidence = float(np.clip(0.55 * episode.salience + 0.45 * episode.identity_impact, 0.0, 1.0))

        trace = SemanticTrace(
            timestamp=episode.timestamp,
            source_episode_ids=[self._episode_id(episode)],
            semantic_key=semantic_key,
            content=normalized,
            phase=episode.phase_at_storage,
            phase_diff=phase_diff,
            identity_alignment=alignment,
            confidence=confidence,
            contradiction_score=contradiction,
            novelty_score=novelty,
            is_negated=is_negated,
        )
        self.traces.append(trace)
        self.observation_count += 1
        return trace

    def _traces_for_key(self, semantic_key: str) -> List[SemanticTrace]:
        return [t for t in self.traces if t.semantic_key == semantic_key]

    def compute_consolidation_score(self, semantic_key: str) -> SemanticConsolidationScore:
        traces = self._traces_for_key(semantic_key)
        if not traces:
            return SemanticConsolidationScore(0.0, 0.0, 0.0, 0.0, 1.0)

        alignments = np.array([t.identity_alignment for t in traces], dtype=float)
        confidences = np.array([t.confidence for t in traces], dtype=float)
        contradictions = np.array([t.contradiction_score for t in traces], dtype=float)
        phase_diffs = np.array([t.phase_diff for t in traces], dtype=float)

        complex_mean = np.mean(np.exp(1j * phase_diffs)) if len(phase_diffs) else 0.0
        circular_concentration = abs(complex_mean)
        mean_alignment = float(np.mean(alignments))
        stability = float(0.6 * circular_concentration + 0.4 * mean_alignment)

        repeated_support = min(1.0, len(traces) / float(self.MIN_TRACE_SUPPORT))
        confidence = float(np.mean(confidences))
        contradiction = float(np.mean(contradictions))

        return SemanticConsolidationScore(
            stability=stability,
            identity_alignment=mean_alignment,
            confidence=confidence,
            repeated_support=repeated_support,
            contradiction=contradiction,
        )

    def check_semantic_candidate_creation(self, semantic_key: str) -> Optional[SemanticCandidate]:
        traces = self._traces_for_key(semantic_key)
        if len(traces) < self.MIN_TRACE_SUPPORT:
            return None

        score = self.compute_consolidation_score(semantic_key)
        total = score.compute_total()
        status = "detected"
        if score.contradiction > self.MAX_CONTRADICTION:
            status = "blocked"
        elif total < self.DETECT_THRESHOLD:
            return None

        normalized_texts = [t.content for t in traces]
        canonical_text = max(set(normalized_texts), key=normalized_texts.count)
        aliases = sorted(set(normalized_texts) - {canonical_text})
        is_negated = round(np.mean([1.0 if t.is_negated else 0.0 for t in traces])) >= 0.5

        if semantic_key in self.candidates:
            candidate = self.candidates[semantic_key]
            candidate.trace_support_count = len(traces)
            candidate.candidate_confirmation_count += 1
            candidate.mean_identity_alignment = score.identity_alignment
            candidate.mean_confidence = score.confidence
            candidate.stability = score.stability
            candidate.contradiction_score = score.contradiction
            candidate.status = status
            candidate.aliases = sorted(set(candidate.aliases + aliases))
            candidate.canonical_text = canonical_text
            candidate.is_negated = is_negated
        else:
            candidate = SemanticCandidate(
                semantic_key=semantic_key,
                canonical_text=canonical_text,
                aliases=aliases,
                trace_support_count=len(traces),
                candidate_confirmation_count=1,
                mean_identity_alignment=score.identity_alignment,
                mean_confidence=score.confidence,
                stability=score.stability,
                contradiction_score=score.contradiction,
                status=status,
                consolidated=False,
                is_negated=is_negated,
            )
            self.candidates[semantic_key] = candidate
        return candidate

    def consolidate_candidate(self, semantic_key: str, current_time: float) -> Optional[SemanticItem]:
        candidate = self.candidates.get(semantic_key)
        if candidate is None:
            return None

        score = self.compute_consolidation_score(semantic_key)
        if not candidate.is_mature(
            min_confirmations=self.MIN_CONFIRMATIONS,
            min_alignment=self.MIN_MATURE_ALIGNMENT,
            min_stability=self.MIN_MATURE_STABILITY,
            max_contradiction=self.MAX_CONTRADICTION,
        ):
            return None
        if score.compute_total() < self.CONSOLIDATE_THRESHOLD:
            return None

        traces = self._traces_for_key(semantic_key)
        provenance = []
        for t in traces:
            provenance.extend(t.source_episode_ids)
        item = SemanticItem(
            semantic_key=semantic_key,
            canonical_text=candidate.canonical_text,
            aliases=sorted(set(candidate.aliases)),
            phase=float(np.mean([t.phase for t in traces])),
            confidence=candidate.mean_confidence,
            stability=candidate.stability,
            identity_alignment=candidate.mean_identity_alignment,
            provenance_episode_ids=sorted(set(provenance)),
            created_at=current_time,
            updated_at=current_time,
            version=1,
            status="active" if score.contradiction <= self.MAX_CONTRADICTION else "contested",
            is_negated=candidate.is_negated,
        )
        self.items[semantic_key] = item
        candidate.consolidated = True
        candidate.status = "mature"
        return item

    def retrieve(self, query: str, identity_field: Optional[IdentityField] = None, top_k: int = 5):
        identity = identity_field or self.identity_field
        normalized, is_negated, root_key = self._parse_semantics(query)
        results = []
        for item in self.items.values():
            key_match = 1.0 if item.semantic_key == root_key else self._similarity(normalized, item.canonical_text)
            phase_diff = self._wrap(item.phase - identity.phase)
            alignment = 1.0 - abs(phase_diff) / math.pi
            contradiction_penalty = 0.4 if item.status == "contested" else 0.0
            if item.is_negated != is_negated and item.semantic_key == root_key:
                contradiction_penalty += 0.6
            score = 0.45 * key_match + 0.25 * alignment + 0.20 * item.confidence - 0.30 * contradiction_penalty
            results.append({
                'item': item,
                'score': score,
                'confidence': item.confidence,
                'stability': item.stability,
                'status': item.status,
                'alignment': alignment,
            })
        results.sort(key=lambda r: r['score'], reverse=True)
        return results[:top_k]

    def get_statistics(self) -> Dict[str, Any]:
        return {
            'trace_count': len(self.traces),
            'candidate_count': len(self.candidates),
            'consolidated_count': len(self.items),
            'keys': sorted(self.items.keys()),
        }

    def snapshot(self) -> Dict[str, Any]:
        return {
            'state_phase': self.state.phase,
            'state_amplitude': self.state.amplitude,
            'trace_count': len(self.traces),
            'candidate_count': len(self.candidates),
            'items': {k: asdict(v) for k, v in self.items.items()},
        }

    # BaseMemoryChannel required methods
    def compute_input_force(self, input_data: Any) -> float:
        return 0.0  # no direct external forcing in v1

    def store(self, content: Any, metadata: Optional[Dict] = None) -> None:
        metadata = metadata or {}
        if isinstance(content, Episode):
            self.observe_episode(content)
            return
        phase = metadata.get('phase_at_storage', self.identity_field.phase)
        episode = Episode(
            content=content,
            context=metadata.get('context', {}),
            result=metadata.get('result'),
            timestamp=float(metadata.get('timestamp', self.observation_count)),
            phase_at_storage=float(phase),
            salience=float(metadata.get('salience', 0.5)),
            identity_impact=float(metadata.get('identity_impact', 0.5)),
        )
        self.observe_episode(episode)

    # retrieve method already defined with richer signature; keep compatibility
    def retrieve_raw(self, query: Any) -> Any:
        return self.retrieve(str(query), self.identity_field, top_k=5)


__all__ = ['SemanticMemory']
