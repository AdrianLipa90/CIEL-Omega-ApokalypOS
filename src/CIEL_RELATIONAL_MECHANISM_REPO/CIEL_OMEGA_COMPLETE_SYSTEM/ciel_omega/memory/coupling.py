"""CIEL/Ω Memory Architecture - Coupling Matrix

Defines inter-channel coupling strengths J_kj that govern how memory
channels influence each other. Asymmetric by design: impact of relation
on identity differs from impact of identity on relation.

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

from __future__ import annotations

import numpy as np
from typing import Optional


# Coupling matrix J_kj: influence of channel j on channel k
# Rows = target (influenced), Columns = source (influencer)
# Order: M0, M1, M2, M3, M4, M5, M6, M7

COUPLING_MATRIX = np.array([
    # M0    M1    M2    M3    M4    M5    M6    M7
    [0.00, 0.45, 0.08, 0.05, 0.02, 0.25, 0.01, 0.00],  # M0 Perceptual
    [0.32, 0.00, 0.58, 0.35, 0.22, 0.62, 0.85, 0.12],  # M1 Working
    [0.18, 0.52, 0.00, 0.72, 0.18, 0.38, 0.42, 0.15],  # M2 Episodic
    [0.12, 0.28, 0.65, 0.00, 0.68, 0.45, 0.82, 0.35],  # M3 Semantic
    [0.05, 0.20, 0.15, 0.62, 0.00, 0.32, 0.58, 0.28],  # M4 Procedural
    [0.48, 0.55, 0.40, 0.48, 0.35, 0.00, 0.88, 0.45],  # M5 Affective/Ethical
    [0.08, 0.78, 0.38, 0.75, 0.52, 0.82, 0.00, 0.92],  # M6 Identity
    [0.02, 0.15, 0.12, 0.32, 0.25, 0.42, 0.88, 0.00],  # M7 Braid/Invariant
], dtype=np.float64)


# Channel name mapping
CHANNEL_NAMES = [
    "M0_Perceptual",
    "M1_Working", 
    "M2_Episodic",
    "M3_Semantic",
    "M4_Procedural",
    "M5_Affective_Ethical",
    "M6_Identity",
    "M7_Braid_Invariant"
]


class CouplingEngine:
    """Manages inter-channel coupling dynamics.
    
    Computes coupling forces between memory channels based on their
    phase states and coupling strengths.
    """
    
    def __init__(self, coupling_matrix: Optional[np.ndarray] = None):
        """Initialize with coupling matrix.
        
        Args:
            coupling_matrix: 8x8 array of coupling strengths, or None for default
        """
        self.J = coupling_matrix if coupling_matrix is not None else COUPLING_MATRIX
        self._validate_matrix()
        
    def _validate_matrix(self):
        """Validate coupling matrix structure"""
        assert self.J.shape == (8, 8), f"Coupling matrix must be 8x8, got {self.J.shape}"
        assert np.all(self.J >= 0), "Coupling strengths must be non-negative"
        assert np.all(self.J <= 1), "Coupling strengths must be <= 1"
        assert np.allclose(np.diag(self.J), 0), "Diagonal must be zero (no self-coupling)"
        
    def compute_coupling_force(self, 
                               target_channel: int,
                               target_phase: float,
                               source_phases: np.ndarray) -> float:
        """Compute total coupling force on target channel from all sources.
        
        F_coupling(k) = Σ_j J_kj * sin(γ_j - γ_k)
        
        Args:
            target_channel: Index of channel being influenced (0-7)
            target_phase: Current phase of target channel
            source_phases: Array of phases for all 8 channels
            
        Returns:
            Total coupling force on target channel
        """
        force = 0.0
        for j in range(8):
            if j == target_channel:
                continue
            coupling_strength = self.J[target_channel, j]
            phase_diff = source_phases[j] - target_phase
            force += coupling_strength * np.sin(phase_diff)
        return force
    
    def compute_all_coupling_forces(self, phases: np.ndarray) -> np.ndarray:
        """Compute coupling forces on all channels simultaneously.
        
        Args:
            phases: Array of 8 phase values
            
        Returns:
            Array of 8 coupling forces
        """
        forces = np.zeros(8)
        for k in range(8):
            forces[k] = self.compute_coupling_force(k, phases[k], phases)
        return forces
    
    def get_strongest_couplings(self, channel: int, top_n: int = 3) -> list[tuple[int, float]]:
        """Get strongest coupling connections for a channel.
        
        Args:
            channel: Channel index (0-7)
            top_n: Number of top connections to return
            
        Returns:
            List of (source_channel, strength) tuples
        """
        row = self.J[channel, :]
        indices = np.argsort(row)[::-1][:top_n]
        return [(int(idx), float(row[idx])) for idx in indices if row[idx] > 0]
    
    def analyze_coupling_hierarchy(self) -> dict:
        """Analyze coupling structure and identify key patterns.
        
        Returns:
            Dictionary with coupling analysis
        """
        analysis = {
            'total_coupling': np.sum(self.J),
            'mean_coupling': np.mean(self.J[self.J > 0]),
            'max_coupling': np.max(self.J),
            'strong_pairs': [],  # J > 0.7
            'medium_pairs': [],  # 0.4 < J < 0.7
            'weak_pairs': [],    # 0.1 < J < 0.4
        }
        
        for i in range(8):
            for j in range(8):
                if i == j:
                    continue
                strength = self.J[i, j]
                pair = (CHANNEL_NAMES[i], CHANNEL_NAMES[j], strength)
                
                if strength > 0.7:
                    analysis['strong_pairs'].append(pair)
                elif strength > 0.4:
                    analysis['medium_pairs'].append(pair)
                elif strength > 0.1:
                    analysis['weak_pairs'].append(pair)
        
        return analysis
    
    def compute_phase_shift_matrix(self,
                                   lambda_r: float = 0.35,
                                   lambda_tau: float = 0.45,
                                   sigma_r: float = 0.20,
                                   sigma_tau: float = 1.0,
                                   delta_max_pair: float = 0.18 * np.pi,
                                   role_amplitudes: Optional[np.ndarray] = None) -> np.ndarray:
        """Compute equilibrium phase shifts Δ^(0)_kj using hybrid formula.
        
        Δ^(0)_kj = clip[
            λ_r * (π/8) * tanh((r_k - r_j)/σ_r) +      # radial geometry
            λ_τ * (π/8) * tanh(log(τ_j/τ_k)/σ_τ) +     # time hierarchy
            s_kj * A^role_kj                            # role amplitude
        ]
        
        Convention: Δ^(0)_kj > 0 means channel j leads channel k in phase.
        
        Args:
            lambda_r: Radial geometry weight
            lambda_tau: Time hierarchy weight
            sigma_r: Radial scale
            sigma_tau: Time scale
            delta_max_pair: Maximum allowed shift between any pair
            role_amplitudes: 8x8 matrix of role-based amplitudes (optional)
            
        Returns:
            8x8 matrix of equilibrium phase shifts
        """
        from .base import CHANNEL_PARAMS
        
        # Extract channel parameters
        radii = np.array([CHANNEL_PARAMS[k].radius for k in range(8)])
        taus = np.array([CHANNEL_PARAMS[k].tau for k in range(8)])
        
        shifts = np.zeros((8, 8))
        
        for k in range(8):
            for j in range(8):
                if k == j:
                    continue
                
                # Component 1: Radial geometry
                # Outer channels (larger r) orbit faster, tend to lead inner channels
                r_diff = radii[k] - radii[j]
                delta_rad = lambda_r * (np.pi / 8) * np.tanh(r_diff / sigma_r)
                
                # Component 2: Time hierarchy
                # Faster channels (smaller τ) tend to lead slower channels
                if taus[j] > 0 and taus[k] > 0:
                    log_tau_ratio = np.log(taus[j] / taus[k])
                    delta_tau = lambda_tau * (np.pi / 8) * np.tanh(log_tau_ratio / sigma_tau)
                else:
                    delta_tau = 0.0
                
                # Component 3: Role amplitude with sign from geometry+time
                if role_amplitudes is not None:
                    # Sign: who should lead based on combined geometry+time
                    omega_r = 0.5  # Weight for radial component
                    omega_tau = 0.5  # Weight for time component
                    combined = omega_r * r_diff + omega_tau * log_tau_ratio
                    sign_kj = np.sign(combined) if abs(combined) > 1e-6 else 0.0
                    
                    delta_role = sign_kj * role_amplitudes[k, j]
                else:
                    delta_role = 0.0
                
                # Total shift
                total_shift = delta_rad + delta_tau + delta_role
                
                # Clip to maximum allowed
                shifts[k, j] = np.clip(total_shift, -delta_max_pair, delta_max_pair)
        
        return shifts
    
    def get_default_role_amplitudes(self) -> np.ndarray:
        """Get default role amplitude matrix A^role_kj for key pairs.
        
        Based on Adrian's specification for nominal mode.
        Most pairs have small or zero amplitude, only strategic pairs
        have significant values.
        
        Returns:
            8x8 matrix of role amplitudes [radians]
        """
        A = np.zeros((8, 8))
        
        # Very close co-phase (core coupling)
        A[6, 7] = A[7, 6] = 0.02 * np.pi  # M6 ↔ M7 (Identity ↔ Invariant)
        
        # Small core lags
        A[6, 5] = A[5, 6] = 0.04 * np.pi  # M6 ↔ M5 (Identity ↔ Affective) - nominal
        # Note: Alert mode would use 0.10-0.12π, but that's mode-dependent
        
        A[6, 3] = A[3, 6] = 0.05 * np.pi  # M6 ↔ M3 (Identity ↔ Semantic)
        A[6, 2] = A[2, 6] = 0.06 * np.pi  # M6 ↔ M2 (Identity ↔ Episodic)
        
        # Consolidation of meaning
        A[2, 3] = A[3, 2] = 0.10 * np.pi  # M2 ↔ M3 (Episodic ↔ Semantic)
        A[3, 4] = A[4, 3] = 0.08 * np.pi  # M3 ↔ M4 (Semantic ↔ Procedural)
        
        # Operational layer
        A[1, 2] = A[2, 1] = 0.12 * np.pi  # M1 ↔ M2 (Working ↔ Episodic)
        A[1, 5] = A[5, 1] = 0.10 * np.pi  # M1 ↔ M5 (Working ↔ Affective)
        A[0, 1] = A[1, 0] = 0.14 * np.pi  # M0 ↔ M1 (Perceptual ↔ Working)
        
        # Deep field trace
        A[5, 7] = A[7, 5] = 0.05 * np.pi  # M5 ↔ M7 (Affective ↔ Invariant)
        A[2, 7] = A[7, 2] = 0.04 * np.pi  # M2 ↔ M7 (Episodic ↔ Invariant)
        
        # All other pairs: small baseline
        # (Already initialized to zero, which is appropriate)
        
        return A


def print_coupling_summary():
    """Print human-readable summary of coupling structure"""
    engine = CouplingEngine()
    
    print("="*70)
    print("MEMORY COUPLING MATRIX SUMMARY")
    print("="*70)
    print()
    
    print("Key Coupling Strengths:")
    print("-"*70)
    
    # Identify strongest couplings
    strong_couplings = []
    for i in range(8):
        for j in range(8):
            if COUPLING_MATRIX[i, j] > 0.7:
                strong_couplings.append((
                    CHANNEL_NAMES[i],
                    CHANNEL_NAMES[j],
                    COUPLING_MATRIX[i, j]
                ))
    
    strong_couplings.sort(key=lambda x: x[2], reverse=True)
    
    for target, source, strength in strong_couplings[:10]:
        arrow = "←" 
        print(f"{target:25s} {arrow} {source:25s}: {strength:.2f}")
    
    print()
    print("Coupling Analysis:")
    print("-"*70)
    analysis = engine.analyze_coupling_hierarchy()
    print(f"Total coupling strength: {analysis['total_coupling']:.2f}")
    print(f"Mean coupling (non-zero): {analysis['mean_coupling']:.3f}")
    print(f"Maximum coupling: {analysis['max_coupling']:.2f}")
    print(f"Strong pairs (>0.7): {len(analysis['strong_pairs'])}")
    print(f"Medium pairs (0.4-0.7): {len(analysis['medium_pairs'])}")
    print(f"Weak pairs (0.1-0.4): {len(analysis['weak_pairs'])}")
    print()
    
    print("Per-Channel Influence:")
    print("-"*70)
    for k in range(8):
        top_sources = engine.get_strongest_couplings(k, top_n=3)
        sources_str = ", ".join([f"{CHANNEL_NAMES[s]} ({v:.2f})" for s, v in top_sources])
        print(f"{CHANNEL_NAMES[k]:25s}: {sources_str}")
    print()
    print("="*70)


__all__ = [
    'COUPLING_MATRIX',
    'CHANNEL_NAMES',
    'CouplingEngine',
    'print_coupling_summary',
]
