"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List
import numpy as np, json, math

# Canonical imports replacing duplicate local definitions
from cognition.introspection import Introspection
from core.physics.csf_simulator import CSF2Kernel, CSF2State, make_csf2_seed
from mathematics.paradoxes.paradox_operators import ParadoxStress
from memory.synchronizer import MemorySynchronizer

def _lap(a: np.ndarray)->np.ndarray:
    out=np.zeros_like(a); out[1:-1,1:-1]=(a[2:,1:-1]+a[:-2,1:-1]+a[1:-1,2:]+a[1:-1,:-2]-4.0*a[1:-1,1:-1]); return out
class CSFReporter:
    def metrics(self, s: CSF2State)->Dict[str,float]:
        grad=np.gradient(s.psi)
        E = float(np.mean(np.abs(grad[0])**2 + np.abs(grad[1])**2))
        coh = float(1.0/(1.0+E))
        return {"coherence":coh,"sigma_mean": float(np.mean(s.sigma)), "omega_var": float(np.var(s.omega))}
    def to_json(self, s: CSF2State)->str:
        return json.dumps({"sigma_mean": float(np.mean(s.sigma)), "coh": self.metrics(s)["coherence"]}, ensure_ascii=False)
class BackendGlue:
    """Adapter: CSF2 ↔ pełny backend (cielFullQuantumCore.py).
    Zakładamy, że backend ma metody:
      - set_fields(psi: np.ndarray, sigma: np.ndarray)
      - step(dt: float) -> None
      - get_fields() -> Tuple[np.ndarray, np.ndarray]
    """
    backend: Any
    def push(self, s: CSF2State)->None:
        self.backend.set_fields(s.psi, s.sigma)
    def pull(self, s: CSF2State)->CSF2State:
        psi,sigma = self.backend.get_fields()
        return CSF2State(psi, sigma, s.lam, s.omega)
    def evolve(self, s: CSF2State, steps:int=5, dt:float=0.02)->CSF2State:
        self.push(s)
        for _ in range(steps): self.backend.step(dt=dt)
        return self.pull(s)
def csf2_demo(steps:int=20)->Dict[str,float]:
    st=make_csf2_seed(); ker=CSF2Kernel(); mem=MemorySynchronizer(); rep=CSFReporter(); stress=ParadoxStress(0.06)
    for k in range(steps):
        st=ker.step(st)
        if (k%5)==0: st=stress.apply(st)
        mem.update(st.sigma, st.psi)
    return rep.metrics(st)
if __name__=="__main__":
    print(csf2_demo(24))