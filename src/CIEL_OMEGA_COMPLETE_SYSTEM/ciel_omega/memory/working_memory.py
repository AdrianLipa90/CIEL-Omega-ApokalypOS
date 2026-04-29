"""CIEL/Ω Memory Architecture - M1 Working Memory

Conservative active operational field between perception and consolidation.
Working memory is short-lived, decays without reinforcement, and does not
write directly to IdentityField or M6.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict
from difflib import SequenceMatcher
import math
import re
from typing import Any, Dict, List, Optional

import numpy as np

from .base import BaseMemoryChannel, CHANNEL_PARAMS, IdentityField, PhaseState
from .working_types import WorkingTrace, WorkingItem, WorkingSnapshot


class WorkingMemory(BaseMemoryChannel):
    """M1 working memory.

    Short-term operational field with:
    - rapid reinforcement
    - exponential decay
    - lightweight retrieval
    - identity-weighted activation

    No direct mutation of IdentityField or M6.
    """

    TRACE_WINDOW = 128
    ACTIVE_THRESHOLD = 0.22
    EVICT_THRESHOLD = 0.05
    DECAY_RATE = 0.18  # per time unit
    REINFORCEMENT_WEIGHT = 0.55
    ALIGNMENT_WEIGHT = 0.25
    CONFIDENCE_WEIGHT = 0.20

    def __init__(self,
                 identity_field: IdentityField,
                 initial_state: Optional[PhaseState] = None):
        params = CHANNEL_PARAMS[1]  # M1
        super().__init__(params, initial_state)
        self.identity_field = identity_field
        self.traces: deque[WorkingTrace] = deque(maxlen=self.TRACE_WINDOW)
        self.items: Dict[str, WorkingItem] = {}
        self.observation_count = 0
        self._pending_consolidation: List[WorkingTrace] = []

    @staticmethod
    def normalize_text(text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _compute_identity_alignment(self, phase: float) -> tuple[float, float]:
        delta = ((phase - self.identity_field.phase + np.pi) % (2 * np.pi)) - np.pi
        alignment = 1.0 - min(abs(delta) / np.pi, 1.0)
        return float(alignment), float(delta)

    def _episode_id(self, source: Any) -> str:
        if hasattr(source, 'timestamp') and hasattr(source, 'content'):
            content = self.normalize_text(str(source.content))
            return f"src:{float(source.timestamp):.3f}:{content[:32]}"
        return f"src:{self.observation_count}"

    def compute_input_force(self, input_data: Any) -> float:
        if isinstance(input_data, dict):
            salience = float(np.clip(input_data.get('salience', 0.5), 0.0, 1.0))
            identity_alignment = float(np.clip(input_data.get('identity_alignment', 0.5), 0.0, 1.0))
            return 0.35 * salience + 0.65 * identity_alignment
        return 0.1

    def store(self, content: Any, metadata: Optional[Dict] = None) -> None:
        metadata = metadata or {}
        current_time = float(metadata.get('timestamp', self.observation_count))
        phase = float(metadata.get('phase', self.state.phase))
        salience = float(np.clip(metadata.get('salience', 0.7), 0.0, 1.0))
        confidence = float(np.clip(metadata.get('confidence', 0.7), 0.0, 1.0))
        normalized = self.normalize_text(str(content))
        alignment, phase_diff = self._compute_identity_alignment(phase)
        source_ids = metadata.get('source_ids') or [self._episode_id(metadata.get('source', content))]

        self.decay(current_time)

        activation_delta = (
            self.REINFORCEMENT_WEIGHT * salience +
            self.ALIGNMENT_WEIGHT * alignment +
            self.CONFIDENCE_WEIGHT * confidence
        )
        activation_delta = float(np.clip(activation_delta, 0.0, 1.0))

        trace = WorkingTrace(
            timestamp=current_time,
            source_ids=source_ids,
            working_key=normalized,
            content=str(content),
            phase=phase,
            phase_diff=phase_diff,
            identity_alignment=alignment,
            activation_delta=activation_delta,
            salience=salience,
            confidence=confidence,
        )
        # If deque is full, oldest trace will be dropped — consolidate instead of evicting
        if len(self.traces) == self.TRACE_WINDOW:
            oldest = self.traces[0]
            self._pending_consolidation.append(oldest)
            item = self.items.get(oldest.working_key)
            if item is not None and item.status not in ('evicted',):
                item.status = 'consolidated'
        self.traces.append(trace)
        self.observation_count += 1

        if normalized in self.items:
            item = self.items[normalized]
            item.activation = float(np.clip(item.activation + activation_delta * (1.0 - 0.3 * item.activation), 0.0, 1.5))
            item.confidence = float(np.clip(0.6 * item.confidence + 0.4 * confidence, 0.0, 1.0))
            item.identity_alignment = float(np.clip(0.6 * item.identity_alignment + 0.4 * alignment, 0.0, 1.0))
            item.phase = float(np.angle(np.exp(1j * item.phase) + np.exp(1j * phase)) % (2 * np.pi))
            item.reinforcement_count += 1
            item.last_observed_at = current_time
            item.last_accessed_at = current_time
            item.status = 'active' if item.activation >= self.ACTIVE_THRESHOLD else item.status
            if normalized not in item.aliases and str(content) != item.canonical_text:
                item.aliases.append(str(content))
        else:
            self.items[normalized] = WorkingItem(
                working_key=normalized,
                canonical_text=str(content),
                aliases=[],
                activation=float(np.clip(activation_delta, 0.0, 1.0)),
                confidence=confidence,
                identity_alignment=alignment,
                phase=phase,
                reinforcement_count=1,
                first_observed_at=current_time,
                last_observed_at=current_time,
                last_accessed_at=current_time,
                status='active' if activation_delta >= self.ACTIVE_THRESHOLD else 'decayed',
            )

    def observe(self, content: Any, current_time: float, phase: Optional[float] = None,
                salience: float = 0.7, confidence: float = 0.7,
                source_ids: Optional[List[str]] = None) -> WorkingTrace:
        before = len(self.traces)
        self.store(content, {
            'timestamp': current_time,
            'phase': self.state.phase if phase is None else phase,
            'salience': salience,
            'confidence': confidence,
            'source_ids': source_ids,
        })
        # deque(maxlen=TRACE_WINDOW) evicts oldest entry when full — size does not grow
        return self.traces[-1]

    def decay(self, current_time: float) -> None:
        for item in self.items.values():
            dt = max(0.0, current_time - item.last_observed_at)
            if dt <= 0:
                continue
            decayed = item.activation * math.exp(-self.DECAY_RATE * dt / self.params.tau)
            item.activation = float(decayed)
            if item.activation < self.EVICT_THRESHOLD:
                item.status = 'evicted'
            elif item.activation < self.ACTIVE_THRESHOLD:
                item.status = 'decayed'
            else:
                item.status = 'active'

    def reinforce(self, working_key: str, amount: float, current_time: float) -> bool:
        item = self.items.get(working_key)
        if item is None or item.status == 'evicted':
            return False
        # consolidated items can be reactivated
        if item.status == 'consolidated':
            item.status = 'active'
        self.decay(current_time)
        item.activation = float(np.clip(item.activation + amount, 0.0, 1.5))
        item.reinforcement_count += 1
        item.last_accessed_at = current_time
        item.last_observed_at = current_time
        item.status = 'active' if item.activation >= self.ACTIVE_THRESHOLD else item.status
        return True

    def retrieve(self, query: Any, top_k: int = 5, include_decayed: bool = False) -> List[Dict[str, Any]]:
        if not isinstance(query, str):
            return []
        q = self.normalize_text(query)
        results = []
        for item in self.items.values():
            if item.status == 'evicted':
                continue
            if not include_decayed and item.status not in ('active', 'consolidated'):
                continue
            key_match = SequenceMatcher(None, q, item.working_key).ratio()
            alias_match = max([SequenceMatcher(None, q, self.normalize_text(a)).ratio() for a in item.aliases], default=0.0)
            K = max(key_match, alias_match)
            score = 0.45 * K + 0.30 * min(item.activation, 1.0) + 0.15 * item.identity_alignment + 0.10 * item.confidence
            if item.status == 'decayed':
                score -= 0.10
            elif item.status == 'consolidated':
                score -= 0.05  # slight penalty vs active, but not forgotten
            results.append({'item': item, 'score': float(score)})
        results.sort(key=lambda r: r['score'], reverse=True)
        return results[:top_k]

    def active_items(self) -> List[WorkingItem]:
        return [item for item in self.items.values() if item.status == 'active']

    def snapshot(self, current_time: float) -> WorkingSnapshot:
        active = self.active_items()
        top_item = max(active, key=lambda x: x.activation, default=None)
        mean_alignment = float(np.mean([i.identity_alignment for i in active])) if active else 0.0
        return WorkingSnapshot(
            timestamp=current_time,
            active_keys=[i.working_key for i in active],
            total_items=len(self.items),
            top_item_key=top_item.working_key if top_item else None,
            top_activation=top_item.activation if top_item else 0.0,
            mean_identity_alignment=mean_alignment,
        )

    def retrieve_raw(self, query: Any) -> Any:
        return self.retrieve(query)

    def evict_decayed(self) -> int:
        to_delete = [k for k, v in self.items.items() if v.status == 'evicted']
        for k in to_delete:
            del self.items[k]
        return len(to_delete)
