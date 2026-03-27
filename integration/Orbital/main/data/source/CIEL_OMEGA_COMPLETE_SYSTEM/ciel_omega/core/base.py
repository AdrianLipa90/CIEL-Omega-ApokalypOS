"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Base protocols and interfaces for CIEL kernels.

Source: ext1.KernelSpec
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

import numpy as np


class KernelSpec(Protocol):
    """Minimal interface for A/B kernel comparisons."""

    grid_size: int
    time_steps: int
    constants: Any

    def evolve_reality(self, steps: Optional[int] = None) -> Dict[str, List[float]]: ...
    def update_reality_fields(self) -> None: ...
    def normalize_field(self, field: np.ndarray) -> None: ...


__all__ = ["KernelSpec"]
