
"""Unified entrypoint for the merged CIEL/Ω canonical system."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import sys

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from .bridge.memory_core_phase_bridge import MemoryCorePhaseBridge

try:
    from .ciel_orchestrator import CIELOrchestrator  # type: ignore
except Exception:
    class CIELOrchestrator:
        def __init__(self, config: Optional[Dict[str, Any]] = None):
            self.config = config or {}


@dataclass
class UnifiedSystem:
    orchestrator: CIELOrchestrator
    bridge: MemoryCorePhaseBridge

    @classmethod
    def create(cls, config: Optional[Dict[str, Any]] = None, identity_phase: float = 0.0, grid_size: int = 24) -> "UnifiedSystem":
        orchestrator = CIELOrchestrator(config=config or {})
        bridge = MemoryCorePhaseBridge(identity_phase=identity_phase, grid_size=grid_size)
        return cls(orchestrator=orchestrator, bridge=bridge)

    def run_text_cycle(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        cycle = self.bridge.step(text, metadata=metadata or {})
        return {
            'input_text': cycle.input_text,
            'memory_semantic_key': cycle.memory_semantic_key,
            'memory_cycle_index': cycle.memory_cycle_index,
            'core_metrics': cycle.core_metrics,
            'vocabulary_metrics': cycle.vocabulary_metrics,
            'euler_metrics': cycle.euler_metrics,
        }
