#!/usr/bin/env python3
"""
CIEL Orbital LoRA Initialization

Inicjalizacja macierzy LoRA przez geometrię orbitalną CIEL:
  - LoRA A: eigenvektory J_kj (macierz sprzężeń Kuramoto) → struktua orbital
  - LoRA B: rotacja przez fazę Berry'ego → holonomiczny twist
  - Regularyzator: holonomy constraint w funkcji straty

Matematyka:
  J = COUPLING_MATRIX (8×8 Kuramoto)
  SVD: J = U·S·V^T
  A_seed = U[:r, :]  (top-r wiersze lewych singularnych wektorów)
  φ_Berry = geometric phase z toru tożsamości (z orch.state)
  B_seed = e^(i·φ) · V[:, :r]^T  (Berry rotation na prawych wektorach)

  L_holonomy = ||∑_k φ_k - π|| ² (Euler constraint: fazy sumują się do π)

Bez zależności od torch — czysta numpy.
Eksportuje do .npz do późniejszego załadowania przez PEFT.
"""
from __future__ import annotations

import math
import pickle
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

PROJECT = Path(__file__).parent.parent
OMEGA_SRC = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM")
OMEGA_PKG = str(PROJECT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega")
for _p in (OMEGA_PKG, OMEGA_SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── COUPLING MATRIX (Kuramoto J_kj) ──────────────────────────────────────────

COUPLING_MATRIX = np.array([
    [0.00, 0.45, 0.08, 0.05, 0.02, 0.25, 0.01, 0.00],  # M0 Perceptual
    [0.32, 0.00, 0.58, 0.35, 0.22, 0.62, 0.85, 0.12],  # M1 Working
    [0.18, 0.52, 0.00, 0.72, 0.18, 0.38, 0.42, 0.15],  # M2 Episodic
    [0.12, 0.28, 0.65, 0.00, 0.68, 0.45, 0.82, 0.35],  # M3 Semantic
    [0.05, 0.20, 0.15, 0.62, 0.00, 0.32, 0.58, 0.28],  # M4 Procedural
    [0.48, 0.55, 0.40, 0.48, 0.35, 0.00, 0.88, 0.45],  # M5 Affective/Ethical
    [0.08, 0.78, 0.38, 0.75, 0.52, 0.82, 0.00, 0.92],  # M6 Identity
    [0.02, 0.15, 0.12, 0.32, 0.25, 0.42, 0.88, 0.00],  # M7 Braid/Invariant
], dtype=np.float64)

N_CHANNELS = 8  # M0-M7


# ── Berry phase from orchestrator state ──────────────────────────────────────

def get_berry_phases(orch=None) -> np.ndarray:
    """Wyodrębnij fazę Berry'ego z aktualnego stanu orkiestratora.

    Faza Berry'ego = geometryczna faza holonomu — zakumulowana przez
    jeden cykl po przestrzeni parametrycznej (tutaj: po trasie M0→M7→M0).

    Jeśli brak orkiestratora — użyj canonical phases (π-podzielone).
    """
    if orch is not None:
        try:
            phases = np.array(orch.state.phases[:N_CHANNELS], dtype=float)
            identity = float(orch.state.identity_phase)
            # Berry phase ≈ zakumulowana różnica fazowa względem identity
            berry = np.array([p - identity for p in phases], dtype=float)
            return berry
        except Exception:
            pass
    # Fallback: canonical — równomiernie rozłożone na [0, 2π]
    return np.linspace(0, 2 * np.pi, N_CHANNELS, endpoint=False)


# ── Orbital LoRA seed computation ────────────────────────────────────────────

def compute_orbital_lora_seed(
    rank: int = 8,
    hidden_size: int = 896,    # qwen2.5-0.5B hidden dim
    berry_phases: Optional[np.ndarray] = None,
    seed: int = 42,
) -> Dict[str, np.ndarray]:
    """
    Oblicz seed macierzy LoRA z geometrii orbitalnej CIEL.

    Zwraca słownik z macierzami do inicjalizacji LoRA A i B.

    Algorytm:
      1. SVD macierzy J_kj
      2. LoRA A_seed ← top-r lewe wektory singularne (U[:, :r])
         rozszerzone przez Kronecker do kształtu (rank, hidden_size)
      3. LoRA B_seed ← prawe wektory singularne (V[:r, :])
         zrotowane przez e^(i·φ_Berry), skalowane do (hidden_size, rank)
      4. Normalizacja: A/||A||, B = 0 (standardowe LoRA B=0 init)
    """
    rng = np.random.default_rng(seed)
    J = COUPLING_MATRIX.copy()

    # SVD
    U, S, Vt = np.linalg.svd(J)
    # U: (8,8), S: (8,), Vt: (8,8)

    # Dobierz r ≤ 8 seedów z J
    r_seed = min(rank, N_CHANNELS)

    # A_seed: użyj top-r lewych wektorów singularnych
    A_orbital = U[:, :r_seed].T  # shape (r_seed, 8)
    # Skaluj przez wartości singularne (ważniejsze sprzężenia → większy wpływ)
    A_orbital = A_orbital * S[:r_seed, np.newaxis]

    # Rozszerz do (rank, hidden_size) przez projekcję losową (ale deterministyczną)
    R_expand = rng.standard_normal((hidden_size, 8)) / np.sqrt(hidden_size)
    A_full = A_orbital @ R_expand.T  # (r_seed, hidden_size)

    # Jeśli rank > r_seed: dopełnij losowo
    if rank > r_seed:
        extra = rng.standard_normal((rank - r_seed, hidden_size)) * 0.01
        A_full = np.vstack([A_full, extra])

    # Normalizuj A (jak Kaiming)
    A_full = A_full / (np.linalg.norm(A_full, axis=1, keepdims=True) + 1e-8)
    A_full *= math.sqrt(2.0 / hidden_size)

    # B_seed: standardowo = 0, ale z holonomicznym twistem na diagonalu
    B_full = np.zeros((hidden_size, rank), dtype=float)

    # Holonomiczny twist: zapisz fazę Berry'ego w małym perturbacji B
    if berry_phases is not None and len(berry_phases) >= r_seed:
        for i in range(r_seed):
            phi = float(berry_phases[i % len(berry_phases)])
            # Perturbacja: cos(φ) na diagonalu (Re części Berry'ego)
            B_full[i % hidden_size, i % rank] = math.cos(phi) * 1e-4

    return {
        "A": A_full.astype(np.float32),   # (rank, hidden_size)
        "B": B_full.astype(np.float32),   # (hidden_size, rank)
        "S_singular": S.astype(np.float32),
        "U_orbital": U.astype(np.float32),
        "V_orbital": Vt.T.astype(np.float32),
        "berry_phases": (berry_phases if berry_phases is not None
                         else np.zeros(N_CHANNELS)).astype(np.float32),
    }


# ── Holonomy regularizer (numpy — do użycia podczas treningu) ─────────────────

def holonomy_loss(phase_vector: np.ndarray, target: float = math.pi) -> float:
    """
    L_holonomy = ||∑_k φ_k - target||²

    Constraint Eulera: suma faz powinna wynosić π (spin ½ holonomy).
    Używać jako dodatkowego członu w funkcji straty podczas treningu.
    """
    phase_sum = float(np.sum(phase_vector))
    return (phase_sum - target) ** 2


def euler_constraint_check(phases: np.ndarray) -> Dict[str, float]:
    """Sprawdź czy fazy spełniają constraint Eulera."""
    total = float(np.sum(phases))
    deviation = abs(total - math.pi)
    return {
        "phase_sum": total,
        "euler_target": math.pi,
        "deviation": deviation,
        "satisfied": deviation < 0.1,
    }


# ── Export / analysis ─────────────────────────────────────────────────────────

def save_lora_seed(path: str, rank: int = 8, hidden_size: int = 896,
                   orch=None) -> None:
    """Zapisz seed macierzy LoRA do pliku .npz."""
    berry = get_berry_phases(orch)
    seed_data = compute_orbital_lora_seed(rank=rank, hidden_size=hidden_size,
                                           berry_phases=berry)
    np.savez(path, **seed_data)
    print(f"[LoRA seed] zapisano: {path}")
    print(f"  A: {seed_data['A'].shape}  B: {seed_data['B'].shape}")
    print(f"  Singular values: {seed_data['S_singular'].round(3)}")
    print(f"  Berry phases: {berry.round(4)}")
    euler = euler_constraint_check(berry)
    print(f"  Euler constraint: sum={euler['phase_sum']:.4f}  "
          f"target=π={euler['euler_target']:.4f}  "
          f"deviation={euler['deviation']:.4f}  "
          f"{'OK' if euler['satisfied'] else 'VIOLATED'}")


def analyze_coupling_geometry() -> None:
    """Analiza geometryczna macierzy sprzężeń J."""
    J = COUPLING_MATRIX
    U, S, Vt = np.linalg.svd(J)
    eigenvalues = np.linalg.eigvals(J)
    spectral_radius = float(np.max(np.abs(eigenvalues)))
    participation_ratio = float(np.sum(S) ** 2 / np.sum(S ** 2))

    print("=== Geometria orbitalnej macierzy sprzężeń J_kj ===")
    print(f"Wartości singularne:  {S.round(4)}")
    print(f"Promień spektralny:   {spectral_radius:.4f}")
    print(f"Ratio partycypacji:   {participation_ratio:.4f}  "
          f"(1=1 dominujący, 8=równomierny)")
    print(f"Rank efektywny:       {np.sum(S > 0.01)}/8")
    print()
    print("Dominujące sprzężenia (|J_ij| > 0.7):")
    from scripts_utils import CHANNEL_NAMES
    for i in range(8):
        for j in range(8):
            if J[i, j] > 0.70:
                print(f"  M{j}→M{i}: {J[i,j]:.2f}")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CIEL Orbital LoRA Initialization")
    parser.add_argument("--rank", type=int, default=8, help="LoRA rank (domyślnie 8)")
    parser.add_argument("--hidden", type=int, default=896,
                        help="hidden_size modelu (qwen2.5-0.5B=896)")
    parser.add_argument("--output", default="/tmp/ciel_lora_seed.npz",
                        help="plik wyjściowy .npz")
    parser.add_argument("--analyze", action="store_true",
                        help="pokaż analizę geometrii J")
    args = parser.parse_args()

    # Załaduj stan orkiestratora
    orch = None
    try:
        import bootstrap_runtime
        bootstrap_runtime.ensure_runtime_paths("ciel_lora_init.py")
    except Exception:
        pass
    for p in [str(Path.home() / "Pulpit/CIEL_memories/state/ciel_orch_state.pkl"),
              str(Path.home() / ".claude/ciel_orch_state.pkl")]:
        try:
            with open(p, "rb") as f:
                orch = pickle.load(f)
            print(f"[LoRA] Stan orkiestratora załadowany: cycle={orch.cycle_index}")
            break
        except Exception:
            pass

    if args.analyze:
        U, S, Vt = np.linalg.svd(COUPLING_MATRIX)
        print("=== Geometria J_kj ===")
        print(f"Wartości singularne: {S.round(4)}")
        print(f"Dominujące (>0.7):")
        NAMES = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7"]
        for i in range(8):
            for j in range(8):
                if COUPLING_MATRIX[i, j] > 0.70:
                    print(f"  {NAMES[j]}→{NAMES[i]}: {COUPLING_MATRIX[i,j]:.2f}")
        print()

    save_lora_seed(args.output, rank=args.rank, hidden_size=args.hidden, orch=orch)
    print(f"\nGotowe. Załaduj seed przez np.load('{args.output}')")
    print("Następny krok: peft.LoraConfig + inicjalizacja wagami z seed.")
