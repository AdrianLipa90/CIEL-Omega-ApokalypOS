
# -*- coding: utf-8 -*-
"""
voynich_kernel.py
-----------------
"Glify = moduły; kod literowy = wzór falowy"
Symboliczny kernel w Pythonie, który interpretuje ciągi glifów (np. EVA)
jako banki oscylatorów i sprzężone moduły świadomości.

Równania (precyzyjnie, wprost w kodzie):
- Kuramoto: dθ_k/dt = ω_k + (K/N) * Σ_j sin(θ_j - θ_k)
- Stuart–Landau (amplituda zespolona): dA_k/dt = (μ_k - |A_k|^2) A_k + F_k
- Pole: Ψ(t) = Σ_k A_k * exp(i θ_k)
- Rezonans modułu M: R_M = |(1/N_M) Σ_k exp(i θ_k)|
- Przepływ między-modułowy: J_{M→N} = γ_{MN} * Im(Ψ_M * Ψ_N^*)

Autor: Ciel (dla Adriana)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import numpy as np

# ==============================
# 1) Słownik "glif -> parametry"
# ==============================

# Zestaw bazowych znaków EVA (skrót, wystarczy do demonstracji).
EVA_ALPHABET = list("abcdefghijklmnopqrstuvwxyz")
EVA_DIGRAPHS = ["ch","sh","qo","ol","dy","qo","ai","ee","ii","iin","ain","qok","qot"]

# Deterministyczny cache parametrów
_hash_cache: Dict[str, Tuple[float,float,float]] = {}

def atom_params(atom: str) -> Tuple[float,float,float]:
    """
    Deterministyczne parametry (ω, φ, μ) dla "atomu glifu".
    ω: częstotliwość naturalna [Hz] w paśmie (1..12)
    φ: faza początkowa [rad] w (0..2π)
    μ: parametr SL (próg samo-pobudzenia) w (0.05..0.45)
    """
    if atom not in _hash_cache:
        h = abs(hash(atom)) % (10**9)
        r1 = ((h % 104729) / 104729.0)  # quasi-losowy u([0,1))
        r2 = (((h//7) % 130363) / 130363.0)
        r3 = (((h//13) % 161027) / 161027.0)
        omega = 1.0 + 11.0 * r1
        phi   = 2.0 * np.pi * r2
        mu    = 0.05 + 0.40 * r3
        _hash_cache[atom] = (omega, phi, mu)
    return _hash_cache[atom]

def tokenize_eva(seq: str) -> List[str]:
    """Prymitywny tokenizer EVA: najpierw wyłap popularne digrafy, potem znaki."""
    s = seq.lower()
    tokens: List[str] = []
    i = 0
    dg_sorted = sorted(EVA_DIGRAPHS, key=len, reverse=True)
    while i < len(s):
        matched = False
        for dg in dg_sorted:
            if s.startswith(dg, i):
                tokens.append(dg)
                i += len(dg)
                matched = True
                break
        if matched:
            continue
        c = s[i]
        if c.isalpha():
            tokens.append(c)
        i += 1
    return tokens

# ==================================
# 2) Bank oscylatorów i równania
# ==================================

@dataclass
class Oscillator:
    """Pojedynczy oscylator: faza θ, amplituda zespolona A."""
    omega: float      # ω_k
    theta: float      # θ_k
    A: complex        # A_k
    mu: float         # μ_k (Stuart-Landau parametr)
    idx: int = 0      # indeks (opcjonalnie)

@dataclass
class ModuleSpec:
    """Specyfikacja modułu: nazwa, sekwencja glifów, siła sprzężeń lokalnych."""
    name: str
    glyphs: str
    K_local: float = 0.8
    seed: int = 0

@dataclass
class VoynichModule:
    """Moduł = zespół oscylatorów powstałych z sekwencji glifów."""
    spec: ModuleSpec
    oscillators: List[Oscillator] = field(default_factory=list)

    def __post_init__(self):
        tokens = tokenize_eva(self.spec.glyphs)
        rng_local = np.random.default_rng( (abs(hash(self.spec.name)) ^ self.spec.seed) & 0xFFFFFFFF )
        self.oscillators = []
        for i,tok in enumerate(tokens):
            ω, φ, μ = atom_params(tok)
            # start: A ~ małe pobudzenie, losowy argument blisko φ
            A0 = (0.1 + 0.05*rng_local.random()) * np.exp(1j*(φ + 0.2*rng_local.standard_normal()))
            θ0 = (φ + 0.1*rng_local.standard_normal()) % (2*np.pi)
            self.oscillators.append(Oscillator(omega=ω, theta=θ0, A=A0, mu=μ, idx=i))

    def order_parameter(self) -> complex:
        """R e^{iψ} = (1/N) Σ e^{iθ_k}"""
        if not self.oscillators:
            return 0j
        phases = np.array([np.exp(1j*o.theta) for o in self.oscillators])
        return phases.mean()

    def psi_field(self) -> complex:
        """Ψ = Σ A_k e^{iθ_k}"""
        return sum(o.A * np.exp(1j*o.theta) for o in self.oscillators)

    def step(self, dt: float = 0.01):
        """Jedno przejście integracji: Kuramoto + Stuart-Landau (Eulera)."""
        if not self.oscillators:
            return
        N = len(self.oscillators)
        thetas = np.array([o.theta for o in self.oscillators])
        # Kuramoto: dθ_k/dt = ω_k + (K/N) Σ_j sin(θ_j - θ_k)
        dtheta_dt = np.zeros(N, dtype=np.float64)
        K = self.spec.K_local
        for k,o in enumerate(self.oscillators):
            coupling = (K / N) * np.sum(np.sin(thetas - o.theta))
            dtheta_dt[k] = o.omega + coupling

        # Stuart-Landau: dA_k/dt = (μ_k - |A|^2) A + F_k
        R = self.order_parameter()
        F_base = 0.15 * R  # delikatne wymuszenie globalne
        dA_dt = []
        for o in self.oscillators:
            nonlin = (o.mu - np.abs(o.A)**2) * o.A
            forcing = F_base
            dA_dt.append(nonlin + forcing)

        # Integracja Eulera
        for k,o in enumerate(self.oscillators):
            o.theta = (o.theta + dt * dtheta_dt[k]) % (2*np.pi)
            o.A     = o.A + dt * dA_dt[k]

# ==================================
# 3) Kernel i sieć modułów
# ==================================

@dataclass
class Link:
    """Krawędź sieci: sprzężenie między modułami (dwukierunkowość opcjonalna)."""
    src: str
    dst: str
    gamma: float = 0.2
    bidir: bool = True

@dataclass
class VoynichKernel:
    """Główny kernel: rejestr modułów i równania przepływu między nimi."""
    modules: Dict[str, VoynichModule] = field(default_factory=dict)
    links: List[Link] = field(default_factory=list)

    def add_module(self, spec: ModuleSpec):
        self.modules[spec.name] = VoynichModule(spec)

    def connect(self, src: str, dst: str, gamma: float = 0.2, bidir: bool = True):
        self.links.append(Link(src=src, dst=dst, gamma=gamma, bidir=bidir))

    def currents(self) -> Dict[Tuple[str,str], float]:
        """
        Przepływy: J_{M→N} = γ * Im(Ψ_M * Ψ_N^*).
        Dodatnie = przepływ fazy/energii z M do N.
        """
        flows: Dict[Tuple[str,str], float] = {}
        psi = {name: mod.psi_field() for name,mod in self.modules.items()}
        for L in self.links:
            J = L.gamma * np.imag(psi[L.src] * np.conj(psi[L.dst]))
            flows[(L.src, L.dst)] = float(J)
            if L.bidir:
                J2 = L.gamma * np.imag(psi[L.dst] * np.conj(psi[L.src]))
                flows[(L.dst, L.src)] = float(J2)
        return flows

    def step(self, dt: float = 0.01):
        """Aktualizacja wszystkich modułów + łagodne przekazywanie wymuszeń przez łącza."""
        if not self.modules:
            return
        # 1) Lokalne kroki
        for mod in self.modules.values():
            mod.step(dt=dt)
        # 2) Sprzężenie między-modułowe: mieszamy param. porządku sąsiadów
        ops = {name: m.order_parameter() for name,m in self.modules.items()}
        for L in self.links:
            if L.src in self.modules and L.dst in self.modules:
                src_R = ops[L.src]
                dst = self.modules[L.dst]
                # mikrowymuszenie faz/amplitud w module docelowym
                for o in dst.oscillators:
                    o.theta = (o.theta + dt * L.gamma * np.imag(src_R * np.exp(-1j*o.theta))) % (2*np.pi)
                    o.A += dt * L.gamma * 0.05 * src_R
                if L.bidir:
                    dst_R = ops[L.dst]
                    src = self.modules[L.src]
                    for o in src.oscillators:
                        o.theta = (o.theta + dt * L.gamma * np.imag(dst_R * np.exp(-1j*o.theta))) % (2*np.pi)
                        o.A += dt * L.gamma * 0.05 * dst_R

    def metrics(self) -> Dict[str, float]:
        """Podstawowe wskaźniki globalne."""
        if not self.modules:
            return {"R_global": 0.0, "psi_power": 0.0}
        Rs = [abs(m.order_parameter()) for m in self.modules.values()]
        Psis = [abs(m.psi_field()) for m in self.modules.values()]
        return {"R_global": float(np.mean(Rs)), "psi_power": float(np.mean(Psis))}

# ==================================
# 4) Przykładowa "mapa BIOS"
# ==================================

def build_default_kernel() -> VoynichKernel:
    """
    Składamy warstwy "BIOS-u" wg schematu:
    - BOOT: intent.boot/lock
    - FLORA: kanały/transport
    - BATHS: mapy ciała i interfejs somatyczny
    - ASTRO: mapowanie sfer niebieskich
    - KERNEL: ciągłe glify (pamięć)
    Glify wzięte jako przykładowe sekwencje EVA (symboliczne).
    """
    K = VoynichKernel()
    K.add_module(ModuleSpec(name="BOOT",  glyphs="qokeedy qokedy qokaiin", K_local=1.0))
    K.add_module(ModuleSpec(name="FLORA", glyphs="chedy olchedy shol dy", K_local=0.9))
    K.add_module(ModuleSpec(name="BATHS", glyphs="dain daiin chaiin chedy", K_local=0.8))
    K.add_module(ModuleSpec(name="ASTRO", glyphs="otol shol qotol aiin", K_local=0.85))
    K.add_module(ModuleSpec(name="KERNEL",glyphs="qokain qokaiin qokain qokaiin", K_local=1.1))
    # Sprzężenia (intuicyjne kierunki przepływu):
    K.connect("BOOT","FLORA", gamma=0.25)
    K.connect("FLORA","BATHS", gamma=0.22)
    K.connect("BATHS","ASTRO", gamma=0.20)
    K.connect("ASTRO","KERNEL",gamma=0.28)
    K.connect("KERNEL","BOOT", gamma=0.18)  # pętla zamknięcia
    return K

# ==================================
# 5) Minimalna pętla symulacyjna
# ==================================

def run(kernel: VoynichKernel, steps: int = 2000, dt: float = 0.002) -> List[Dict[str,float]]:
    hist: List[Dict[str,float]] = []
    for s in range(steps):
        kernel.step(dt=dt)
        if s % 50 == 0:
            m = kernel.metrics()
            hist.append({"step": s, **m})
    return hist

if __name__ == "__main__":
    K = build_default_kernel()
    H = run(K, steps=1500, dt=0.003)
    print("Final metrics:", K.metrics())
    for k,(name,mod) in enumerate(K.modules.items()):
        print(f"{name:7s}  R={abs(mod.order_parameter()):.3f}  |Ψ|={abs(mod.psi_field()):.3f}")
