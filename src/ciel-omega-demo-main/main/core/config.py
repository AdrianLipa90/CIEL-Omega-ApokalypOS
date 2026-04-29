from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from .compute_backend import ComputeMode


@dataclass
class CielConfig:
    enable_gpu: bool = True
    enable_numba: bool = True
    compute_mode: ComputeMode = 'fft'
    log_path: str = 'logs/reality.jsonl'
    ethics_min_coherence: float = 0.4
    ethics_block_on_violation: bool = True
    dataset_path: Optional[str] = None
