"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Lightweight ethics guard — fast per-step coherence / fidelity check.

Source: ext1.EthicsGuard
"""

from __future__ import annotations


class EthicsGuard:
    """Hard-constraint guardian: raises on ethical breach if *block* is True."""

    def __init__(self, bound: float = 0.90, min_coh: float = 0.4, block: bool = True):
        self.ethical_bound = float(bound)
        self.min_coherence = float(min_coh)
        self.block = bool(block)

    def check_step(self, coherence: float, ethical_ok: bool, info_fidelity: float) -> None:
        if coherence < self.min_coherence or not ethical_ok:
            msg = (
                f"[EthicsGuard] breach: coherence={coherence:.3f} "
                f"ethical_ok={ethical_ok} fidelity={info_fidelity:.3f}"
            )
            if self.block:
                raise RuntimeError(msg)
            else:
                print("⚠", msg)


__all__ = ["EthicsGuard"]
