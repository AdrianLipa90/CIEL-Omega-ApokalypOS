#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metatime Gluon Solver v2.0
Pełny solver dla sektora gluonowego w teorii Metatime.
Oblicza:
- τ dla 8 gluonów z pierwszych par bliźniaczych
- stałą sprzężenia g i α_s(bare)
- skalę μ* z jednopętlowej funkcji beta QCD
- masę najlżejszego glueballa (0^{++})
- macierze Gell-Manna i stałe struktury SU(3)
- opcjonalnie inne wielkości (np. stałą napięcia struny)
Wszystkie stałe pochodzą z dokumentów Metatime.
"""

import numpy as np
from sympy import isprime
from typing import List, Tuple, Optional

# =============================================================================
# 1. Generowanie τ z liczb bliźniaczych
# =============================================================================

def generate_twin_primes(n_pairs: int = 8) -> List[Tuple[int, int]]:
    """
    Generuje pierwsze n_pairs par liczb bliźniaczych (p, p+2).
    """
    twins = []
    num = 3
    while len(twins) < n_pairs:
        if isprime(num) and isprime(num + 2):
            twins.append((num, num + 2))
        num += 2
    return twins

def tau_from_twins(twin_pairs: List[Tuple[int, int]]) -> np.ndarray:
    """
    Dla każdej pary (p, p+2) zwraca τ = p+1.
    """
    return np.array([p + 1 for p, _ in twin_pairs])

# =============================================================================
# 2. Stałe teorii Metatime (z dokumentów)
# =============================================================================

# Podstawowe stałe (z lie4full.py / BookOfParadoxes.pdf)
ALPHA_C = 0.474812      # współczynnik kinetyczny pola informacji (1/g^2)
I0 = 0.009               # operator intencji
BETA_FERMION = 0.414     # wykładnik dla fermionów (z mas)
M_E = 0.511              # masa elektronu w MeV
TAU_E = 4.0              # τ elektronu (z generatora)

# Stałe QCD
M_Z = 91.1876            # masa Z w GeV
ALPHA_S_MZ = 0.118       # α_s(M_Z) eksperymentalne
N_F = 5                  # liczba aktywnych zapachów w skali GeV

# =============================================================================
# 3. Główna klasa solvera
# =============================================================================

class GluonSolver:
    """
    Solver dla sektora gluonowego Metatime.
    """
    def __init__(self, twin_pairs: Optional[List[Tuple[int, int]]] = None):
        """
        Inicjalizacja: jeśli nie podano par, generuje 8 pierwszych par bliźniaczych.
        """
        if twin_pairs is None:
            twin_pairs = generate_twin_primes(8)
        self.twin_pairs = twin_pairs
        self.tau = tau_from_twins(twin_pairs)
        self._compute_all()

    def _compute_all(self):
        """Oblicza wszystkie pochodne wielkości."""
        # Stałe podstawowe
        self.alpha_c = ALPHA_C
        self.I0 = I0
        self.g = 1.0 / np.sqrt(self.alpha_c)
        self.alpha_s_bare = self.g**2 / (4 * np.pi)

        # Skala masy M0 z elektronu
        self.M0 = M_E / (TAU_E ** BETA_FERMION)   # MeV

        # Masa glueballa
        self.sum_tau2 = np.sum(self.tau ** 2)
        self.m_glueball_MeV = self.M0 * self.alpha_c * self.sum_tau2
        self.m_glueball_GeV = self.m_glueball_MeV / 1000.0

        # Skala μ*
        self._compute_mu_star()

        # Macierze Gell-Manna i stałe struktury
        self.T_matrices, self.f_abc = self._su3_generators()

    def _compute_mu_star(self):
        """Oblicza skalę μ*, przy której α_s(μ*) = α_s_bare."""
        beta0 = 11 - 2/3 * N_F
        # alpha_s(μ) = alpha_s(M_Z) / (1 + (beta0 * alpha_s(M_Z)/(2π)) * ln(μ/M_Z))
        C = (beta0 * ALPHA_S_MZ) / (2 * np.pi)
        # Rozwiązujemy: alpha_s_bare = ALPHA_S_MZ / (1 + C * ln(μ/M_Z))
        # => 1 + C ln(μ/M_Z) = ALPHA_S_MZ / alpha_s_bare
        ratio = ALPHA_S_MZ / self.alpha_s_bare
        if ratio <= 0:
            self.mu_star = np.nan
            return
        log_arg = (ratio - 1) / C   # ujemne, bo alpha_s_bare > ALPHA_S_MZ
        self.mu_star = M_Z * np.exp(log_arg)

    def _su3_generators(self) -> Tuple[List[np.ndarray], np.ndarray]:
        """
        Zwraca listę 8 macierzy Gell-Manna (generatory SU(3) w reprezentacji fundamentalnej)
        oraz tablicę stałych struktury f^{abc} (wymiar 8x8x8).
        """
        # Macierze Gell-Manna (standardowe)
        λ = []
        # λ1
        λ1 = np.array([[0, 1, 0],
                       [1, 0, 0],
                       [0, 0, 0]], dtype=complex)
        λ.append(λ1)
        # λ2
        λ2 = np.array([[0, -1j, 0],
                       [1j, 0, 0],
                       [0, 0, 0]], dtype=complex)
        λ.append(λ2)
        # λ3
        λ3 = np.array([[1, 0, 0],
                       [0, -1, 0],
                       [0, 0, 0]], dtype=complex)
        λ.append(λ3)
        # λ4
        λ4 = np.array([[0, 0, 1],
                       [0, 0, 0],
                       [1, 0, 0]], dtype=complex)
        λ.append(λ4)
        # λ5
        λ5 = np.array([[0, 0, -1j],
                       [0, 0, 0],
                       [1j, 0, 0]], dtype=complex)
        λ.append(λ5)
        # λ6
        λ6 = np.array([[0, 0, 0],
                       [0, 0, 1],
                       [0, 1, 0]], dtype=complex)
        λ.append(λ6)
        # λ7
        λ7 = np.array([[0, 0, 0],
                       [0, 0, -1j],
                       [0, 1j, 0]], dtype=complex)
        λ.append(λ7)
        # λ8
        λ8 = np.array([[1, 0, 0],
                       [0, 1, 0],
                       [0, 0, -2]], dtype=complex) / np.sqrt(3)
        λ.append(λ8)

        # Normalizacja do Tr(T^a T^b) = 1/2 δ^{ab}
        T = [lam / 2.0 for lam in λ]

        # Obliczanie stałych struktury f^{abc} z komutatorów [T^a, T^b] = i f^{abc} T^c
        f = np.zeros((8, 8, 8), dtype=float)
        for a in range(8):
            for b in range(8):
                comm = T[a] @ T[b] - T[b] @ T[a]
                for c in range(8):
                    # f^{abc} = -2i Tr( T^c [T^a, T^b] )
                    val = -2j * np.trace(T[c] @ comm)
                    f[a, b, c] = np.real(val)  # powinno być rzeczywiste
        return T, f

    def print_summary(self):
        """Drukuje pełne podsumowanie wyników."""
        print("=" * 70)
        print("🌌 METATIME GLUON SOLVER – WYNIKI")
        print("=" * 70)
        print(f"Liczba gluonów: {len(self.tau)}")
        print(f"Pary bliźniacze: {self.twin_pairs}")
        print(f"τ gluonów: {self.tau.tolist()}")
        print(f"Suma kwadratów τ: {self.sum_tau2:.1f}")
        print("-" * 70)
        print(f"α_c (pole informacji) = {self.alpha_c:.6f}")
        print(f"g = 1/√α_c = {self.g:.6f}")
        print(f"α_s(bare) = g²/(4π) = {self.alpha_s_bare:.6f}")
        print(f"Skala μ* (α_s = α_s_bare) = {self.mu_star:.2f} GeV")
        print("-" * 70)
        print(f"Masa glueballa 0⁺⁺:")
        print(f"  M₀ (z elektronu) = {self.M0:.4f} MeV")
        print(f"  m_glueball = {self.m_glueball_MeV:.1f} MeV = {self.m_glueball_GeV:.3f} GeV")
        print(f"  (porównanie z kratą QCD: ~1.7 GeV)")
        print("-" * 70)
        print("Stałe struktury SU(3) f^{abc} (wybrane niezerowe):")
        for a in range(8):
            for b in range(a+1, 8):
                for c in range(8):
                    if abs(self.f_abc[a, b, c]) > 1e-10:
                        print(f"  f^{a+1}{b+1}{c+1} = {self.f_abc[a, b, c]:.3f}")
        print("=" * 70)

# =============================================================================
# 4. Przykład użycia
# =============================================================================

if __name__ == "__main__":
    solver = GluonSolver()
    solver.print_summary()

    # Opcjonalnie: można też podać własne pary
    # własne_pary = [(3,5), (5,7), (11,13), (17,19), (29,31), (41,43), (59,61), (71,73)]
    # solver2 = GluonSolver(twin_pairs=własne_pary)
    # solver2.print_summary()