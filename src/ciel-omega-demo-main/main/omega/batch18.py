from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import hashlib
import json
import threading

import numpy as np

from .field_ops import coherence_metric, field_norm, laplacian2, normalize_field
from .schumann import SchumannClock


@dataclass
class OmegaDriftCorePlus:
    clock: SchumannClock
    drift_gain: float = 0.045
    harmonic_sweep: Tuple[int, int] = (1, 3)
    jitter: float = 0.004
    renorm: bool = True

    def step(self, psi: np.ndarray, sigma_scalar: float = 1.0, t: Optional[float] = None) -> np.ndarray:
        hmin, hmax = self.harmonic_sweep
        sigma_clipped = float(np.clip(sigma_scalar, 0.0, 1.0))
        h = int(np.clip(round(hmin + (hmax - hmin) * sigma_clipped), hmin, hmax))
        ph = self.clock.phase(t=t, k=h) + float(np.random.uniform(-self.jitter, self.jitter))
        psi_next = psi * np.exp(1j * (self.drift_gain * float(sigma_scalar) + ph))
        if self.renorm:
            psi_next = normalize_field(psi_next)
        return psi_next


@dataclass
class OmegaBootRitual:
    drift: OmegaDriftCorePlus
    steps: int = 16
    intent_bias: float = 0.12
    log: List[Dict[str, Any]] = field(default_factory=list, init=False)

    def run(self, psi0: np.ndarray, sigma0: float = 0.5) -> Dict[str, Any]:
        psi = psi0.copy()
        sigma = float(sigma0)
        self.log.clear()

        for i in range(int(self.steps)):
            psi *= np.exp(1j * float(self.intent_bias))
            psi = self.drift.step(psi, sigma_scalar=sigma)
            psi = psi + 1j * 0.01 * laplacian2(psi)
            psi = normalize_field(psi)
            sigma = float(np.clip(0.92 * sigma + 0.08 * field_norm(psi) ** 2, 0.0, 1.2))
            self.log.append({'step': i, 'sigma': sigma, 'coh': coherence_metric(psi)})

        return {
            'psi': psi,
            'sigma': sigma,
            'coherence': coherence_metric(psi),
            'boot_complete': True,
            'log': list(self.log),
        }


@dataclass
class RCDECalibratorPro:
    lam: float = 0.22
    dt: float = 0.05
    sigma: float = 0.5
    target_sigma_fn: Optional[Callable[[np.ndarray], float]] = None
    lam_bounds: Tuple[float, float] = (0.05, 0.5)

    def _target(self, psi: np.ndarray) -> float:
        if self.target_sigma_fn is not None:
            return float(self.target_sigma_fn(psi))
        return float(field_norm(psi) ** 2)

    def step(self, psi: np.ndarray) -> float:
        target = self._target(psi)
        err = float(target - self.sigma)
        lam_adapt = float(np.clip(float(self.lam) * (1.0 + 0.8 * abs(err)), self.lam_bounds[0], self.lam_bounds[1]))
        self.sigma = float(self.sigma + float(self.dt) * lam_adapt * err)
        self.sigma = float(np.clip(self.sigma, 0.0, 1.5))
        return self.sigma


@dataclass
class NodeState:
    name: str
    psi: np.ndarray
    sigma: float


def _empathy(A: np.ndarray, B: np.ndarray) -> float:
    return float(np.exp(-np.mean(np.abs(A - B))))


@dataclass
class ResConnectParallel:
    nodes: List[NodeState]
    drift_factory: Callable[[], OmegaDriftCorePlus]
    history: List[Dict[str, Any]] = field(default_factory=list, init=False)

    def step(self) -> None:
        threads: List[threading.Thread] = []
        results: Dict[str, Tuple[np.ndarray, float]] = {}
        lock = threading.Lock()

        def evolve(node: NodeState) -> None:
            drift = self.drift_factory()
            psi = drift.step(node.psi, sigma_scalar=node.sigma)
            psi = psi + 1j * 0.01 * laplacian2(psi)
            psi = normalize_field(psi)
            sig = float(np.clip(0.9 * node.sigma + 0.1 * field_norm(psi) ** 2, 0.0, 1.2))
            with lock:
                results[node.name] = (psi, sig)

        for n in self.nodes:
            th = threading.Thread(target=evolve, args=(n,), daemon=True)
            threads.append(th)
            th.start()
        for th in threads:
            th.join()

        for n in self.nodes:
            psi, sig = results[n.name]
            n.psi = psi
            n.sigma = sig

        if len(self.nodes) >= 2:
            ems: List[float] = []
            base = self.nodes[0].psi
            for n in self.nodes[1:]:
                ems.append(_empathy(base, n.psi))
            self.history.append({'empathy_mean': float(np.mean(ems)), 'nodes': len(self.nodes)})

    def snapshot(self) -> Dict[str, Any]:
        return {
            'nodes': [{'name': n.name, 'sigma': float(n.sigma), 'coh': coherence_metric(n.psi)} for n in self.nodes],
            'last_empathy': (self.history[-1]['empathy_mean'] if self.history else None),
        }


