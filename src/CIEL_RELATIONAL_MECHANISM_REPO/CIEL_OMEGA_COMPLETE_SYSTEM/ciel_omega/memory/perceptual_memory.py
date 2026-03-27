"""CIEL/Ω Memory Architecture - M0 Perceptual Memory

Conservative perceptual ingress buffer. M0 is a fast first-order channel with
strong decay, high plasticity, and no direct write path into IdentityField or M6.
It stores raw percepts transiently and supports salience-ranked retrieval.
"""

from __future__ import annotations

from collections import deque
from difflib import SequenceMatcher
import math
import re
from typing import Any, Dict, List, Optional

import numpy as np

from .base import BaseMemoryChannel, CHANNEL_PARAMS, IdentityField, PhaseState
from .perceptual_types import PerceptualItem, PerceptualSnapshot, PerceptualTrace


class PerceptualMemory(BaseMemoryChannel):
    """M0 perceptual memory.

    Fast ingress channel with:
    - raw percept traces
    - strong exponential decay
    - duplicate merging by modality + normalized surface
    - salience / confidence ranked retrieval

    It may read IdentityField for alignment scoring, but never mutates it.
    """

    TRACE_WINDOW = 256
    ACTIVE_THRESHOLD = 0.18
    EVICT_THRESHOLD = 0.03
    DECAY_RATE = 0.60  # strong decay per time unit
    SALIENCE_WEIGHT = 0.50
    ALIGNMENT_WEIGHT = 0.15
    CONFIDENCE_WEIGHT = 0.20
    NOVELTY_WEIGHT = 0.15

    def __init__(self,
                 identity_field: IdentityField,
                 initial_state: Optional[PhaseState] = None):
        params = CHANNEL_PARAMS[0]  # M0
        super().__init__(params, initial_state)
        self.identity_field = identity_field
        self.traces: deque[PerceptualTrace] = deque(maxlen=self.TRACE_WINDOW)
        self.items: Dict[str, PerceptualItem] = {}
        self.observation_count = 0

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

    def _infer_novelty(self, percept_key: str) -> float:
        if percept_key not in self.items:
            return 1.0
        count = self.items[percept_key].exposure_count
        return float(1.0 / (1.0 + 0.35 * count))

    def _source_id(self, content: Any, current_time: float) -> str:
        normalized = self.normalize_text(str(content))
        return f"perc:{current_time:.3f}:{normalized[:32]}"

    def compute_input_force(self, input_data: Any) -> float:
        if isinstance(input_data, dict):
            salience = float(np.clip(input_data.get('salience', 0.5), 0.0, 1.0))
            confidence = float(np.clip(input_data.get('confidence', 0.5), 0.0, 1.0))
            novelty = float(np.clip(input_data.get('novelty', 0.5), 0.0, 1.0))
            return 0.55 * salience + 0.20 * confidence + 0.25 * novelty
        return 0.1

    def store(self, content: Any, metadata: Optional[Dict] = None) -> None:
        metadata = metadata or {}
        current_time = float(metadata.get('timestamp', self.observation_count))
        modality = str(metadata.get('modality', 'text')).strip().lower() or 'text'
        phase = float(metadata.get('phase', self.state.phase))
        salience = float(np.clip(metadata.get('salience', 0.7), 0.0, 1.0))
        confidence = float(np.clip(metadata.get('confidence', 0.7), 0.0, 1.0))
        raw_text = str(content)
        normalized = self.normalize_text(raw_text)
        percept_key = f"{modality}:{normalized}"
        alignment, phase_diff = self._compute_identity_alignment(phase)
        novelty = self._infer_novelty(percept_key)

        self.decay(current_time)

        activation_delta = (
            self.SALIENCE_WEIGHT * salience +
            self.ALIGNMENT_WEIGHT * alignment +
            self.CONFIDENCE_WEIGHT * confidence +
            self.NOVELTY_WEIGHT * novelty
        )
        activation_delta = float(np.clip(activation_delta, 0.0, 1.2))

        trace = PerceptualTrace(
            timestamp=current_time,
            source_id=metadata.get('source_id', self._source_id(raw_text, current_time)),
            percept_key=percept_key,
            modality=modality,
            raw_content=raw_text,
            normalized_content=normalized,
            phase=phase,
            phase_diff=phase_diff,
            identity_alignment=alignment,
            salience=salience,
            confidence=confidence,
            novelty_score=novelty,
        )
        self.traces.append(trace)
        self.observation_count += 1

        if percept_key in self.items:
            item = self.items[percept_key]
            item.activation = float(np.clip(item.activation + activation_delta * (1.0 - 0.25 * min(item.activation, 1.0)), 0.0, 1.6))
            item.salience = float(np.clip(0.55 * item.salience + 0.45 * salience, 0.0, 1.0))
            item.confidence = float(np.clip(0.55 * item.confidence + 0.45 * confidence, 0.0, 1.0))
            item.identity_alignment = float(np.clip(0.65 * item.identity_alignment + 0.35 * alignment, 0.0, 1.0))
            item.phase = float(np.angle(np.exp(1j * item.phase) + np.exp(1j * phase)) % (2 * np.pi))
            item.exposure_count += 1
            item.last_observed_at = current_time
            item.status = 'active' if item.activation >= self.ACTIVE_THRESHOLD else item.status
            if raw_text != item.canonical_text and raw_text not in item.aliases:
                item.aliases.append(raw_text)
        else:
            self.items[percept_key] = PerceptualItem(
                percept_key=percept_key,
                modality=modality,
                canonical_text=raw_text,
                aliases=[],
                activation=float(np.clip(activation_delta, 0.0, 1.0)),
                salience=salience,
                confidence=confidence,
                identity_alignment=alignment,
                phase=phase,
                exposure_count=1,
                first_observed_at=current_time,
                last_observed_at=current_time,
                status='active' if activation_delta >= self.ACTIVE_THRESHOLD else 'decayed',
            )

    def observe(self, content: Any, current_time: float, *, modality: str = 'text',
                phase: Optional[float] = None, salience: float = 0.7,
                confidence: float = 0.7, source_id: Optional[str] = None) -> PerceptualTrace:
        before = len(self.traces)
        self.store(content, {
            'timestamp': current_time,
            'modality': modality,
            'phase': self.state.phase if phase is None else phase,
            'salience': salience,
            'confidence': confidence,
            'source_id': source_id,
        })
        assert len(self.traces) == before + 1
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

    def retrieve(self, query: Any, top_k: int = 5, include_decayed: bool = False) -> List[Dict[str, Any]]:
        if not isinstance(query, str):
            return []
        q = self.normalize_text(query)
        results = []
        for item in self.items.values():
            if item.status == 'evicted':
                continue
            if not include_decayed and item.status != 'active':
                continue
            key_match = SequenceMatcher(None, q, item.percept_key.split(':', 1)[1]).ratio()
            alias_match = max([SequenceMatcher(None, q, self.normalize_text(a)).ratio() for a in item.aliases], default=0.0)
            K = max(key_match, alias_match)
            score = 0.35 * K + 0.35 * min(item.activation, 1.0) + 0.20 * item.salience + 0.10 * item.confidence
            if item.status == 'decayed':
                score -= 0.12
            results.append({'item': item, 'score': float(score)})
        results.sort(key=lambda r: r['score'], reverse=True)
        return results[:top_k]

    def active_items(self) -> List[PerceptualItem]:
        return [item for item in self.items.values() if item.status == 'active']

    def snapshot(self, current_time: float) -> PerceptualSnapshot:
        active = self.active_items()
        dominant = max(active, key=lambda x: x.activation, default=None)
        mean_salience = float(np.mean([i.salience for i in active])) if active else 0.0
        return PerceptualSnapshot(
            timestamp=current_time,
            active_keys=[i.percept_key for i in active],
            total_items=len(self.items),
            dominant_key=dominant.percept_key if dominant else None,
            dominant_activation=dominant.activation if dominant else 0.0,
            mean_salience=mean_salience,
        )

    def evict_decayed(self) -> int:
        to_delete = [k for k, v in self.items.items() if v.status == 'evicted']
        for k in to_delete:
            del self.items[k]
        return len(to_delete)
