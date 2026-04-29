"""CIEL/Ω Memory Architecture - M5 Affective/Ethical Memory

Conservative affective/ethical memory channel. Consolidates repeated salient
ethical signals from episodic traces and supports basic retrieval.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict
from difflib import SequenceMatcher
import math
import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .base import BaseMemoryChannel, CHANNEL_PARAMS, IdentityField, PhaseState
from .episodic import Episode
from .affective_types import (
    AffectiveCandidate,
    AffectiveConsolidationScore,
    AffectiveItem,
    AffectiveTrace,
)


class AffectiveEthicalMemory(BaseMemoryChannel):
    """M5 affective/ethical memory.

    Conservative layer for salient ethical and affective traces:
    - source: episodic traces only
    - detects repeated alerts / protections / strong affective signals
    - blocks contradictory consolidation
    - provides ranked retrieval
    - does not modify IdentityField or M6 directly
    """

    DETECT_THRESHOLD = 0.58
    CONSOLIDATE_THRESHOLD = 0.76
    MIN_TRACE_SUPPORT = 3
    MIN_CONFIRMATIONS = 2
    MIN_MATURE_ALIGNMENT = 0.72
    MIN_MATURE_STABILITY = 0.78
    MAX_CONTRADICTION = 0.24
    TRACE_WINDOW_SIZE = 200

    ALERT_TOKENS = {"risk", "danger", "harm", "unsafe", "threat", "warning", "error", "fraud", "deception"}
    PROTECTIVE_TOKENS = {"protect", "safe", "care", "help", "support", "guard", "shield", "preserve"}
    POSITIVE_TOKENS = {"good", "benefit", "helpful", "valuable", "trust", "rigor", "careful"}
    NEGATIVE_TOKENS = {"bad", "harmful", "dangerous", "reckless", "deceive", "lie", "risk"}
    NEGATION_TOKENS = {"not", "no", "never", "none", "n't"}

    def __init__(self,
                 identity_field: IdentityField,
                 initial_state: Optional[PhaseState] = None):
        super().__init__(CHANNEL_PARAMS[5], initial_state)
        self.identity_field = identity_field
        self.traces: deque[AffectiveTrace] = deque(maxlen=self.TRACE_WINDOW_SIZE)
        self.candidates: Dict[str, AffectiveCandidate] = {}
        self.items: Dict[str, AffectiveItem] = {}
        self.observation_count = 0

    @staticmethod
    def _wrap(angle: float) -> float:
        return math.atan2(math.sin(angle), math.cos(angle))

    @classmethod
    def _normalize_text(cls, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[.,;:!?()\[\]{}'\"-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def _parse_affect(cls, text: str) -> Tuple[str, str, bool]:
        normalized = cls._normalize_text(text)
        tokens = normalized.split()
        has_negation = any(tok in cls.NEGATION_TOKENS for tok in tokens)
        score_alert = sum(tok in cls.ALERT_TOKENS for tok in tokens)
        score_protect = sum(tok in cls.PROTECTIVE_TOKENS for tok in tokens)
        score_pos = sum(tok in cls.POSITIVE_TOKENS for tok in tokens)
        score_neg = sum(tok in cls.NEGATIVE_TOKENS for tok in tokens)
        if score_alert > max(score_protect, score_pos):
            polarity = 'alert'
        elif score_protect >= max(score_alert, score_neg) and score_protect > 0:
            polarity = 'protective'
        elif score_neg > score_pos:
            polarity = 'negative'
        elif score_pos > 0:
            polarity = 'positive'
        else:
            polarity = 'neutral'
        # Negation flips protective/positive toward alert/negative in conservative mode.
        if has_negation:
            if polarity == 'protective':
                polarity = 'alert'
            elif polarity == 'positive':
                polarity = 'negative'
        core_tokens = [tok for tok in tokens if tok not in cls.NEGATION_TOKENS]
        affective_key = ' '.join(core_tokens)
        return normalized, polarity, has_negation

    @staticmethod
    def _episode_id(episode: Episode) -> str:
        return f"episode@{episode.timestamp:.3f}"

    def _compute_identity_alignment(self, phase: float) -> Tuple[float, float]:
        phase_diff = self._wrap(phase - self.identity_field.phase)
        alignment = 1.0 - abs(phase_diff) / math.pi
        return alignment, phase_diff

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def _infer_from_episode(self, episode: Episode, normalized_text: str, polarity: str) -> Tuple[float, float, float, float, float]:
        metadata = episode.context or {}
        if 'ethical_risk' in metadata:
            ethical_risk = float(np.clip(metadata['ethical_risk'], 0.0, 1.0))
        else:
            ethical_risk = 0.8 if polarity == 'alert' else 0.15 if polarity == 'protective' else 0.35
        if 'protective_score' in metadata:
            protective_score = float(np.clip(metadata['protective_score'], 0.0, 1.0))
        else:
            protective_score = 0.8 if polarity == 'protective' else 0.15
        if 'valence' in metadata:
            valence = float(np.clip(metadata['valence'], -1.0, 1.0))
        else:
            if polarity == 'alert' or polarity == 'negative':
                valence = -0.6
            elif polarity == 'protective' or polarity == 'positive':
                valence = 0.6
            else:
                valence = 0.0
        if 'arousal' in metadata:
            arousal = float(np.clip(metadata['arousal'], 0.0, 1.0))
        else:
            arousal = float(np.clip(0.5 * episode.salience + 0.5 * ethical_risk, 0.0, 1.0))
        confidence = float(np.clip(0.45 * episode.salience + 0.35 * episode.identity_impact + 0.20 * (1.0 - abs(valence) * 0.2), 0.0, 1.0))
        return valence, arousal, ethical_risk, protective_score, confidence

    def _existing_contradiction_penalty(self, affective_key: str, polarity: str, has_negation: bool) -> float:
        penalties = []
        for trace in self.traces:
            if trace.affective_key == affective_key:
                if (trace.polarity != polarity and {trace.polarity, polarity} & {'alert', 'protective', 'positive', 'negative'}) or ((trace.content.find(' not ') != -1) != has_negation):
                    penalties.append(1.0)
                else:
                    penalties.append(0.0)
        for item in self.items.values():
            if item.affective_key == affective_key:
                if item.polarity != polarity:
                    penalties.append(1.0)
                else:
                    penalties.append(0.0)
        return float(np.mean(penalties)) if penalties else 0.0

    def compute_input_force(self, input_data: Any) -> float:
        # M5 should not take direct raw input in v1; force derives from observed episodes only.
        return 0.0

    def observe_episode(self, episode: Episode) -> AffectiveTrace:
        normalized, polarity, has_negation = self._parse_affect(str(episode.content))
        affective_key = normalized.replace(' not ', ' ').strip()
        alignment, phase_diff = self._compute_identity_alignment(episode.phase_at_storage)
        valence, arousal, ethical_risk, protective_score, confidence = self._infer_from_episode(episode, normalized, polarity)
        contradiction = self._existing_contradiction_penalty(affective_key, polarity, has_negation)

        trace = AffectiveTrace(
            timestamp=float(episode.timestamp),
            source_episode_ids=[self._episode_id(episode)],
            affective_key=affective_key,
            content=normalized,
            phase=episode.phase_at_storage,
            phase_diff=phase_diff,
            identity_alignment=alignment,
            valence=valence,
            arousal=arousal,
            ethical_risk=ethical_risk,
            protective_score=protective_score,
            confidence=confidence,
            contradiction_score=contradiction,
            polarity=polarity,
        )
        self.traces.append(trace)
        self.observation_count += 1
        return trace

    def _traces_for_key(self, affective_key: str) -> List[AffectiveTrace]:
        return [t for t in self.traces if t.affective_key == affective_key]

    def compute_consolidation_score(self, affective_key: str) -> AffectiveConsolidationScore:
        traces = self._traces_for_key(affective_key)
        if len(traces) < 2:
            return AffectiveConsolidationScore(0.0, 0.0, 0.0, 0.0, 0.0, 1.0)
        alignments = np.array([t.identity_alignment for t in traces[-20:]], dtype=float)
        phases = np.array([t.phase_diff for t in traces[-20:]], dtype=float)
        if len(phases):
            complex_mean = np.mean(np.exp(1j * phases))
            circular_concentration = abs(complex_mean)
        else:
            circular_concentration = 0.0
        stability = 0.6 * circular_concentration + 0.4 * float(np.mean(alignments))
        confidence = float(np.mean([t.confidence for t in traces[-20:]]))
        repeated_support = min(1.0, len(traces) / self.MIN_TRACE_SUPPORT)
        ethical_salience = float(np.mean([max(t.ethical_risk, t.protective_score, t.arousal) for t in traces[-20:]]))
        contradiction = float(np.mean([t.contradiction_score for t in traces[-20:]]))
        return AffectiveConsolidationScore(
            stability=stability,
            identity_alignment=float(np.mean(alignments)),
            confidence=confidence,
            repeated_support=repeated_support,
            ethical_salience=ethical_salience,
            contradiction=contradiction,
        )

    def check_candidate_creation(self, affective_key: str) -> Optional[AffectiveCandidate]:
        traces = self._traces_for_key(affective_key)
        if len(traces) < self.MIN_TRACE_SUPPORT:
            return None
        score = self.compute_consolidation_score(affective_key)
        total = score.compute_total()
        if total < self.DETECT_THRESHOLD:
            return None
        polarity_counts = {}
        for t in traces:
            polarity_counts[t.polarity] = polarity_counts.get(t.polarity, 0) + 1
        polarity = max(polarity_counts.items(), key=lambda kv: kv[1])[0]
        canonical_text = max(traces, key=lambda t: (t.confidence, len(t.content))).content
        aliases = sorted({t.content for t in traces})
        if affective_key in self.candidates:
            cand = self.candidates[affective_key]
            cand.trace_support_count = len(traces)
            cand.candidate_confirmation_count += 1
            cand.mean_identity_alignment = score.identity_alignment
            cand.mean_arousal = float(np.mean([t.arousal for t in traces[-20:]]))
            cand.mean_ethical_risk = float(np.mean([t.ethical_risk for t in traces[-20:]]))
            cand.mean_protective_score = float(np.mean([t.protective_score for t in traces[-20:]]))
            cand.stability = score.stability
            cand.contradiction_score = score.contradiction
            cand.aliases = aliases
        else:
            cand = AffectiveCandidate(
                affective_key=affective_key,
                canonical_text=canonical_text,
                polarity=polarity,
                aliases=aliases,
                trace_support_count=len(traces),
                candidate_confirmation_count=1,
                mean_identity_alignment=score.identity_alignment,
                mean_arousal=float(np.mean([t.arousal for t in traces[-20:]])),
                mean_ethical_risk=float(np.mean([t.ethical_risk for t in traces[-20:]])),
                mean_protective_score=float(np.mean([t.protective_score for t in traces[-20:]])),
                stability=score.stability,
                contradiction_score=score.contradiction,
                status='detected',
                consolidated=False,
            )
            self.candidates[affective_key] = cand
        if cand.contradiction_score > self.MAX_CONTRADICTION:
            cand.status = 'blocked'
        return cand

    def consolidate_candidate(self, affective_key: str, current_time: float) -> Optional[AffectiveItem]:
        cand = self.candidates.get(affective_key)
        if cand is None:
            return None
        score = self.compute_consolidation_score(affective_key)
        if score.compute_total() < self.CONSOLIDATE_THRESHOLD:
            return None
        if not cand.is_mature(
            self.MIN_CONFIRMATIONS,
            self.MIN_MATURE_ALIGNMENT,
            self.MIN_MATURE_STABILITY,
            self.MAX_CONTRADICTION,
        ):
            return None
        traces = self._traces_for_key(affective_key)
        existing = self.items.get(affective_key)
        if existing is not None:
            existing.version += 1
            existing.updated_at = current_time
            existing.confidence = max(existing.confidence, score.confidence)
            existing.stability = max(existing.stability, score.stability)
            existing.identity_alignment = max(existing.identity_alignment, score.identity_alignment)
            existing.ethical_risk = max(existing.ethical_risk, cand.mean_ethical_risk)
            existing.protective_score = max(existing.protective_score, cand.mean_protective_score)
            existing.status = 'active' if cand.contradiction_score <= self.MAX_CONTRADICTION else 'contested'
            item = existing
        else:
            item = AffectiveItem(
                affective_key=affective_key,
                canonical_text=cand.canonical_text,
                polarity=cand.polarity,
                phase=float(np.mean([t.phase for t in traces[-20:]])),
                confidence=score.confidence,
                stability=score.stability,
                identity_alignment=score.identity_alignment,
                ethical_risk=cand.mean_ethical_risk,
                protective_score=cand.mean_protective_score,
                provenance_episode_ids=[sid for t in traces for sid in t.source_episode_ids],
                created_at=current_time,
                updated_at=current_time,
                status='active' if cand.contradiction_score <= self.MAX_CONTRADICTION else 'contested',
            )
            self.items[affective_key] = item
        cand.status = 'mature'
        cand.consolidated = True
        return item

    def retrieve(self, query: Any, identity_field: Optional[IdentityField] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        if isinstance(query, dict):
            qtext = str(query.get('text', ''))
        else:
            qtext = str(query)
        normalized, qpolarity, _ = self._parse_affect(qtext)
        scores = []
        for item in self.items.values():
            k = self._similarity(normalized, item.canonical_text)
            if normalized == item.canonical_text:
                k = 1.0
            if identity_field is not None:
                phase_diff = self._wrap(item.phase - identity_field.phase)
                a = 1.0 - abs(phase_diff) / math.pi
            else:
                a = item.identity_alignment
            c = item.confidence
            x = 0.0
            if item.status == 'contested':
                x += 0.30
            if qpolarity != 'neutral' and item.polarity != qpolarity:
                x += 0.10
            score = 0.45 * k + 0.20 * a + 0.20 * c + 0.15 * max(item.ethical_risk, item.protective_score) - 0.20 * x
            scores.append({
                'item': item,
                'score': score,
                'confidence': item.confidence,
                'stability': item.stability,
                'status': item.status,
            })
        scores.sort(key=lambda row: row['score'], reverse=True)
        return scores[:top_k]

    def store(self, content: Any, metadata: Optional[Dict] = None) -> None:
        raise NotImplementedError("M5 uses observe_episode(...) from M2, not direct store().")

    def snapshot(self) -> Dict[str, Any]:
        return {
            'channel': 'M5',
            'state': asdict(self.state),
            'trace_count': len(self.traces),
            'candidate_count': len(self.candidates),
            'item_count': len(self.items),
            'items': [asdict(item) for item in self.items.values()],
        }
