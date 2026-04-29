"""
Neutrinotime14 — poprawiona symulacja CP naruszenia
====================================================
Naprawa Bug #1 (krytyczny): P_alpha_beta stosował globalną fazę Berry'ego
jako skalar np.exp(1j*gamma), który kasuje się w |·|² → ΔP_CP = 0.

FIX: Faza Berry'ego wchodzi WEWNĄTRZ macierzy fazowej, różnicowo
dla każdego eigenstanu masy, z wagami τᵢ z Metatime (Collatz):
  τ = [0.02, 0.05, 0.10]  →  τ_norm = τ / mean(τ)
  berry_k = γ · τ_norm[k]

Fizyczne uzasadnienie: różne stany masowe propagują wzdłuż różnych
orbit na M_time (różne τᵢ → różna akumulacja holonomii Berry'ego).
Dla antyneutrin: C-transformacja daje H → H*, A_n → -A_n*, γ → -γ
(Simon 1983, Phys. Rev. Lett. 51, 2167).

Naprawa Bug #2 (poważny): berry_phase() oznaczona jako aproksymacja
pierwszego rzędu holonomii, nie pełna faza geometryczna.

Adrian Lipa / CIEL — 2026-04-15
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Parametry fizyczne (PDG 2024) ─────────────────────────────────────────────

dm21 = 7.42e-5   # eV² (solar)
dm31 = 2.51e-3   # eV² (atmospheric)
E    = 0.01      # GeV ≈ 10 MeV (supernova neutrino)

theta12 = np.deg2rad(33.44)
theta23 = np.deg2rad(49.0)
theta13 = np.deg2rad(8.57)
delta_cp = 0.0   # Dirac phase = 0 → CP tylko z metatime

gamma_time = 0.05   # metatime coupling constant
epsilon    = 1e-4   # tensor time coupling

N_points   = 500
L_max_km   = 3.086e16  # 1 kpc [km]

# ── Metatime Collatz eigenvalues (τᵢ) ────────────────────────────────────────

# Trzy stany masowe mają różne τᵢ z twin-prime Collatz sequence
# (Formal_SM.pdf, MetaEFT.pdf)
TAU = np.array([0.02, 0.05, 0.10])
TAU_NORM = TAU / TAU.mean()   # [0.571, 1.429, 2.857] — relatywne wagi holonomii


# ── PMNS matrix ───────────────────────────────────────────────────────────────

def build_pmns(th12, th23, th13, delta):
    c12, s12 = np.cos(th12), np.sin(th12)
    c23, s23 = np.cos(th23), np.sin(th23)
    c13, s13 = np.cos(th13), np.sin(th13)
    eid = np.exp(-1j * delta)
    return np.array([
        [c12*c13,                      s12*c13,                    s13*np.conj(eid)],
        [-s12*c23 - c12*s23*s13*eid,   c12*c23 - s12*s23*s13*eid, s23*c13         ],
        [ s12*s23 - c12*c23*s13*eid,  -c12*s23 - s12*c23*s13*eid, c23*c13         ],
    ])

U     = build_pmns(theta12, theta23, theta13, delta_cp)
M2    = np.diag([0.0, dm21, dm31])
H_mass = M2 / (2 * E * 1e9)   # eV → GeV normalizacja


# ── Berry phase (aproksymacja pierwszego rzędu holonomii) ─────────────────────
# UWAGA [Bug #2 fix]: To jest aproksymacja ε·∫Tr(T_op)·|du|,
# NIE pełna faza geometryczna ∮⟨n|i∂_λ|n⟩dλ.
# Pełna implementacja wymaga diagonalizacji H(λ) wzdłuż trajektorii.

def berry_phase_approx(u_vectors: np.ndarray, eps: float) -> float:
    """
    Aproksymacja holonomii Berry'ego jako całka linii tensora czasu
    wzdłuż trajektorii w M_time.

    Args:
        u_vectors: trajektoria na S² (N×3 unit vectors)
        eps: coupling epsilon (metatime→neutrino Hilbert space)

    Returns:
        γ ≈ ε · ∫ Tr(T_op) · |du|  [aproksymacja, nie pełna faza Berry'ego]
    """
    gamma = 0.0
    for i in range(len(u_vectors) - 1):
        du = u_vectors[i+1] - u_vectors[i]
        # T_op: lokalna reprezentacja tensora czasu T_μν wzdłuż trajektorii
        T_op = np.array([
            [u_vectors[i][0] + 0.01*u_vectors[i][1],  u_vectors[i][1]          ],
            [u_vectors[i][1],                          u_vectors[i][2] + 0.01*u_vectors[i][0]],
        ])
        gamma += eps * np.trace(T_op) * np.linalg.norm(du)
    return gamma


# ── P_alpha_beta — POPRAWIONA ─────────────────────────────────────────────────

def P_alpha_beta(L: float, gamma: float, alpha: int = 0, beta: int = 1) -> float:
    """
    Prawdopodobieństwo przejścia ν_alpha → ν_beta na dystansie L.

    FIX Bug #1: Faza Berry'ego wchodzi WEWNĄTRZ macierzy fazowej,
    różnicowo per eigenstan masy z wagami τᵢ (Collatz/Metatime).

    Dla antyneutrin: przekaż gamma = -gamma_nu (C-transformacja).

    Args:
        L:     dystans [km]
        gamma: całkowita faza Berry'ego (γ_nu lub -γ_nu dla antyneutrin)
        alpha: flavor wejściowy (0=e, 1=μ, 2=τ)
        beta:  flavor wyjściowy

    Returns:
        P(ν_alpha → ν_beta)
    """
    mass_phases = np.diag(H_mass) * L      # φ_k = m_k²·L/(2E)

    # Kluczowa poprawka: Berry phase jest różnicowy per eigenstan
    # eigenstan k dostaje fazę γ·τ_norm[k] proporcjonalną do jego
    # pozycji na orbicie metatime (τᵢ z Collatz)
    berry_per_eigenstate = gamma * TAU_NORM  # shape (3,)

    # Macierz fazowa: exp(-i·φ_k + i·γ_k) per eigenstan
    phase_diag = np.exp(-1j * mass_phases + 1j * berry_per_eigenstate)
    phase_matrix = np.diag(phase_diag)

    # Amplituda przejścia: ⟨ν_beta|U·phase·U†|ν_alpha⟩
    U_L = U @ phase_matrix @ U.conj().T
    amp = U_L[beta, alpha]
    return float(np.abs(amp)**2)


# ── Trajektoria kosmologiczna ─────────────────────────────────────────────────

def build_trajectory(N: int, dynamic: bool = False) -> np.ndarray:
    """Trajektoria na S² (minimalna lub dynamiczna z perturbacjami)."""
    theta_base = np.linspace(0, np.pi/2, N)
    phi_base   = np.linspace(0, np.pi, N)

    if dynamic:
        delta_phi = 0.01 * np.sin(np.linspace(0, 20*np.pi, N))
        g_grad    = 0.005 * np.sin(np.linspace(0, 10*np.pi, N))
        theta = theta_base + delta_phi + g_grad
        phi   = phi_base   + delta_phi + g_grad + 0.01*np.random.randn(N)*0.1
    else:
        theta, phi = theta_base, phi_base

    return np.array([
        [np.sin(theta[i])*np.cos(phi[i]),
         np.sin(theta[i])*np.sin(phi[i]),
         np.cos(theta[i])]
        for i in range(N)
    ])


# ── Obliczenia ────────────────────────────────────────────────────────────────

u_vectors = build_trajectory(N_points, dynamic=True)

# Faza Berry'ego dla neutrin (aproksymacja)
gamma_berry = berry_phase_approx(u_vectors, epsilon)
gamma_nu    = gamma_time + gamma_berry
gamma_anu   = -gamma_nu   # C-transformacja: γ → -γ (Simon 1983)

print(f"γ_berry (aproks.)  = {gamma_berry:.6f}")
print(f"γ_nu (total)       = {gamma_nu:.6f}")
print(f"γ_anu              = {gamma_anu:.6f}")
print(f"TAU_NORM           = {TAU_NORM}")
print()

# Prawdopodobieństwa w funkcji L
L_vals = np.linspace(0, L_max_km, 300)

P_nu_emu   = np.array([P_alpha_beta(L, gamma_nu,  alpha=0, beta=1) for L in L_vals])
P_anu_emu  = np.array([P_alpha_beta(L, gamma_anu, alpha=0, beta=1) for L in L_vals])
DeltaP_mu  = P_nu_emu - P_anu_emu

P_nu_etau  = np.array([P_alpha_beta(L, gamma_nu,  alpha=0, beta=2) for L in L_vals])
P_anu_etau = np.array([P_alpha_beta(L, gamma_anu, alpha=0, beta=2) for L in L_vals])
DeltaP_tau = P_nu_etau - P_anu_etau

# Sprawdzenie
print(f"max |ΔP_CP (ν_μ)|  = {np.max(np.abs(DeltaP_mu)):.6f}  ← powinno być > 0")
print(f"max |ΔP_CP (ν_τ)|  = {np.max(np.abs(DeltaP_tau)):.6f}  ← powinno być > 0")
print(f"mean ΔP_CP (ν_μ)   = {np.mean(DeltaP_mu):.6f}")
print()

# ── Wykresy ───────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 1, figsize=(12, 8))
fig.suptitle(
    "Neutrinotime14 — POPRAWIONE oscylacje neutrin\n"
    "Faza Berry'ego różnicowa per eigenstan (τᵢ z Collatz/Metatime)",
    fontsize=13
)

# Panel 1: ν_e → ν_μ
ax1 = axes[0]
ax1.plot(L_vals, P_nu_emu,  label=r'$P(\nu_e \to \nu_\mu)$',        lw=2)
ax1.plot(L_vals, P_anu_emu, label=r'$P(\bar\nu_e \to \bar\nu_\mu)$', lw=2, ls='--')
ax1.plot(L_vals, DeltaP_mu, label=r'$\Delta P_{CP}$', color='black', lw=1.5, ls=':')
ax1.axhline(0, color='gray', lw=0.5)
ax1.set_ylabel('Prawdopodobieństwo')
ax1.set_title(r'$\nu_e \to \nu_\mu$')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Panel 2: ν_e → ν_τ
ax2 = axes[1]
ax2.plot(L_vals, P_nu_etau,  label=r'$P(\nu_e \to \nu_\tau)$',        lw=2)
ax2.plot(L_vals, P_anu_etau, label=r'$P(\bar\nu_e \to \bar\nu_\tau)$', lw=2, ls='--')
ax2.plot(L_vals, DeltaP_tau, label=r'$\Delta P_{CP}$', color='black', lw=1.5, ls=':')
ax2.axhline(0, color='gray', lw=0.5)
ax2.set_xlabel('Dystans L [km]')
ax2.set_ylabel('Prawdopodobieństwo')
ax2.set_title(r'$\nu_e \to \nu_\tau$')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/adrian/Pulpit/Mummu/neutrinotime14_fixed.png', dpi=150, bbox_inches='tight')
plt.show()
print("Wykres zapisany: neutrinotime14_fixed.png")
