from __future__ import annotations

from ..core.ciel_constants import CIELConstants, DEFAULT_CONSTANTS
from ..core.config import CielConfig
from .ciel0_fft import CIEL0KernelFFT
from .ciel0_nofft import CIEL0KernelNoFFT


def make_ciel0_kernel(
    *,
    cfg: CielConfig,
    grid_size: int = 64,
    constants: CIELConstants = DEFAULT_CONSTANTS,
    length: float = 10.0,
):
    if cfg.compute_mode == 'nofft':
        return CIEL0KernelNoFFT(constants=constants, grid_size=grid_size)
    return CIEL0KernelFFT(constants=constants, grid_size=grid_size, length=length)
