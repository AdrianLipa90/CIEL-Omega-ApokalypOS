#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metatime / ResChem General Solver v1.1
Author: Adrian Lipa (CIEL/0 Project)
Based on the Metatime/ResChem Formalism v2.0

This solver implements the core equations of the unified theory:
- Information operator O_I and its fluctuations (from first Riemann zero)
- Fermion masses with topological indices and linking numbers
- Boson masses (W, Z, Higgs) from spectral scaling
- Nuclear binding energies via scaled SEMF
- Material wave analysis: atomic frequencies, chord coherence
- Superconductor properties (YBCO example)
- Fractal potential for O_I vacuum expectation value
"""

import numpy as np
from scipy.optimize import minimize_scalar
from typing import Dict, List, Tuple, Optional

# =============================================================================
# 1. Fundamental constants
# =============================================================================

OI_REF = 0.00917                 # reference information operator
IM_S1 = 14.134725141734694       # first nontrivial Riemann zero
SIGMA_OI = OI_REF / IM_S1         # fluctuation scale (Heisenberg-Lipa rule)

BETA = 0.414341                   # spectral exponent = 1/(1 + IM_S1/10)
D_F = 2.7                         # fractal dimension for mass scaling

# Golden ratio
PHI = (1 + np.sqrt(5)) / 2

# Mass scale (adjust to match PDG in MeV)
M0_FERMION = 1.0                  # base unit for fermion masses (will be scaled)
M0_BOSON = 1000.0                 # base unit for boson masses (MeV), effectively GeV/MeV

# =============================================================================
# 2. Topological indices and linking coefficients (examples)
#    These should be derived from twin‑prime / Collatz analysis.
#    Here we provide typical values from METATIME v2.1.
# =============================================================================

LAMBDA_F = {
    'e': 0.996,      # electron
    'μ': 1.052,      # muon (placeholder)
    'τ': 1.200,      # tau (placeholder)
    'u': 1.050,      # up quark
    'd': 1.020,      # down quark
    's': 1.080,      # strange quark
    'c': 1.120,      # charm quark
    'b': 1.150,      # bottom quark
    't': 1.200,      # top quark
}

C_F = {
    'e': 0.0,        # electron: no topological correction
    'μ': 0.1,        # muon: small positive
    'τ': 0.05,       # tau: very small
    'u': -12.5,      # up quark: moderate suppression
    'd': -27.13,     # down quark: strong destructive interference
    's': -6.3,       # strange quark: mild suppression
    'c': -5.1,       # charm quark
    'b': -0.9,       # bottom quark
    't': 0.8,        # top quark: slight enhancement
}

# =============================================================================
# 3. Helper functions
# =============================================================================

def sample_oi(n_samples: int = 1, seed: Optional[int] = None) -> np.ndarray:
    """
    Sample O_I from a normal distribution centered at OI_REF with width SIGMA_OI.
    """
    if seed is not None:
        np.random.seed(seed)
    return np.random.normal(OI_REF, SIGMA_OI, size=n_samples)

# =============================================================================
# 4. Fermion masses
# =============================================================================

def mass_fermion(particle: str, oi: float, scale: float = 1.0) -> float:
    """
    Compute fermion mass for given O_I.
    Formula: m = M0 * λ^β * exp( C * (oi - OI_REF) )
    """
    lam = LAMBDA_F.get(particle, 1.0)
    c = C_F.get(particle, 0.0)
    return scale * (lam ** BETA) * np.exp(c * (oi - OI_REF))

# =============================================================================
# 5. Boson masses (from spectral scaling)
# =============================================================================

def mass_Z(oi: float) -> float:
    """
    Z boson mass: m_Z = (IM_S1 * 2π / oi) * spectral_scale
    spectral_scale = 9.3503 (from Metatime Unified Monolith)
    """
    spectral_scale = 9.3503
    return (IM_S1 * 2 * np.pi / oi) * spectral_scale  # in MeV (since M0_BOSON = 1000)

def mass_W(oi: float) -> float:
    """
    W boson mass: from Weinberg angle cosθ_W ≈ 0.88147 (related to golden ratio)
    """
    cos_theta_w = 0.88147
    return mass_Z(oi) * cos_theta_w

def mass_Higgs(oi: float) -> float:
    """
    Higgs mass: from ratio m_H/m_Z ≈ 1.3718 (topological seam)
    """
    higgs_ratio = 1.3718
    return mass_Z(oi) * higgs_ratio

# =============================================================================
# 6. Nuclear binding energy (scaled SEMF)
# =============================================================================

def binding_energy_semf(A: int, Z: int, oi: float) -> float:
    """
    Semi‑empirical mass formula with coefficients scaled by O_I.
    gamma = 1 / (1 + IM_S1/A)
    """
    gamma = 1.0 / (1.0 + IM_S1 / A)
    scale = (oi / OI_REF) ** gamma

    # Base coefficients (in MeV)
    a_v0, a_s0, a_c0, a_a0 = 15.5, 16.8, 0.72, 23.0
    a_v = a_v0 * scale
    a_s = a_s0 * scale
    a_c = a_c0 * scale
    a_a = a_a0 * scale

    # Volume, surface, Coulomb, asymmetry terms
    vol = a_v * A
    surf = -a_s * A**(2/3)
    coul = -a_c * Z * (Z - 1) / A**(1/3)
    asym = -a_a * (A - 2*Z)**2 / A

    # Pairing term δ
    if A % 2 == 1:
        delta = 0.0
    elif Z % 2 == 0:
        delta = 12.0 / np.sqrt(A)
    else:
        delta = -12.0 / np.sqrt(A)

    return vol + surf + coul + asym + delta

# =============================================================================
# 7. Material wave analysis
# =============================================================================

def atom_frequency(f0: float, lam: float, oi: float) -> float:
    """
    Characteristic frequency of an atom: f = f0 * λ * (oi / OI_REF)
    """
    return f0 * lam * (oi / OI_REF)

def chord_coherence(frequencies: List[float]) -> float:
    """
    Compute chord coherence C_chord as fraction of pairs whose frequency
    difference modulo 12 falls into the set of pure intervals K.
    """
    K = {0, 3, 4, 5, 7, 8, 9}
    n = len(frequencies)
    if n < 2:
        return 0.0
    count = 0
    for i in range(n):
        for j in range(i+1, n):
            diff_mod12 = int(abs(frequencies[i] - frequencies[j])) % 12
            if diff_mod12 in K:
                count += 1
    total_pairs = n * (n - 1) / 2
    return count / total_pairs

def estimate_Tc(material_params: Dict, oi: float) -> Tuple[float, float]:
    """
    Simplified estimate of superconducting Tc (e.g., for YBCO).
    material_params should contain:
        - 'f0' : reference frequency
        - 'lambda_atoms' : list of λ for each atom type
        - 'amplitudes' : list of wave amplitudes
        - 'Tc_base' : base critical temperature (K)
    """
    f0 = material_params['f0']
    lam_list = material_params['lambda_atoms']
    amps = material_params['amplitudes']
    Tc_base = material_params['Tc_base']

    freqs = [atom_frequency(f0, lam, oi) for lam in lam_list]
    C_chord = chord_coherence(freqs)
    avg_amp = np.mean(amps)
    Tc = Tc_base * avg_amp * C_chord
    return Tc, C_chord

# =============================================================================
# 8. Fractal potential V_fractal(OI) and vacuum expectation value
# =============================================================================

# Small set of twin primes for demonstration (first few pairs)
TWIN_PRIMES = [(3,5), (5,7), (11,13), (17,19), (29,31), (41,43), (59,61), (71,73)]

def V_fractal(oi: float, twin_primes: List[Tuple[int,int]] = TWIN_PRIMES,
              C2: float = 0.66016) -> float:
    """
    Fractal potential from twin‑prime distribution.
    V = C2 * Σ_{twin primes} (1/ln^2 p) * cos(2π (oi/OI_REF) ln p) * exp(-oi/p)
    """
    total = 0.0
    for p, _ in twin_primes:
        lnp = np.log(p)
        term = (1.0 / (lnp * lnp)) * np.cos(2 * np.pi * (oi / OI_REF) * lnp) * np.exp(-oi / p)
        total += term
    return C2 * total

def find_vev(oi_guess: float = OI_REF) -> float:
    """
    Numerically minimize V_fractal to obtain the vacuum expectation value ⟨O_I⟩.
    """
    res = minimize_scalar(V_fractal, bracket=(0.5*OI_REF, 1.5*OI_REF), method='brent')
    if res.success:
        return res.x
    else:
        raise RuntimeError("VEV minimization failed")

# =============================================================================
# 9. Example usage and tests
# =============================================================================

def demo():
    print("=" * 60)
    print("METATIME / RESCHEM GENERAL SOLVER v1.1")
    print("=" * 60)

    # Sample O_I
    oi = sample_oi(seed=42)[0]
    print(f"\nSampled O_I = {oi:.6f}  (reference: {OI_REF})")

    # Fermion masses (scale to MeV for leptons, GeV for quarks)
    print("\n--- Fermion masses ---")
    for p in ['e', 'μ', 'τ', 'u', 'd', 's', 'c', 'b', 't']:
        scale = 1.0 if p in ['e','μ','τ'] else 1000.0  # quarks in MeV (top in GeV later)
        m = mass_fermion(p, oi, scale=scale)
        unit = "MeV" if p in ['e','μ','τ'] else "MeV" if p != 't' else "GeV"
        if p == 't':
            m /= 1000.0   # convert to GeV
        print(f"  m_{p:2} = {m:8.3f} {unit}")

    # Boson masses (in GeV)
    print("\n--- Boson masses (GeV) ---")
    mz = mass_Z(oi) / 1000.0
    mw = mass_W(oi) / 1000.0
    mh = mass_Higgs(oi) / 1000.0
    print(f"  m_Z  = {mz:8.3f} GeV")
    print(f"  m_W  = {mw:8.3f} GeV")
    print(f"  m_H  = {mh:8.3f} GeV")

    # Nuclear binding energy for selected nuclei
    print("\n--- Nuclear binding energy (MeV/nucleon) ---")
    nuclei = [(56,26,'Fe-56'), (208,82,'Pb-208'), (16,8,'O-16')]
    for A, Z, name in nuclei:
        B = binding_energy_semf(A, Z, oi)
        print(f"  {name:6} : B/A = {B/A:6.3f} MeV")

    # Material example: YBCO (simplified)
    print("\n--- Superconductor YBCO ---")
    ybco_params = {
        'f0': 1.0,                       # THz (arbitrary scale)
        'lambda_atoms': [0.702, 0.748, 0.738, 0.540],  # for Y, Ba, Cu, O
        'amplitudes': [0.466, 0.566, 1.412, 0.707],
        'Tc_base': 38.28                  # base Tc in K
    }
    Tc, Cc = estimate_Tc(ybco_params, oi)
    print(f"  Chord coherence C_chord = {Cc:.3f}")
    print(f"  Estimated Tc = {Tc:.2f} K  (experimental YBCO ~92 K)")

    # VEV of O_I from fractal potential
    print("\n--- Fractal potential minimum ---")
    vev = find_vev()
    print(f"  ⟨O_I⟩ = {vev:.6f}  (reference = {OI_REF})")

if __name__ == "__main__":
    demo()