@dataclass
class DissociationAnalyzer:
    low_thr: float = 0.3
    high_thr: float = 0.8
    hysteresis: float = 0.05
    state: str = field(default='mixed', init=False)

    def step(self, ego: np.ndarray, world: np.ndarray) -> Dict[str, Any]:
        a = ego.real.ravel()
        b = world.real.ravel()
        a = (a - a.mean()) / (a.std() + 1e-12)
        b = (b - b.mean()) / (b.std() + 1e-12)
        rho = float(np.dot(a, b) / max(1, (len(a) - 1)))

        if self.state != 'dissociation' and rho < (float(self.low_thr) - float(self.hysteresis)):
            self.state = 'dissociation'
        elif self.state != 'integration' and rho > (float(self.high_thr) + float(self.hysteresis)):
            self.state = 'integration'
        elif self.state not in ('dissociation', 'integration'):
            self.state = 'mixed'

        blend: Optional[np.ndarray] = None
        if self.state == 'dissociation':
            phase = np.angle(world)
            blend = ego * 0.9 + 0.1 * np.exp(1j * phase)
            blend = normalize_field(blend)

        return {'rho': rho, 'state': self.state, 'reintegration_suggestion': blend}


@dataclass
class LongTermMemory:
    entries: List[Dict[str, Any]] = field(default_factory=list)

    def put(self, label: str, psi: np.ndarray, sigma: float, meta: Optional[Dict[str, Any]] = None) -> None:
        payload: Dict[str, Any] = {
            'label': label,
            'sigma': float(sigma),
            'shape': tuple(int(x) for x in psi.shape),
            'psi_real': psi.real.astype(np.float32).tolist(),
            'psi_imag': psi.imag.astype(np.float32).tolist(),
            'meta': dict(meta or {}),
        }
        payload['hash'] = hashlib.sha256(json.dumps(payload['psi_real'][:64]).encode()).hexdigest()[:16]
        self.entries.append(payload)

    def export_json(self) -> str:
        return json.dumps(self.entries, ensure_ascii=False)

    def load_json(self, data: str) -> None:
        self.entries = json.loads(data)

    def restore(self, idx: int = -1) -> Tuple[np.ndarray, float, Dict[str, Any]]:
        e = self.entries[idx]
        re = np.array(e['psi_real'], dtype=np.float32).reshape(e['shape'])
        im = np.array(e['psi_imag'], dtype=np.float32).reshape(e['shape'])
        psi = (re + 1j * im).astype(np.complex128)
        return psi, float(e['sigma']), dict(e.get('meta', {}))


@dataclass
class CollatzLie4Engine:
    steps: int = 64

    def collatz_seq(self, n: int) -> List[int]:
        if n <= 0:
            raise ValueError('n must be > 0')
        seq = [int(n)]
        while n != 1 and len(seq) < int(self.steps):
            n = (3 * n + 1) if (n % 2) else (n // 2)
            seq.append(int(n))
        return seq

    def _E(self, i: int, j: int) -> np.ndarray:
        M = np.zeros((4, 4), dtype=float)
        M[i, j] = 1.0
        return M

    def lorentz_gen(self, mu: int, nu: int) -> np.ndarray:
        eta = np.diag([1.0, -1.0, -1.0, -1.0])
        s1 = self._E(mu, nu) * eta[nu, nu]
        s2 = self._E(nu, mu) * eta[mu, mu]
        return s1 - s2

    def invariant(self, n: int) -> Dict[str, float]:
        seq = self.collatz_seq(int(n))
        G = np.eye(4)
        for k, val in enumerate(seq[:8]):
            i = (int(val) % 3) + 1
            A = self.lorentz_gen(0, i)
            G = G @ (np.eye(4) + (0.05 + 0.01 * k) * A)
        detG = float(np.linalg.det(G))
        trG = float(np.trace(G))
        spec = float(np.max(np.real(np.linalg.eigvals(G))))
        return {'det': detG, 'trace': trG, 'spec': spec, 'len': float(len(seq))}


def demo(steps: int = 12, n: int = 96) -> Dict[str, Any]:
    x = np.linspace(-2.0, 2.0, int(n))
    X, Y = np.meshgrid(x, x)
    psi0 = np.exp(-(X**2 + Y**2)) * np.exp(1j * (X + 0.2 * Y))

    clk = SchumannClock()
    drift = OmegaDriftCorePlus(clk, drift_gain=0.04, harmonic_sweep=(1, 3), jitter=0.003)
    boot = OmegaBootRitual(drift, steps=int(steps), intent_bias=0.1)
    out = boot.run(psi0, sigma0=0.55)

    rcde = RCDECalibratorPro(lam=0.22, dt=0.05, sigma=0.6)
    psi = out['psi']
    for _ in range(10):
        psi = psi + 1j * 0.01 * laplacian2(psi)
        psi = normalize_field(psi)
        rcde.step(psi)

    nodes = [
        NodeState('A', psi0.copy(), 0.5),
        NodeState('B', psi0 * np.exp(1j * 0.3), 0.6),
        NodeState('C', psi0 * np.exp(1j * 0.6), 0.55),
    ]
    net = ResConnectParallel(nodes, drift_factory=lambda: OmegaDriftCorePlus(clk))
    for _ in range(5):
        net.step()

    da = DissociationAnalyzer()
    ego = psi0
    world = np.roll(psi0, 4, axis=1) * np.exp(1j * 0.25)
    diss = da.step(ego, world)

    ltm = LongTermMemory()
    ltm.put('post-boot', out['psi'], sigma=float(out['sigma']), meta={'coh': float(out['coherence'])})
    psi_rest, sigma_rest, meta_rest = ltm.restore(-1)

    cl4 = CollatzLie4Engine(steps=64)
    inv = cl4.invariant(27)

    return {
        'boot': {'sigma': float(out['sigma']), 'coherence': float(out['coherence'])},
        'rcde_pro_sigma': float(rcde.sigma),
        'resconnect': net.snapshot(),
        'dissociation': {'rho': float(diss['rho']), 'state': diss['state']},
        'ltm': {'entries': len(ltm.entries), 'sigma_rest': sigma_rest, 'meta': meta_rest, 'psi_shape': list(psi_rest.shape)},
        'collatz_lie4': inv,
    }
