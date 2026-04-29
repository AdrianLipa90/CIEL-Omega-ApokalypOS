from __future__ import annotations

from typing import Optional

from .config import CielConfig
from .ethics import EthicsGuard
from .interfaces import KernelSpec
from .reality_logger import RealityLogger
from .sigma import SoulInvariantOperator
from .gpu import GPUEngine


def _resolve_ethical_bound(constants) -> float:
    for name in ('ethical_bound', 'ETHICAL_BOUND', 'E_BOUND', 'life_threshold'):
        try:
            v = getattr(constants, name)
        except Exception:
            continue
        try:
            return float(v)
        except Exception:
            continue
    return 0.90


def attach_soul_invariant_hooks(kernel: KernelSpec) -> SoulInvariantOperator:
    return SoulInvariantOperator()


def attach_ethics_and_logging(kernel: KernelSpec, cfg: Optional[CielConfig] = None):
    cfg = cfg or CielConfig()
    guard = EthicsGuard(
        bound=_resolve_ethical_bound(getattr(kernel, 'constants', None)),
        min_coh=cfg.ethics_min_coherence,
        block=cfg.ethics_block_on_violation,
    )
    logger = RealityLogger(cfg.log_path)
    return guard, logger


def make_gpu_engine(cfg: Optional[CielConfig] = None) -> GPUEngine:
    cfg = cfg or CielConfig()
    return GPUEngine(enable_gpu=cfg.enable_gpu, enable_numba=cfg.enable_numba)
