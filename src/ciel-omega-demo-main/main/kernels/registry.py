from __future__ import annotations

from typing import Callable, Dict

from ..core.ciel_constants import CIELConstants
from ..core.config import CielConfig
from .factory import make_ciel0_kernel
from .unified_reality import UnifiedRealityKernel
from .ciel0_framework import CIEL0FrameworkKernel


KernelFactory = Callable[[CielConfig, int, CIELConstants, float], object]


def _wrap_ciel0(cfg: CielConfig, grid_size: int, constants: CIELConstants, length: float):
    return make_ciel0_kernel(cfg=cfg, grid_size=grid_size, constants=constants, length=length)


def _wrap_unified_reality(cfg: CielConfig, grid_size: int, constants: CIELConstants, length: float):
    return UnifiedRealityKernel(
        constants=constants,
        grid_size=grid_size,
        compute_mode=cfg.compute_mode,
        length=length,
    )


def _wrap_ciel0_framework(cfg: CielConfig, grid_size: int, constants: CIELConstants, length: float):
    return CIEL0FrameworkKernel(
        constants=constants,
        grid_size=grid_size,
        compute_mode=cfg.compute_mode,
        length=length,
    )


KERNELS: Dict[str, KernelFactory] = {
    'ciel0': _wrap_ciel0,
    'unified_reality': _wrap_unified_reality,
    'ciel0_framework': _wrap_ciel0_framework,
}
