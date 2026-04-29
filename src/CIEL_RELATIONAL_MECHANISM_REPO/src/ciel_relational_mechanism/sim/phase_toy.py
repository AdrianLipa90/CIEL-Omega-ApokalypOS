"""Minimal dimensionless relational phase toy simulator.

Mechanism only:
- phases on a cycle family
- Euler-Berry closure defect
- effective pair coupling kernel A_ij
- reduction readiness from defect threshold
No metric closure and no physical constants are assumed here.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import cmath, math

@dataclass
class PhaseState:
    labels: List[str]
    gamma: Dict[str, float]
    def delta_H(self) -> complex:
        return sum(cmath.exp(1j * self.gamma[label]) for label in self.labels)
    def R_H(self) -> float:
        d = self.delta_H()
        return d.real*d.real + d.imag*d.imag

@dataclass
class PairKernel:
    labels: List[str]
    values: Dict[Tuple[str, str], float] = field(default_factory=dict)
    @classmethod
    def zero(cls, labels: List[str]) -> 'PairKernel':
        vals = {(a,b):0.0 for a in labels for b in labels if a != b}
        return cls(labels=labels, values=vals)
    def set_symmetric(self, a: str, b: str, value: float) -> None:
        self.values[(a,b)] = value
        self.values[(b,a)] = value
    def neighbors(self, a: str):
        for b in self.labels:
            if a != b:
                yield b, self.values.get((a,b),0.0)

@dataclass
class StepRecord:
    step: int
    gamma: Dict[str, float]
    delta_H_real: float
    delta_H_imag: float
    R_H: float
    reduction_ready: bool

class RelationalPhaseToySim:
    def __init__(self, labels: List[str], initial_gamma: Dict[str, float], kernel: PairKernel, dt: float = 0.01, learning_rate: float = 0.05, reduction_threshold: float = 1.0):
        self.state = PhaseState(labels=labels, gamma=dict(initial_gamma))
        self.kernel = kernel
        self.dt = dt
        self.learning_rate = learning_rate
        self.reduction_threshold = reduction_threshold
        self.history: List[StepRecord] = []
    def effective_Aij_drive(self, a: str) -> float:
        ga = self.state.gamma[a]
        drive = 0.0
        for b, w in self.kernel.neighbors(a):
            drive += w * math.sin(self.state.gamma[b] - ga)
        return drive
    def step(self) -> StepRecord:
        updates = {a: self.learning_rate * self.effective_Aij_drive(a) for a in self.state.labels}
        for a, dgamma in updates.items():
            self.state.gamma[a] += self.dt * dgamma
        delta = self.state.delta_H(); rh = self.state.R_H()
        rec = StepRecord(step=len(self.history), gamma=dict(self.state.gamma), delta_H_real=delta.real, delta_H_imag=delta.imag, R_H=rh, reduction_ready=(rh <= self.reduction_threshold))
        self.history.append(rec)
        return rec
    def run(self, steps: int):
        return [self.step() for _ in range(steps)]
