"""CIEL/Ω Memory Architecture - M4 Procedural Memory

Conservative procedural memory channel. Consolidates reusable procedures from
repeated successful episodes for the same goal while blocking contradictions.
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
from .procedural_types import (
    ProceduralTrace,
    ProceduralCandidate,
    ProceduralItem,
    ProceduralConsolidationScore,
)


class ProceduralMemory(BaseMemoryChannel):
    """M4 procedural memory.

    Stores reusable action patterns keyed by goal. Consolidation requires
    repeated successful traces, high identity alignment, and low contradiction.
    Does not mutate IdentityField or M6 directly.
    """

    TRACE_WINDOW_SIZE = 200
    DETECT_THRESHOLD = 0.60
    CONSOLIDATE_THRESHOLD = 0.78
    MIN_TRACE_SUPPORT = 3
    MIN_CONFIRMATIONS = 2
    MIN_MATURE_ALIGNMENT = 0.70
    MIN_MATURE_STABILITY = 0.78
    MIN_SUCCESS_RATE = 0.72
    MAX_CONTRADICTION = 0.20

    def __init__(self,
                 identity_field: IdentityField,
                 initial_state: Optional[PhaseState] = None):
        super().__init__(CHANNEL_PARAMS[4], initial_state)
        self.identity_field = identity_field
        self.traces: deque[ProceduralTrace] = deque(maxlen=self.TRACE_WINDOW_SIZE)
        self.candidates: Dict[str, ProceduralCandidate] = {}
        self.items: Dict[str, ProceduralItem] = {}
        self.observation_count = 0

    @staticmethod
    def _wrap(angle: float) -> float:
        return math.atan2(math.sin(angle), math.cos(angle))

    @classmethod
    def normalize_text(cls, text: str) -> str:
        text = str(text).lower().strip()
        text = re.sub(r"[.,;:!?()\[\]{}'\"-]", ' ', text)
        text = re.sub(r"\s+", ' ', text).strip()
        return text

    @classmethod
    def _extract_goal_action(cls, episode: Episode) -> Tuple[str, str]:
        ctx = episode.context or {}
        goal = ctx.get('goal') or ctx.get('task') or ctx.get('objective') or 'generic goal'
        action = ctx.get('action') or ctx.get('procedure') or episode.content
        return cls.normalize_text(goal), cls.normalize_text(action)

    @classmethod
    def _procedure_key(cls, goal_key: str, action_text: str) -> str:
        return f"{goal_key} -> {action_text}"

    @staticmethod
    def _episode_id(episode: Episode) -> str:
        return f"episode@{episode.timestamp:.3f}"

    def _compute_identity_alignment(self, phase: float) -> Tuple[float, float]:
        phase_diff = self._wrap(phase - self.identity_field.phase)
        alignment = 1.0 - abs(phase_diff) / math.pi
        return float(alignment), float(phase_diff)

    @staticmethod
    def _extract_success(result: Any, context: Dict[str, Any]) -> float:
        if isinstance(result, dict):
            if 'success' in result:
                return float(np.clip(1.0 if result['success'] else 0.0, 0.0, 1.0))
            if 'score' in result:
                return float(np.clip(result['score'], 0.0, 1.0))
        if 'success' in context:
            return float(np.clip(1.0 if context['success'] else 0.0, 0.0, 1.0))
        if isinstance(result, str):
            lowered = result.lower()
            if any(tok in lowered for tok in ('success', 'completed', 'resolved', 'passed')):
                return 0.9
            if any(tok in lowered for tok in ('failed', 'error', 'blocked', 'rejected')):
                return 0.1
        return 0.5

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    def compute_input_force(self, input_data: Any) -> float:
        # M4 should not take direct raw input in v1.
        return 0.0

    def observe_episode(self, episode: Episode) -> ProceduralTrace:
        goal_key, action_text = self._extract_goal_action(episode)
        procedure_key = self._procedure_key(goal_key, action_text)
        alignment, phase_diff = self._compute_identity_alignment(episode.phase_at_storage)
        confidence = float(np.clip(0.45 * episode.salience + 0.35 * episode.identity_impact + 0.20 * alignment, 0.0, 1.0))
        success = self._extract_success(episode.result, episode.context or {})
        contradiction = self._existing_contradiction_penalty(goal_key, action_text, success)
        novelty = 1.0 - min(1.0, len([t for t in self.traces if t.goal_key == goal_key and t.action_text == action_text]) / 5.0)

        trace = ProceduralTrace(
            timestamp=float(episode.timestamp),
            source_episode_ids=[self._episode_id(episode)],
            procedure_key=procedure_key,
            goal_key=goal_key,
            action_text=action_text,
            result_success=success,
            phase=episode.phase_at_storage,
            phase_diff=phase_diff,
            identity_alignment=alignment,
            confidence=confidence,
            contradiction_score=contradiction,
            novelty_score=novelty,
        )
        self.traces.append(trace)
        self.observation_count += 1
        return trace

    def _existing_contradiction_penalty(self, goal_key: str, action_text: str, success: float) -> float:
        penalties = []
        norm_action = self.normalize_text(action_text)
        for trace in self.traces:
            if trace.goal_key != goal_key:
                continue
            sim = self._similarity(norm_action, trace.action_text)
            if sim > 0.92:
                # same action; contradiction if outcomes disagree strongly
                if abs(trace.result_success - success) > 0.55:
                    penalties.append(0.8)
            else:
                # different procedure competing for same goal
                if max(success, trace.result_success) > 0.7:
                    penalties.append(0.55)
        for item in self.items.values():
            if item.goal_key != goal_key:
                continue
            sim = self._similarity(norm_action, item.canonical_action)
            if sim < 0.92:
                penalties.append(0.65 if item.success_rate > 0.72 and success > 0.72 else 0.35)
        return float(np.mean(penalties)) if penalties else 0.0

    def _traces_for_key(self, procedure_key: str) -> List[ProceduralTrace]:
        return [t for t in self.traces if t.procedure_key == procedure_key]

    def _goal_level_contradiction(self, procedure_key: str) -> float:
        traces = self._traces_for_key(procedure_key)
        if not traces:
            return 1.0
        goal_key = traces[-1].goal_key
        action_text = traces[-1].action_text
        own_success = float(np.mean([t.result_success for t in traces[-20:]]))
        penalties = []
        for trace in self.traces:
            if trace.goal_key != goal_key or trace.procedure_key == procedure_key:
                continue
            sim = self._similarity(action_text, trace.action_text)
            if sim < 0.92 and max(own_success, trace.result_success) > 0.7:
                penalties.append(0.75)
        for item in self.items.values():
            if item.goal_key != goal_key or item.procedure_key == procedure_key:
                continue
            sim = self._similarity(action_text, item.canonical_action)
            if sim < 0.92 and max(own_success, item.success_rate) > 0.7:
                penalties.append(0.80)
        return float(np.mean(penalties)) if penalties else 0.0

    def compute_consolidation_score(self, procedure_key: str) -> ProceduralConsolidationScore:
        traces = self._traces_for_key(procedure_key)
        if len(traces) < 2:
            return ProceduralConsolidationScore(0.0, 0.0, 0.0, 0.0, 0.0, 1.0)
        recent = traces[-20:]
        phase_diffs = np.array([t.phase_diff for t in recent], dtype=float)
        complex_mean = np.mean(np.exp(1j * phase_diffs)) if len(phase_diffs) else 0.0
        circular_concentration = abs(complex_mean) if len(phase_diffs) else 0.0
        mean_alignment = float(np.mean([t.identity_alignment for t in recent]))
        stability = 0.6 * circular_concentration + 0.4 * mean_alignment
        confidence = float(np.mean([t.confidence for t in recent]))
        repeated_support = min(1.0, len(traces) / self.MIN_TRACE_SUPPORT)
        success_rate = float(np.mean([t.result_success for t in recent]))
        contradiction = float(np.mean([t.contradiction_score for t in recent]))
        contradiction = max(contradiction, self._goal_level_contradiction(procedure_key))
        return ProceduralConsolidationScore(stability, mean_alignment, confidence, repeated_support, success_rate, contradiction)

    def check_candidate_creation(self, procedure_key: str) -> Optional[ProceduralCandidate]:
        traces = self._traces_for_key(procedure_key)
        if len(traces) < self.MIN_TRACE_SUPPORT:
            return None
        score = self.compute_consolidation_score(procedure_key)
        total = score.compute_total()
        if total < self.DETECT_THRESHOLD:
            return None
        canonical_action = max(traces, key=lambda t: (t.confidence, len(t.action_text))).action_text
        goal_key = traces[-1].goal_key
        aliases = sorted({t.action_text for t in traces})
        if procedure_key in self.candidates:
            cand = self.candidates[procedure_key]
            cand.trace_support_count = len(traces)
            cand.candidate_confirmation_count += 1
            cand.mean_identity_alignment = score.identity_alignment
            cand.mean_confidence = score.confidence
            cand.stability = score.stability
            cand.contradiction_score = score.contradiction
            cand.success_rate = score.success_rate
            cand.aliases = aliases
            if score.contradiction > self.MAX_CONTRADICTION:
                cand.status = 'blocked'
        else:
            cand = ProceduralCandidate(
                procedure_key=procedure_key,
                goal_key=goal_key,
                canonical_action=canonical_action,
                aliases=aliases,
                trace_support_count=len(traces),
                candidate_confirmation_count=1,
                mean_identity_alignment=score.identity_alignment,
                mean_confidence=score.confidence,
                stability=score.stability,
                contradiction_score=score.contradiction,
                success_rate=score.success_rate,
                status='blocked' if score.contradiction > self.MAX_CONTRADICTION else 'detected',
                consolidated=False,
            )
            self.candidates[procedure_key] = cand
        return cand

    def consolidate_candidate(self, procedure_key: str, current_time: float) -> Optional[ProceduralItem]:
        cand = self.candidates.get(procedure_key)
        if cand is None:
            return None
        total = self.compute_consolidation_score(procedure_key).compute_total()
        if total < self.CONSOLIDATE_THRESHOLD:
            return None
        if not cand.is_mature(
            min_confirmations=self.MIN_CONFIRMATIONS,
            min_alignment=self.MIN_MATURE_ALIGNMENT,
            min_stability=self.MIN_MATURE_STABILITY,
            min_success_rate=self.MIN_SUCCESS_RATE,
            max_contradiction=self.MAX_CONTRADICTION,
        ):
            return None
        traces = self._traces_for_key(procedure_key)
        item = ProceduralItem(
            procedure_key=procedure_key,
            goal_key=cand.goal_key,
            canonical_action=cand.canonical_action,
            aliases=list(cand.aliases),
            phase=float(np.angle(np.mean([np.exp(1j * t.phase) for t in traces[-20:]])) % (2 * np.pi)),
            confidence=cand.mean_confidence,
            stability=cand.stability,
            identity_alignment=cand.mean_identity_alignment,
            success_rate=cand.success_rate,
            provenance_episode_ids=sorted({eid for t in traces for eid in t.source_episode_ids}),
            created_at=current_time,
            updated_at=current_time,
            version=1,
            status='active',
        )
        self.items[procedure_key] = item
        cand.consolidated = True
        cand.status = 'mature'
        return item

    def retrieve(self, query: Any, identity_field: Optional[IdentityField] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        if not isinstance(query, str):
            return []
        q = self.normalize_text(query)
        field = identity_field or self.identity_field
        results = []
        for item in self.items.values():
            K = max(self._similarity(q, item.goal_key), self._similarity(q, item.canonical_action))
            phase_diff = self._wrap(item.phase - field.phase)
            A = 1.0 - abs(phase_diff) / math.pi
            X = 0.25 if item.status == 'contested' else 0.0
            score = 0.38 * K + 0.22 * A + 0.20 * item.confidence + 0.20 * item.success_rate - 0.20 * X
            results.append({'item': item, 'score': float(score)})
        results.sort(key=lambda r: r['score'], reverse=True)
        return results[:top_k]

    def snapshot(self) -> Dict[str, Any]:
        return {
            'channel': 'M4 Procedural Memory',
            'traces': len(self.traces),
            'candidates': len(self.candidates),
            'items': len(self.items),
            'active_items': [asdict(item) for item in self.items.values()],
        }

    def retrieve_raw(self, query: Any) -> Any:
        return self.retrieve(query, self.identity_field)

    def store(self, content: Any, metadata: Optional[Dict] = None) -> None:
        # Conservative: M4 only stores from Episode objects or compatible dicts.
        if isinstance(content, Episode):
            self.observe_episode(content)
        elif isinstance(content, dict):
            episodic = Episode(
                content=content.get('content', ''),
                context=content.get('context', {}),
                result=content.get('result'),
                timestamp=float((metadata or {}).get('timestamp', self.observation_count)),
                phase_at_storage=float((metadata or {}).get('phase', self.state.phase)),
                salience=float((metadata or {}).get('salience', 0.7)),
                identity_impact=float((metadata or {}).get('identity_impact', 0.7)),
            )
            self.observe_episode(episodic)
        else:
            raise TypeError('ProceduralMemory.store expects Episode or dict-compatible episode payload')
