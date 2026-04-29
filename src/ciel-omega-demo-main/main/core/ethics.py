from __future__ import annotations


class EthicsGuard:
    def __init__(self, bound: float = 0.90, min_coh: float = 0.4, block: bool = True):
        self.ethical_bound = float(bound)
        self.min_coherence = float(min_coh)
        self.block = bool(block)

    def check_step(self, coherence: float, ethical_ok: bool, info_fidelity: float) -> None:
        if coherence < self.min_coherence or not ethical_ok:
            msg = (
                f'[EthicsGuard] breach: coherence={coherence:.3f} '
                f'ethical_ok={ethical_ok} fidelity={info_fidelity:.3f}'
            )
            if self.block:
                raise RuntimeError(msg)
            print(msg)
