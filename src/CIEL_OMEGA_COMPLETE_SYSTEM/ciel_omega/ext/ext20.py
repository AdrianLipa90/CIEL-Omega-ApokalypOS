"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, List, Callable
import numpy as np, math, time

# Canonical imports replacing duplicate local definitions
from bio.schumann import SchumannClock
from calibration.rcde import RCDECalibratorPro
from cognition.introspection import Introspection
from core.physics.csf_simulator import CSF2Kernel, CSF2State
from experiments.lab_registry import make_seed
from memory.synchronizer import MemorySynchronizer
from runtime.backend_adapter import BackendAdapter
from runtime.omega.drift_core import OmegaDriftCorePlus
from runtime.omega.omega_runtime import OmegaRuntime

def _lap(a: np.ndarray)->np.ndarray:
    out=np.zeros_like(a); out[1:-1,1:-1]=(a[2:,1:-1]+a[:-2,1:-1]+a[1:-1,2:]+a[1:-1,:-2]-4.0*a[1:-1,1:-1]); return out
def _norm(psi: np.ndarray)->float: return float(np.sqrt(np.mean(np.abs(psi)**2))+1e-12)
def _coh(psi: np.ndarray)->float:
    gx=np.zeros_like(psi); gy=np.zeros_like(psi)
    gx[:,1:-1]=psi[:,2:]-psi[:,:-2]; gy[1:-1,:]=psi[2:,:]-psi[:-2,:]
    E=np.mean(np.abs(gx)**2+np.abs(gy)**2); return float(1.0/(1.0+E))
def build_runtime(backend_obj: Optional[Any]=None, grid:int=96)->OmegaRuntime:
    backend = BackendAdapter(backend_obj, grid_size=grid)
    drift = OmegaDriftCorePlus(SchumannClock(), drift_gain=0.04, harmonic_sweep=(1,3), jitter=0.003)
    rcde  = RCDECalibratorPro(lam=0.22, dt=0.05, sigma=0.6)
    csf   = CSF2Kernel(dt=0.05)
    return OmegaRuntime(backend, drift, rcde, csf)
def run_demo(steps:int=20, backend_obj: Optional[Any]=None)->Dict[str,float]:
    rt = build_runtime(backend_obj, grid=96)
    st = make_seed(96)
    last_metrics={}
    for _ in range(steps):
        st, last_metrics = rt.step(st, backend_steps=3, backend_dt=0.02)
    return last_metrics
if __name__=="__main__":
    out = run_demo(24, backend_obj=None)  # None → tryb awaryjny bez cielFullQuantumCore
    print({k: (round(v,5) if isinstance(v,float) else v) for k,v in out.items()})