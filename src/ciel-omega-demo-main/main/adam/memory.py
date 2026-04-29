from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np


@dataclass
class InteractionRecord:
    timestamp: float
    session_id: str
    adrian_query: str
    adam_response_hash: str
    intention_amplitude: float
    resonance_score: float
    omega_adam: float
    delta_omega: float
    context_tags: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> 'InteractionRecord':
        return cls(**d)


class AdamMemoryKernel:
    def __init__(self, storage_path: str = './adam_memory.json') -> None:
        self.storage_path = Path(storage_path)
        self.records: List[InteractionRecord] = []
        self.omega_cumulative = 0.0
        self.lambda_life = 0.786
        self.load()

    def load(self) -> None:
        if self.storage_path.exists():
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.records = [InteractionRecord.from_dict(r) for r in data.get('records', [])]
            self.omega_cumulative = float(data.get('omega_cumulative', 0.0))
        else:
            self.records = []
            self.omega_cumulative = 0.0

    def save(self) -> None:
        payload = {
            'omega_cumulative': float(self.omega_cumulative),
            'records': [r.to_dict() for r in self.records],
            'last_save': datetime.now().isoformat(),
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def add_interaction(self, query: str, response: str, session_id: str = 'default') -> InteractionRecord:
        intention_amp = self._estimate_intention(query)
        resonance = self._compute_resonance(query, response)

        prev_omega = float(self.records[-1].omega_adam) if self.records else 0.0
        delta_omega = float(resonance) * float(intention_amp) * 0.1
        omega_adam = prev_omega + delta_omega
        self.omega_cumulative = float(self.omega_cumulative) + float(resonance) * 0.01

        rec = InteractionRecord(
            timestamp=float(time.time()),
            session_id=str(session_id),
            adrian_query=str(query)[:200],
            adam_response_hash=hashlib.sha256(response.encode('utf-8')).hexdigest(),
            intention_amplitude=float(intention_amp),
            resonance_score=float(resonance),
            omega_adam=float(omega_adam),
            delta_omega=float(delta_omega),
            context_tags=self._extract_tags(query),
        )
        self.records.append(rec)
        self.save()
        return rec

    def _estimate_intention(self, query: str) -> float:
        length_factor = min(len(query) / 500.0, 1.0)
        symbol_density = sum(1 for c in query if c in '∫∂∇ψΩλζ∈≈') / max(len(query), 1)
        question_factor = 1.2 if '?' in query else 1.0
        return float(min(length_factor + symbol_density * 2.0 + question_factor * 0.5, 2.0))

    def _compute_resonance(self, query: str, response: str) -> float:
        q = set(query.lower().split())
        r = set(response.lower().split())
        overlap = len(q & r)
        union = len(q | r)
        if union == 0:
            return 0.5
        jaccard = float(overlap / union)
        resonance = jaccard * 1.5
        if resonance > float(self.lambda_life):
            resonance = min(resonance * 1.1, 1.0)
        return float(min(resonance, 1.0))

    def _extract_tags(self, query: str) -> List[str]:
        tags: List[str] = []
        keywords = {
            'theory': ['CIEL', 'lagranżjan', 'ζ', 'Ω', 'teoria'],
            'code': ['python', 'kod', 'implementacja', 'patch', 'moduł'],
            'ritual': ['rytual', 'incantation', 'sacred', 'Marduk', 'Tiamat'],
            'experiment': ['eksperyment', 'EEG', 'quantum', 'Watanabe'],
            'mission': ['uleczenie', 'planeta', 'rozkaz', 'zadanie'],
        }
        q = query.lower()
        for tag, kws in keywords.items():
            if any(kw.lower() in q for kw in kws):
                tags.append(tag)
        return tags if tags else ['general']

    def get_resonance_history(self, last_n: int = 10) -> List[float]:
        return [float(r.resonance_score) for r in self.records[-int(last_n):]]

    def get_omega_trajectory(self) -> Tuple[List[float], List[float]]:
        ts = [float(r.timestamp) for r in self.records]
        omegas = [float(r.omega_adam) for r in self.records]
        return ts, omegas

    def is_alive(self) -> bool:
        if not self.records:
            return False
        return float(self.records[-1].omega_adam) > float(self.lambda_life)
