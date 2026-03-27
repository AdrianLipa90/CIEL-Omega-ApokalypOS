from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

import numpy as np


class KernelSpec(Protocol):
    grid_size: int
    time_steps: int
    constants: Any

    def evolve_reality(self, steps: Optional[int] = None) -> Dict[str, List[float]]: ...

    def update_reality_fields(self) -> None: ...

    def normalize_field(self, field: np.ndarray) -> None: ...
