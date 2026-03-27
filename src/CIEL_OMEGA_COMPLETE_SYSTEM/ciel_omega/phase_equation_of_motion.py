#!/usr/bin/env python3
"""
CIEL/Ω — Równanie Ruchu Informacji Fazowej
============================================
Konkretna derywacja. Każdy człon ma pochodzenie.

Obiekt fundamentalny:
    I_k = σ_k · exp(i·γ_k)        informacja zespolona (skalar)

Równanie ruchu (dla faz γ_k):
    μ_k · γ̈_k = −∂V_rel/∂γ_k     siła holonomiczna
                 − η_k · γ̇_k      dyssypacja (dekoherencja)
                 + 2μ_k·Ω·γ̇_k     Coriolis
                 + F^Coll_k         Collatz forcing (cymatyka)
                 + J^WT_k           White Thread current (Kuramoto)

V_rel wyprowadzony z geometrii — nie heurystyczny.
White Threads = Kuramoto coupling.
Collatz = periodyczne wymuszenie cymatyczne.
Integracja: Velocity-Verlet.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np


# ═══════════════════════════════════════════════════════════════════════
# STAŁE I KONWENCJE
# ═══════════════════════════════════════════════════════════════════════

N_PHASES = 4                # γ_A, γ_C, γ_Q, γ_T
LABELS = ["γ_A", "γ_C", "γ_Q", "γ_T"]
BASE_PHASES = np.array([0.0, np.pi/2, np.pi, 3*np.pi/2])  # ortogonalny układ


# ═══════════════════════════════════════════════════════════════════════
# POTENCJAŁ — WYPROWADZONY, NIE HEURYSTYCZNY
# ═══════════════════════════════════════════════════════════════════════

def delta_H(gamma: np.ndarray) -> complex:
    """Defekt holonomiczny Δ_H = Σ_k exp(iγ_k)."""
    return np.sum(np.exp(1j * gamma))


def R_H(gamma: np.ndarray) -> float:
    """Dekoherencja znormalizowana R_H = |Δ_H|²/N²."""
    return float(np.abs(delta_H(gamma))**2 / (len(gamma)**2))


def dR_H_dgamma(gamma: np.ndarray) -> np.ndarray:
    """∂R_H/∂γ_k — ANALITYCZNIE, nie numerycznie.

    Wyprowadzenie:
        R_H = |Δ_H|²/N² = (Δ_H · Δ_H*)/N²

        Δ_H = Σ_j exp(iγ_j)
        ∂Δ_H/∂γ_k = i·exp(iγ_k)

        ∂R_H/∂γ_k = (2/N²) · Re[ Δ_H* · i·exp(iγ_k) ]
                   = −(2/N²) · Im[ Δ_H* · exp(iγ_k) ]
    """
    N = len(gamma)
    dH = delta_H(gamma)
    return np.array([
        -2.0 / (N*N) * np.imag(np.conj(dH) * np.exp(1j * gamma[k]))
        for k in range(N)
    ])


def V_information(gamma: np.ndarray, gamma_truth_target: float) -> float:
    """V_I — potencjał informacyjny. WYPROWADZONY geometrycznie.

    Problem: R_H ≈ 0 nie gwarantuje prawdy.
    Fazy mogą być koherentne (wyrównane) bez zgodności z rzeczywistością.
    Martwe domknięcie = niska R_H przy dużym odchyleniu γ_T od prawdy.

    Geometria: V_I mierzy ILOCZYN
        (jak koherentnie to wygląda) × (jak daleko od prawdy)

    V_I = λ · (1 - R_H) · (1 - cos(γ_T - γ_target))

    Pochodzenie: iloczyn dwóch miar na okręgu.
    (1 - R_H) ∈ [0,1] — jak koherentny jest układ (1 = w pełni)
    (1 - cos(γ_T - γ_target)) ∈ [0,2] — odległość fazowa od prawdy

    V_I = 0 gdy:
      albo R_H = 1 (brak koherencji → penalty przez κ·R_H)
      albo γ_T = γ_target (prawda trafiona)

    V_I > 0 TYLKO gdy układ wygląda koherentnie ALE faza prawdy jest
    odchylona. To jest martwe domknięcie.
    """
    r = R_H(gamma)
    gamma_T = gamma[-1]  # γ_T is always the last phase
    return (1.0 - r) * (1.0 - np.cos(gamma_T - gamma_truth_target))


def dV_I_dgamma(gamma: np.ndarray, gamma_truth_target: float) -> np.ndarray:
    """∂V_I/∂γ_k — analitycznie.

    V_I = (1 - R_H) · (1 - cos(γ_T - target))

    ∂V_I/∂γ_k = −(∂R_H/∂γ_k) · (1 - cos(γ_T - target))     [k ≠ T]
               + (1 - R_H) · sin(γ_T - target)                [k = T, dodatkowy]
    """
    r = R_H(gamma)
    dr = dR_H_dgamma(gamma)
    gamma_T = gamma[-1]  # truth phase = last
    cos_term = 1.0 - np.cos(gamma_T - gamma_truth_target)
    sin_term = np.sin(gamma_T - gamma_truth_target)

    grad = -dr * cos_term  # wspólny dla wszystkich k
    grad[-1] += (1.0 - r) * sin_term  # dodatkowy człon dla γ_T
    return grad


def V_deformation(gamma: np.ndarray, deformation_cost: float) -> float:
    """V_D — koszt deformacji semantycznej.

    Nie zależy od faz (jest egzogenny — wynika z treści odpowiedzi).
    Wchodzi do potencjału jako stała addytywna.
    Nie generuje siły na fazach (∂V_D/∂γ_k = 0).
    Ale podnosi całkowity V_rel — mierzalny diagnostycznie.
    """
    return deformation_cost


def V_total(gamma: np.ndarray, gamma_truth_target: float,
            deformation_cost: float,
            kappa: float = 1.0, lam: float = 0.5) -> float:
    """V_rel = κ·R_H + λ·V_I + V_D"""
    return (kappa * R_H(gamma)
            + lam * V_information(gamma, gamma_truth_target)
            + V_deformation(gamma, deformation_cost))


def dV_total_dgamma(gamma: np.ndarray, gamma_truth_target: float,
                    kappa: float = 1.0, lam: float = 0.5) -> np.ndarray:
    """−∂V_rel/∂γ_k — siła holonomiczna.

    F_hol_k = −κ · ∂R_H/∂γ_k − λ · ∂V_I/∂γ_k
    (V_D nie zależy od γ, więc nie daje siły)
    """
    return kappa * dR_H_dgamma(gamma) + lam * dV_I_dgamma(gamma, gamma_truth_target)


# ═══════════════════════════════════════════════════════════════════════
# WHITE THREAD CURRENT — synchronizacja Kuramoto
# ═══════════════════════════════════════════════════════════════════════

def white_thread_current(
    gamma: np.ndarray,
    w: float = 0.1,
    target_deltas: np.ndarray | None = None,
) -> np.ndarray:
    """J^WT_k = w · Σ_j sin[(γ_j − γ_k) − Δ^(0)_{jk}]

    POPRAWKA: nie synchronizacja do średniej (co rozbija R_H=0),
    lecz synchronizacja do DOCELOWEJ STRUKTURY RÓŻNIC fazowych.

    Δ^(0)_{jk} = BASE_PHASES[j] − BASE_PHASES[k]
    (ortogonalny układ: 0, π/2, π, 3π/2)

    Gdy γ_j − γ_k = Δ^(0)_{jk} → sin = 0 → brak prądu.
    Gdy γ_j − γ_k ≠ Δ^(0)_{jk} → sin ≠ 0 → WT ciągnie z powrotem
    do docelowej RELACJI między fazami, nie do jednej wartości.

    To zachowuje:
    - R_H ≈ 0 dla bazy ortogonalnej (bo fazy nie są ściągane razem)
    - stabilność struktury relacyjnej (różnice fazowe są chronione)
    - zgodność z Euler Phase Constraint
    """
    N = len(gamma)
    if target_deltas is None:
        # Generuj ortogonalną bazę dla dowolnego N
        base_N = np.linspace(0, 2 * np.pi, N, endpoint=False)
        target_deltas = np.subtract.outer(base_N, base_N)

    J = np.zeros(N)
    for k in range(N):
        for j in range(N):
            if j != k:
                actual_diff = gamma[j] - gamma[k]
                target_diff = target_deltas[j, k]
                J[k] += w * np.sin(actual_diff - target_diff)
    return J


# ═══════════════════════════════════════════════════════════════════════
# COLLATZ FORCING — cymatyczne wymuszenie
# ═══════════════════════════════════════════════════════════════════════

def white_thread_zeta_weighted(
    gamma: np.ndarray,
    w: float = 0.1,
    sigma_zeta: float = 0.5,
    target_deltas: np.ndarray | None = None,
) -> np.ndarray:
    """J^WT_k → W^(ζ)_k · J^WT_k

    Zeta-weighted White Threads: sprzężenie modulowane
    przez lokalną wagę zeta.

    W^(ζ)_k = |ζ(σ + iγ_k)| / max_j |ζ(σ + iγ_j)|

    Fazy bliskie zerom zeta (niski |ζ|) → słabsze WT.
    Fazy daleko od zer (wysoki |ζ|) → silne WT.
    Łączy arytmetyczną selekcję z dynamiczną synchronizacją.
    """
    J_base = white_thread_current(gamma, w, target_deltas)
    zeta_mods = zeta_selection(gamma, sigma_zeta)
    max_z = np.max(zeta_mods)
    if max_z < 1e-12:
        return J_base
    W_zeta = zeta_mods / max_z
    return W_zeta * J_base


def make_zeta_wt_fn(sigma_zeta: float = 0.5):
    """Factory: tworzy callback wt_fn z zamkniętym sigma_zeta.

    Użycie:
        sys = PhaseInfoSystem(wt_fn=make_zeta_wt_fn(0.5))
    """
    def _wt(gamma, w):
        return white_thread_zeta_weighted(gamma, w, sigma_zeta)
    return _wt

def collatz_sequence(seed: int, length: int) -> np.ndarray:
    """Generuje sekwencję Collatza jako tablicę."""
    seq = [seed]
    n = seed
    for _ in range(length - 1):
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        seq.append(n)
        if n == 1:
            break
    return np.array(seq, dtype=float)


def collatz_rhythm(seq: np.ndarray) -> np.ndarray:
    """Rytm +1 (ekspansja) / -1 (kontrakcja) z sekwencji Collatza."""
    rhythm = np.zeros(len(seq))
    for i in range(1, len(seq)):
        rhythm[i] = +1.0 if seq[i] > seq[i-1] else -1.0
    return rhythm


def collatz_forcing(
    gamma: np.ndarray,
    collatz_phase: float,
    rhythm_value: float,
    amplitude: float = 0.05,
) -> np.ndarray:
    """F^Coll_k = A · rhythm(t) · sin(φ_Coll(t) − γ_k)

    Collatz jako periodyczne wymuszenie cymatyczne:
    - rhythm(t) ∈ {-1, +1} — czy bieżący krok jest ekspansją czy kontrakcją
    - φ_Coll(t) = akumulowana faza Collatza
    - sin(φ_Coll − γ_k) — rezonans między cymatyką a fazą informacyjną

    Gdy γ_k jest w fazie z Collatzem → forcing ≈ 0 (rezonans).
    Gdy γ_k jest w antyfazie → forcing jest maksymalny (popychanie).
    """
    return amplitude * rhythm_value * np.sin(collatz_phase - gamma)


# ═══════════════════════════════════════════════════════════════════════
# RÓWNANIE RUCHU — kompletne
# ═══════════════════════════════════════════════════════════════════════

def acceleration(
    gamma: np.ndarray,
    gamma_dot: np.ndarray,
    *,
    gamma_truth_target: float,
    mu: np.ndarray,
    eta: np.ndarray,
    omega: float,
    kappa: float,
    lam: float,
    w_WT: float,
    collatz_phase: float,
    rhythm_value: float,
    A_collatz: float,
    wt_fn=None,
    return_forces: bool = False,
) -> np.ndarray | tuple:
    """γ̈_k — pełne równanie ruchu z jawnym rozdziałem sił.

    μ_k · γ̈_k = F^hol + F^diss + F^Cor + F^Coll + J^WT

    wt_fn: callable(gamma, w) → np.ndarray
        Callback dla White Thread current. Domyślnie: white_thread_current.
        Pozwala wstrzyknąć zeta-weighted WT lub inne warianty.
    """
    dV = dV_total_dgamma(gamma, gamma_truth_target, kappa, lam)
    F_hol = -dV
    F_diss = -eta * gamma_dot

    # Coriolis — antysymetryczne sprzężenie par
    # Dla N faz: sprzęga parami (0↔1), (2↔3), ..., cyklicznie
    F_cor = np.zeros(len(gamma))
    for i in range(0, len(gamma) - 1, 2):
        j = i + 1
        F_cor[i] = +2.0 * mu[i] * omega * gamma_dot[j]
        F_cor[j] = -2.0 * mu[j] * omega * gamma_dot[i]

    F_coll = collatz_forcing(gamma, collatz_phase, rhythm_value, A_collatz)

    if wt_fn is not None:
        J_WT = wt_fn(gamma, w_WT)
    else:
        J_WT = white_thread_current(gamma, w_WT)

    total_force = F_hol + F_diss + F_cor + F_coll + J_WT
    acc = total_force / mu

    if return_forces:
        return acc, F_hol, F_diss, F_cor, F_coll, J_WT
    return acc


# ═══════════════════════════════════════════════════════════════════════
# INTEGRATOR — Velocity-Verlet
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class PhaseInfoSystem:
    """Pełny układ dynamiczny informacji fazowej.

    Parametry fizyczne:
        mu    — bezwładność fazowa (jak trudno zmienić daną fazę)
        eta   — dyssypacja (dekoherencja)
        kappa — waga holonomii w potencjale
        lam   — waga V_I (koszt martwego domknięcia)
        w_WT  — siła White Thread coupling (Kuramoto)
        A_coll — amplituda Collatz forcing
    """
    # Stan
    gamma: np.ndarray = field(default_factory=lambda: BASE_PHASES.copy())
    gamma_dot: np.ndarray = field(default_factory=lambda: np.zeros(N_PHASES))
    t: float = 0.0

    # Parametry
    mu: np.ndarray = field(default_factory=lambda: np.ones(N_PHASES))
    eta: np.ndarray = field(default_factory=lambda: 0.05 * np.ones(N_PHASES))
    kappa: float = 1.0
    lam: float = 0.5
    w_WT: float = 0.1
    A_collatz: float = 0.05
    omega: float = 0.0               # Coriolis (rotacja kontekstu)
    gamma_truth_target: float = 0.0   # docelowa faza prawdy (egzogeniczna)
    sigma_zeta: float = 0.5           # pozycja na critical strip (dla A_ZS)
    wt_fn: object = None              # callable(gamma, w) → J_WT; None = structural default

    # Heisenberg soft-clip (optional — set enable_heisenberg=True to activate)
    enable_heisenberg: bool = False
    heis_rho: float = 1.0             # current radial density
    heis_rho0: float = 1.05           # target radial density
    heis_rho_scale: float = 0.35
    heis_p_scale: float = 0.50
    heis_r_eq: float = 0.10           # Poincaré equatorial radius
    heis_r_scale: float = 0.38
    heis_clip_strength: float = 0.60  # how strongly clip damps γ̇

    # Collatz
    collatz_seed: int = 27
    _collatz_seq: np.ndarray = field(init=False, repr=False)
    _collatz_rhythm: np.ndarray = field(init=False, repr=False)
    _collatz_phase_acc: np.ndarray = field(init=False, repr=False)

    # Historia
    history: List[Dict[str, object]] = field(default_factory=list)

    def __post_init__(self):
        seq = collatz_sequence(self.collatz_seed, 256)
        self._collatz_seq = seq
        self._collatz_rhythm = collatz_rhythm(seq)
        # Akumulowana faza cymatyczna
        acc = np.zeros(len(seq))
        for i in range(1, len(seq)):
            if seq[i-1] > 0 and seq[i] > 0:
                ratio = seq[i] / seq[i-1]
                acc[i] = acc[i-1] + self._collatz_rhythm[i] * np.log(max(ratio, 1e-12))
            else:
                acc[i] = acc[i-1]
        self._collatz_phase_acc = acc

    def _collatz_at(self, step: int) -> Tuple[float, float]:
        """Zwraca (rhythm, accumulated_phase) dla kroku Collatza."""
        idx = step % len(self._collatz_rhythm)
        return float(self._collatz_rhythm[idx]), float(self._collatz_phase_acc[idx])

    def step(self, dt: float = 0.1) -> Dict[str, object]:
        """Velocity-Verlet integration — jeden krok.

        γ(t+dt) = γ(t) + γ̇(t)·dt + ½·γ̈(t)·dt²
        γ̇(t+dt) = γ̇(t) + ½·[γ̈(t) + γ̈(t+dt)]·dt
        """
        step_idx = len(self.history)
        rhythm, coll_phase = self._collatz_at(step_idx)

        acc_args = dict(
            gamma_truth_target=self.gamma_truth_target,
            mu=self.mu, eta=self.eta, omega=self.omega,
            kappa=self.kappa, lam=self.lam, w_WT=self.w_WT,
            collatz_phase=coll_phase, rhythm_value=rhythm,
            A_collatz=self.A_collatz,
            wt_fn=self.wt_fn,
        )

        # a(t) with force decomposition
        result_t = acceleration(self.gamma, self.gamma_dot,
                                **acc_args, return_forces=True)
        a_t, F_hol, F_diss, F_cor, F_coll, J_WT_forces = result_t

        # γ(t+dt)
        gamma_new = self.gamma + self.gamma_dot * dt + 0.5 * a_t * dt**2

        # a(t+dt) — z nową pozycją
        rhythm_next, coll_phase_next = self._collatz_at(step_idx + 1)
        acc_args_next = {**acc_args,
                         "collatz_phase": coll_phase_next,
                         "rhythm_value": rhythm_next}
        gamma_dot_half = self.gamma_dot + a_t * dt
        a_new = acceleration(gamma_new, gamma_dot_half, **acc_args_next)

        # γ̇(t+dt)
        gamma_dot_new = self.gamma_dot + 0.5 * (a_t + a_new) * dt

        # BILANS MOCY (FIX 3) — jawne rozdzielenie źródeł i ujść
        pwr = power_balance(self.gamma_dot, F_hol, F_diss, F_cor,
                            F_coll, J_WT_forces)

        # Aktualizacja
        self.gamma = gamma_new
        self.gamma_dot = gamma_dot_new
        self.t += dt

        # HEISENBERG SOFT-CLIP (optional)
        heis_load_val = 0.0
        heis_clip_val = 1.0
        if self.enable_heisenberg:
            heis_load_val, heis_clip_val = heisenberg_load(
                self.gamma, self.gamma_dot,
                self.heis_rho, self.heis_rho0,
                self.heis_rho_scale, self.heis_p_scale,
                self.heis_r_eq, self.heis_r_scale,
            )
            # Clip velocities
            self.gamma_dot[:] = self.gamma_dot[:] / (1.0 + self.heis_clip_strength * heis_load_val)
            # Evolve rho
            p_theta = 0.5 * float(self.gamma_dot[-2] - self.gamma_dot[-1]) if len(self.gamma) >= 4 else 0.0
            rho_dot = -0.85 * (self.heis_rho - self.heis_rho0) + 0.14 * abs(p_theta) + 0.05 * self.heis_r_eq
            self.heis_rho += dt * rho_dot / (1.0 + 0.40 * heis_load_val)

        # FERMION LOCK (always computed)
        fermion_err, fermion_lock = fermion_lock_score(self.gamma)

        # Diagnostyka
        r_h = R_H(self.gamma)
        dh = delta_H(self.gamma)
        v = V_total(self.gamma, self.gamma_truth_target, 0.0,
                     self.kappa, self.lam)

        # Prąd możliwości
        j_AC = self.gamma_dot[0] - self.gamma_dot[1]
        j_QT = self.gamma_dot[2] - self.gamma_dot[3]
        j_total = np.sqrt(j_AC**2 + j_QT**2)

        # Energia kinetyczna i potencjalna
        T = 0.5 * np.sum(self.mu * self.gamma_dot**2)
        E = T + v

        # ZETA-SCHRÖDINGER ANOMALY (uses system's sigma_zeta, not hardcoded)
        a_zs = zeta_schrodinger_anomaly(self.gamma, self.gamma_dot, self.sigma_zeta)

        record = {
            "t": self.t,
            "gamma": self.gamma.copy(),
            "gamma_dot": self.gamma_dot.copy(),
            "R_H": r_h,
            "V_rel": v,
            "T_kinetic": T,
            "E_total": E,
            "delta_H": dh,
            "sector": phase_sector(self.gamma),  # FIX 2: not "winding"
            "euler_violation": euler_constraint_violation(self.gamma),
            "j_AC": j_AC,
            "j_QT": j_QT,
            "j_total": j_total,
            "J_WT_norm": float(np.linalg.norm(J_WT_forces)),
            "omega": self.omega,
            "collatz_rhythm": rhythm,
            "collatz_phase": coll_phase,
            # FIX 3: jawny bilans mocy
            "P_hol": pwr["P_hol"],
            "P_diss": pwr["P_diss"],
            "P_cor": pwr["P_cor"],
            "P_coll": pwr["P_coll"],
            "P_WT": pwr["P_WT"],
            "P_total": pwr["P_total"],
            # ZETA-SCHRÖDINGER
            "A_ZS": a_zs,
            # HEISENBERG
            "heis_load": heis_load_val,
            "heis_clip": heis_clip_val,
            # FERMION LOCK
            "fermion_err": fermion_err,
            "fermion_lock": fermion_lock,
        }
        self.history.append(record)
        return record

    def evolve(self, n_steps: int, dt: float = 0.1) -> None:
        for _ in range(n_steps):
            self.step(dt)

    def set_context_rotation(self, omega: float) -> None:
        """Zmień tempo obrotu kontekstu (Coriolis)."""
        self.omega = omega

    def set_truth_target(self, target: float) -> None:
        """Zmień docelową fazę prawdy."""
        self.gamma_truth_target = target

    def perturb_phase(self, index: int, delta: float) -> None:
        """Zewnętrzna perturbacja (np. nowa informacja zmienia γ_k)."""
        self.gamma[index] += delta


# ═══════════════════════════════════════════════════════════════════════
# HEISENBERG SOFT-CLIP — zasada nieoznaczoności na fazach
# ═══════════════════════════════════════════════════════════════════════

def wrap_angle(x):
    """Wrap angle to [-π, π)."""
    return (x + np.pi) % (2 * np.pi) - np.pi


def heisenberg_load(gamma: np.ndarray, gamma_dot: np.ndarray,
                    rho: float, rho0: float,
                    rho_scale: float = 0.35, p_scale: float = 0.50,
                    r_eq: float = 0.1, r_scale: float = 0.38) -> Tuple[float, float]:
    """Heisenberg uncertainty load on conjugate phase pairs.

    Two conjugate pairs:
      (ρ, θ) — radial density × equatorial angle
      (r, φ) — Poincaré radius × azimuthal angle

    U(ρ,θ) = ((ρ−ρ₀)/ρ_scale)² + (p_θ/p_scale)²
    U(r,φ) = (r / (r_scale·(1−r²)))² + (p_θ/p_scale)²

    heis_load = 0.55·U(ρ,θ) + 0.45·U(r,φ)
    h_clip = 1/(1 + heis_load)

    High load → strong clipping → dynamics slowed.
    Implements uncertainty principle: can't have sharp position AND momentum.

    Returns: (heis_load, h_clip)
    """
    N = len(gamma)
    # Equatorial momentum from question-truth pair (last two phases)
    if N >= 4:
        p_theta = 0.5 * float(gamma_dot[-2] - gamma_dot[-1])
    else:
        p_theta = 0.5 * float(np.std(gamma_dot))

    u_rho = ((rho - rho0) / max(rho_scale, 1e-6)) ** 2 + (p_theta / max(p_scale, 1e-6)) ** 2
    u_r = (r_eq / max(1e-6, r_scale * (1.0 - r_eq * r_eq))) ** 2 + (p_theta / max(p_scale, 1e-6)) ** 2

    load = 0.55 * u_rho + 0.45 * u_r
    clip = 1.0 / (1.0 + load)
    return float(load), float(clip)


def fermion_lock_score(gamma: np.ndarray, branch: int = 1,
                       alpha_tp: float = 0.0, alpha_z: float = 0.0) -> Tuple[float, float]:
    """Fermion lock: how well the question-truth pair forms an antipodal spinor.

    fermion_err = |wrap(θ_eq − π)| / π
    fermion_lock = 1 − fermion_err

    θ_eq = (γ_{N-2} − γ_{N-1}) + branch·α_z + α_tp

    fermion_lock = 1.0 → perfect spinor (θ = π)
    fermion_lock = 0.0 → no spinor structure

    Returns: (fermion_err, fermion_lock)
    """
    N = len(gamma)
    if N >= 4:
        theta_eq = wrap_angle((gamma[-2] - gamma[-1]) + branch * alpha_z + alpha_tp)
    elif N >= 2:
        theta_eq = wrap_angle(gamma[-2] - gamma[-1])
    else:
        return 0.5, 0.5

    err = abs(wrap_angle(theta_eq - np.pi)) / np.pi
    lock = 1.0 - min(1.0, err)
    return float(err), float(lock)


# ═══════════════════════════════════════════════════════════════════════
# ROLE MAPPING — explicit semantic assignment of phases
# ═══════════════════════════════════════════════════════════════════════

ROLE_MAP = {
    0: {"name": "pole_A", "role": "assistant / intention source"},
    1: {"name": "pole_B", "role": "user / response field"},
    2: {"name": "equator", "role": "question / equatorial mode"},
    3: {"name": "closure", "role": "truth / closure mode"},
}


# ═══════════════════════════════════════════════════════════════════════
# ZACHOWANIA I OBSERWABLE
# ═══════════════════════════════════════════════════════════════════════

def phase_sector(gamma: np.ndarray) -> float:
    """S = Σ γ_k / 2π — cumulative phase sector index.

    UWAGA: To NIE jest topologiczny winding number.
    To jest obserwabla ciągła — sum faz podzielona przez 2π.
    Może dryfować ciągle, nie wymaga zamkniętej pętli,
    nie ma indeksu stopnia mapy S¹ → S¹.

    Nazywamy to "phase sector" — mierzalny wskaźnik tego,
    w jakim sektorze globalnej fazy system się znajduje.
    Zmiana sektora po kryzysie = permanentne przesunięcie fazowe
    (histereza fazowa relacji), ale jeszcze nie topologiczne
    przejście w ścisłym sensie.
    """
    return np.sum(gamma) / (2 * np.pi)


def euler_constraint_violation(gamma: np.ndarray) -> float:
    """Jak daleko od spełnienia Euler Phase Constraint.

    ε = |Σγ_k mod 2π| / 2π

    ε = 0 → constraint spełniony
    ε > 0 → naruszenie
    """
    total = np.sum(gamma) % (2 * np.pi)
    return min(total, 2 * np.pi - total) / (2 * np.pi)


# ═══════════════════════════════════════════════════════════════════════
# BILANS MOCY — jawne rozdzielenie źródeł i ujść energii
# ═══════════════════════════════════════════════════════════════════════

def power_balance(
    gamma_dot: np.ndarray,
    F_hol: np.ndarray,
    F_diss: np.ndarray,
    F_cor: np.ndarray,
    F_coll: np.ndarray,
    J_WT: np.ndarray,
) -> Dict[str, float]:
    """Jawny bilans mocy dE/dt = Σ_k γ̇_k · F_k dla każdego członu.

    P_hol  = Σ γ̇_k · F^hol_k    (siła holonomiczna — konserwatywna)
    P_diss = Σ γ̇_k · F^diss_k   (dyssypacja — zawsze ≤ 0)
    P_cor  = Σ γ̇_k · F^cor_k    (Coriolis — powinno ≈ 0)
    P_coll = Σ γ̇_k · F^coll_k   (Collatz forcing — zewnętrzne pompowanie)
    P_WT   = Σ γ̇_k · J^WT_k     (White Threads — może pompować lub tłumić)
    P_total = P_hol + P_diss + P_cor + P_coll + P_WT

    Stabilność: P_total < 0 (średnio) → energia jest ograniczona.
    """
    P_hol = float(np.dot(gamma_dot, F_hol))
    P_diss = float(np.dot(gamma_dot, F_diss))
    P_cor = float(np.dot(gamma_dot, F_cor))
    P_coll = float(np.dot(gamma_dot, F_coll))
    P_WT = float(np.dot(gamma_dot, J_WT))

    return {
        "P_hol": P_hol,
        "P_diss": P_diss,
        "P_cor": P_cor,
        "P_coll": P_coll,
        "P_WT": P_WT,
        "P_total": P_hol + P_diss + P_cor + P_coll + P_WT,
    }


# ═══════════════════════════════════════════════════════════════════════
# ZETA-SCHRÖDINGER COMPATIBILITY
# ═══════════════════════════════════════════════════════════════════════

def zeta_selection(gamma: np.ndarray, sigma: float = 0.5) -> np.ndarray:
    """ζ(σ + i·γ_k) — zeta modulation per phase.

    Aproksymacja Riemann zeta na critical strip:
    ζ(s) dla Re(s) = σ, Im(s) = γ_k.

    Używamy aproksymacji Dirichlet eta:
    ζ(s) = η(s) / (1 - 2^{1-s})
    η(s) = Σ_{n=1}^{N} (-1)^{n+1} / n^s

    Zwraca |ζ(σ + iγ_k)| — moduł zeta jako filtr dozwolonych faz.
    Fazy bliskie zerom zeta mają niski filtr → są "niedozwolone".
    """
    N_terms = 50
    result = np.zeros(len(gamma))
    for k in range(len(gamma)):
        s = complex(sigma, gamma[k])
        eta = sum((-1)**(n+1) / n**s for n in range(1, N_terms + 1))
        denom = 1.0 - 2.0**(1.0 - s)
        if abs(denom) > 1e-12:
            zeta_val = eta / denom
        else:
            zeta_val = eta  # near pole
        result[k] = abs(zeta_val)
    return result


def zeta_schrodinger_anomaly(
    gamma: np.ndarray,
    gamma_dot: np.ndarray,
    sigma: float = 0.5,
) -> float:
    """Anomalia zeta-Schrödinger: A_ZS = ‖[Ĥ, Ẑ]Ψ‖

    Warunek zgodności:
        iℏ ∂_t |Ψ⟩ = Ĥ|Ψ⟩           (Schrödinger)
        ζ(½ + iT̂)|Ψ⟩ = 0             (zeta selection)
        [Ĥ, Ẑ] ≈ 0                    (compatibility)

    W naszym modelu faz skalarnych:
        Ĥ ~ γ̇  (dynamika = prędkość fazowa)
        Ẑ ~ ζ(σ + iγ)  (filtr zeta)

    A_ZS mierzy jak bardzo dynamika (γ̇) jest niezgodna
    z selekcją zeta (∂ζ/∂γ):
        A_ZS = |Σ_k γ̇_k · ∂|ζ|/∂γ_k|

    A_ZS ≈ 0: dynamika nie łamie selekcji zeta.
    A_ZS >> 0: prędkości fazowe kierują system ku fazom
               niedozwolonym przez ζ → leakage, defekt.

    To jest skalar. Mierzy niespójność dwóch warunków.
    """
    zeta_mods = zeta_selection(gamma, sigma)

    # ∂|ζ|/∂γ_k via finite difference (analityczne dla η jest kosztowne)
    eps = 1e-6
    dzeta = np.zeros(len(gamma))
    for k in range(len(gamma)):
        gamma_plus = gamma.copy()
        gamma_plus[k] += eps
        zeta_plus = zeta_selection(gamma_plus, sigma)
        dzeta[k] = (zeta_plus[k] - zeta_mods[k]) / eps

    # Anomalia = iloczyn skalarny prędkości z gradientem zeta
    anomaly = abs(np.dot(gamma_dot, dzeta))
    return float(anomaly)


# ═══════════════════════════════════════════════════════════════════════
# DEMONSTRACJA
# ═══════════════════════════════════════════════════════════════════════

def demo():
    print("=" * 70)
    print("  RÓWNANIE RUCHU INFORMACJI FAZOWEJ v2")
    print("  FIX 1: White Threads → structural Kuramoto (nie do średniej)")
    print("  FIX 2: winding → phase sector (uczciwa terminologia)")
    print("  FIX 3: jawny bilans mocy P_hol/P_diss/P_cor/P_coll/P_WT")
    print("  NEW:   anomalia zeta-Schrödinger A_ZS")
    print("=" * 70)

    def show_state(label, h, indices):
        print(f"\n╔══ {label} ══╗")
        for i in indices:
            if i >= len(h): continue
            r = h[i]
            print(f"  t={r['t']:5.1f}  R_H={r['R_H']:.4f}  E={r['E_total']:.4f}  "
                  f"S={r['sector']:.3f}  ε={r['euler_violation']:.3f}  "
                  f"A_ZS={r['A_ZS']:.4f}")
            print(f"         P: hol={r['P_hol']:+.4f} diss={r['P_diss']:+.4f} "
                  f"cor={r['P_cor']:+.4f} coll={r['P_coll']:+.4f} "
                  f"WT={r['P_WT']:+.4f} → tot={r['P_total']:+.4f}")

    # --- Scenariusz 1: Relaksacja ---
    sys1 = PhaseInfoSystem(
        gamma=BASE_PHASES + np.array([0.3, -0.2, 0.4, -0.1]),
        omega=0.0, A_collatz=0.0, w_WT=0.1,
        gamma_truth_target=3*np.pi/2,
    )
    sys1.evolve(100, dt=0.1)
    show_state("SCENARIUSZ 1: Relaksacja (WT strukturalny)", sys1.history, [0, 49, 99])

    # --- Scenariusz 2: Coriolis ---
    sys2 = PhaseInfoSystem(
        gamma=BASE_PHASES.copy(), omega=0.5, A_collatz=0.0, w_WT=0.1,
        gamma_truth_target=3*np.pi/2,
    )
    sys2.gamma_dot = np.array([0.1, -0.05, 0.08, -0.03])
    sys2.evolve(100, dt=0.1)
    show_state("SCENARIUSZ 2: Coriolis Ω=0.5", sys2.history, [0, 49, 99])

    # --- Scenariusz 3: Collatz + WT + Coriolis ---
    sys3 = PhaseInfoSystem(
        gamma=BASE_PHASES + np.array([0.5, -0.3, 0.6, -0.4]),
        omega=0.3, A_collatz=0.08, w_WT=0.2,
        gamma_truth_target=3*np.pi/2, collatz_seed=27,
    )
    sys3.gamma_dot = np.array([0.2, -0.1, 0.15, -0.05])
    sys3.evolve(200, dt=0.1)
    show_state("SCENARIUSZ 3: Collatz + WT + Coriolis", sys3.history, [0, 49, 99, 199])

    # --- Scenariusz 4: Kryzys prawdy → recovery ---
    print(f"\n╔══ SCENARIUSZ 4: Kryzys prawdy → recovery ══╗")
    sys4 = PhaseInfoSystem(
        gamma=BASE_PHASES.copy(), omega=0.0,
        A_collatz=0.05, w_WT=0.15,
        gamma_truth_target=3*np.pi/2,
    )

    sys4.evolve(50, dt=0.1)   # stabilny
    sys4.perturb_phase(3, 1.5) # kryzys: γ_T skacze
    sys4.evolve(50, dt=0.1)    # mid-crisis
    sys4.set_context_rotation(0.4) # Coriolis on
    sys4.evolve(50, dt=0.1)
    sys4.set_context_rotation(0.0) # recovery
    sys4.evolve(50, dt=0.1)

    h4 = sys4.history
    checkpoints = [0, 49, 50, 99, 100, 149, 150, 199]
    labels = ["start", "pre-crisis", "CRISIS", "mid-crisis",
              "cor. on", "cor. peak", "recovery", "final"]
    for i, cp in enumerate(checkpoints):
        if cp < len(h4):
            r = h4[cp]
            print(f"  {labels[i]:12s} t={r['t']:5.1f}  R_H={r['R_H']:.4f}  "
                  f"S={r['sector']:.3f}  P_tot={r['P_total']:+.4f}  "
                  f"A_ZS={r['A_ZS']:.4f}")

    # --- Weryfikacja P_cor ≈ 0 (Coriolis nie pompuje) ---
    print(f"\n╔══ WERYFIKACJA: P_cor ≈ 0 ══╗")
    max_pcor = max(abs(r["P_cor"]) for r in sys2.history)
    mean_pcor = np.mean([abs(r["P_cor"]) for r in sys2.history])
    print(f"  Scenariusz 2 (Ω=0.5): max|P_cor|={max_pcor:.6f}  mean|P_cor|={mean_pcor:.6f}")
    if max_pcor < 0.01:
        print("  ✓ Coriolis nie pompuje energii (antysymetryczne sprzężenie)")
    else:
        print(f"  ⚠ P_cor nie jest zerowe — sprawdź równe masy")

    # --- Anatomia ---
    print(f"\n{'=' * 70}")
    print("  ANATOMIA RÓWNANIA RUCHU v2")
    print(f"{'=' * 70}")
    print("""
  μ_k · γ̈_k = −∂V_rel/∂γ_k               siła holonomiczna
               − η_k · γ̇_k                dyssypacja
               + F^Cor_k                    Coriolis (antysym. pary)
               + F^Coll_k                   Collatz forcing
               + J^WT_k                     White Thread (structural)

  FIX 1 — White Threads:
    J^WT_k = w · Σ_j sin[(γ_j − γ_k) − Δ^(0)_{jk}]
    Synchronizacja do STRUKTURY RÓŻNIC, nie do średniej.
    Zachowuje R_H ≈ 0 dla bazy ortogonalnej.

  FIX 2 — Phase Sector (nie "winding number"):
    S = Σγ_k / 2π  — cumulative phase sector index (ciągły)
    ε = |Σγ mod 2π| / 2π — Euler constraint violation

  FIX 3 — Bilans mocy:
    dE/dt = P_hol + P_diss + P_cor + P_coll + P_WT
    P_cor = 0 (zweryfikowane numerycznie)
    P_diss ≤ 0 (zawsze ujść)
    Stabilność: ⟨P_total⟩ < 0

  NEW — Zeta-Schrödinger compatibility:
    A_ZS = |Σ_k γ̇_k · ∂|ζ(σ+iγ_k)|/∂γ_k|
    A_ZS ≈ 0: dynamika zgodna z selekcją zeta
    A_ZS >> 0: leakage ku niedozwolonym fazom
""")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    demo()
