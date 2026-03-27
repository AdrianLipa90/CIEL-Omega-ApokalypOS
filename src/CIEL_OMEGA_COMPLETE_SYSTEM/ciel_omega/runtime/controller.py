"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Real-time simulation controller (threaded step loop).

Source: ext7.RealTimeController
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional


@dataclass
class RealTimeController:
    """Run a step function in a background thread at fixed intervals."""

    step_fn: Callable[[], Dict[str, float]]
    on_step: Optional[Callable[[int, Dict[str, float]], None]] = None
    interval: float = 0.1
    steps: int = 100
    _running: bool = field(default=False, init=False)
    _thread: Optional[threading.Thread] = field(default=None, init=False)

    def _loop(self):
        for i in range(self.steps):
            if not self._running:
                break
            data = self.step_fn()
            if self.on_step:
                self.on_step(i, data)
            time.sleep(self.interval)
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)


__all__ = ["RealTimeController"]
