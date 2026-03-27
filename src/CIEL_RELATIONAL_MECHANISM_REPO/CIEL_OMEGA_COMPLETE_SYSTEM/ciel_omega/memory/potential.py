"""CIEL/Ω Memory Architecture - Memory Potentials

Defines potential energy landscape that governs memory dynamics.
Memories evolve to minimize total potential: alignment with identity,
conflict between channels, drift from anchors, and noise.

V_mem = V_align + V_conflict + V_drift + V_noise

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

from __future__ import annotations

import numpy as np
from typing import Optional
from .base import CHANNEL_PARAMS, IdentityField


class MemoryPotential:
    """Computes potential energy components for memory system.
    
    The total potential governs how memory channels evolve. Lower potential
    corresponds to more stable, coherent memory configurations.
    """
    
    def __init__(self, identity_field: Optional[IdentityField] = None):
        """Initialize potential calculator.
        
        Args:
            identity_field: Central identity attractor, or None to create default
        """
        self.identity = identity_field or IdentityField()
        
        # Load channel-specific alignment costs
        self.alpha = np.array([
            CHANNEL_PARAMS[k].alignment_cost for k in range(8)
        ])
        
        # Conflict coupling strengths - SYMMETRIC β from asymmetric J
        # β_kj = sqrt(J_kj * J_jk) to ensure potential is scalar
        from .coupling import COUPLING_MATRIX
        J = COUPLING_MATRIX
        self.beta = np.zeros((8, 8))
        for k in range(8):
            for j in range(8):
                if k != j:
                    # Geometric mean of asymmetric couplings
                    self.beta[k, j] = np.sqrt(J[k, j] * J[j, k])
                    # Optional: weight by coupling strengths to identity
                    coupling_k = CHANNEL_PARAMS[k].coupling_strength
                    coupling_j = CHANNEL_PARAMS[j].coupling_strength
                    self.beta[k, j] *= (coupling_k + coupling_j) / 2.0
        
        # Drift penalties (HIGHER for stable/slow channels)
        # Use sqrt(τ) for reasonable scaling - not too weak, not explosive
        self.chi = np.array([
            np.sqrt(CHANNEL_PARAMS[k].tau) for k in range(8)
        ])
        
        # Noise penalties (higher for fast channels)
        self.nu = np.array([
            CHANNEL_PARAMS[k].tau for k in range(8)
        ])
        
        # EBA constraint strength
        self.lambda_eba = 1.0  # Can be tuned
        
    def compute_alignment_potential(self, phases: np.ndarray) -> float:
        """Compute V_align: cost of misalignment with identity.
        
        V_align = Σ_k α_k (1 - cos(γ_k - γ_I))
        
        This is lowest when all channels align with identity phase,
        highest when they oppose it.
        
        Args:
            phases: Array of 8 channel phases
            
        Returns:
            Alignment potential energy
        """
        identity_phase = self.identity.phase
        phase_diffs = phases - identity_phase
        costs = self.alpha * (1.0 - np.cos(phase_diffs))
        return np.sum(costs)
    
    def compute_conflict_potential(self, 
                                  phases: np.ndarray,
                                  equilibrium_shifts: Optional[np.ndarray] = None) -> float:
        """Compute V_conflict: cost of channel misalignment.
        
        V_conflict = Σ_{k<j} β_kj (1 - cos(γ_k - γ_j - Δ^(0)_kj))
        
        Channels don't need identical phases, but should maintain
        stable relative phase shifts Δ^(0)_kj based on their radii.
        
        Args:
            phases: Array of 8 channel phases
            equilibrium_shifts: Optional 8x8 matrix of equilibrium shifts
            
        Returns:
            Conflict potential energy
        """
        if equilibrium_shifts is None:
            # Use zero shifts if not provided
            equilibrium_shifts = np.zeros((8, 8))
        
        potential = 0.0
        for k in range(8):
            for j in range(k + 1, 8):  # k < j to avoid double counting
                phase_diff = phases[k] - phases[j] - equilibrium_shifts[k, j]
                cost = self.beta[k, j] * (1.0 - np.cos(phase_diff))
                potential += cost
        
        return potential
    
    def compute_drift_potential(self, 
                               phases: np.ndarray,
                               anchor_phases: np.ndarray) -> float:
        """Compute V_drift: cost of drifting from anchored positions.
        
        V_drift = Σ_k χ_k (γ_k - γ_k^anchor)²
        
        This quadratic term penalizes large deviations from historically
        stable positions, with penalty stronger for stable channels.
        
        Args:
            phases: Current channel phases
            anchor_phases: Anchored reference phases
            
        Returns:
            Drift potential energy
        """
        drifts = phases - anchor_phases
        # Wrap to [-π, π] for shortest path
        drifts = np.arctan2(np.sin(drifts), np.cos(drifts))
        costs = self.chi * drifts**2
        return np.sum(costs)
    
    def compute_noise_potential(self, velocities: np.ndarray) -> float:
        """Compute V_noise: cost of rapid fluctuations.
        
        V_noise = Σ_k ν_k (dγ_k/dt)²
        
        This penalizes excessive velocity, preventing instability.
        Penalty is higher for slow channels that should not fluctuate.
        
        Args:
            velocities: Array of 8 phase velocities
            
        Returns:
            Noise potential energy
        """
        costs = self.nu * velocities**2
        return np.sum(costs)
    
    def compute_eba_potential(self,
                             memory_loop: Optional['MemoryLoop'] = None,
                             epsilon_eba: Optional[float] = None) -> float:
        """Compute V_EBA: cost of EBA condition violation.
        
        V_EBA = λ_EBA * (1 - cos(ε_EBA))
        
        This enforces topological closure of memory loops.
        Low when loop closes properly (ε_EBA ≈ 0),
        high when there's geometric/topological defect.
        
        Args:
            memory_loop: Complete loop to analyze (if provided)
            epsilon_eba: Pre-computed EBA defect (alternative to loop)
            
        Returns:
            EBA potential energy
        """
        if epsilon_eba is not None:
            # Use provided defect value
            defect = epsilon_eba
        elif memory_loop is not None:
            # Compute from loop
            from .holonomy import HolonomyCalculator
            calc = HolonomyCalculator(self.beta)
            result = calc.compute_eba_defect(memory_loop)
            defect = result['epsilon_eba']
        else:
            # No loop information - return zero
            return 0.0
        
        # Potential from defect
        V_eba = self.lambda_eba * (1.0 - np.cos(defect))
        
        return V_eba
    
    def compute_static_potential(self,
                                phases: np.ndarray,
                                anchor_phases: np.ndarray,
                                equilibrium_shifts: Optional[np.ndarray] = None) -> dict:
        """Compute static potential V_static (generates forces).
        
        V_static = V_align + V_conflict + V_drift
        
        This is the actual potential whose gradient drives dynamics.
        
        Args:
            phases: Current channel phases
            anchor_phases: Reference anchor phases
            equilibrium_shifts: Equilibrium phase shifts between channels
            
        Returns:
            Dictionary with static potential components
        """
        V_align = self.compute_alignment_potential(phases)
        V_conflict = self.compute_conflict_potential(phases, equilibrium_shifts)
        V_drift = self.compute_drift_potential(phases, anchor_phases)
        
        V_static = V_align + V_conflict + V_drift
        
        return {
            'V_align': V_align,
            'V_conflict': V_conflict,
            'V_drift': V_drift,
            'V_static': V_static,
            'components': {
                'alignment': V_align / (V_static + 1e-10),
                'conflict': V_conflict / (V_static + 1e-10),
                'drift': V_drift / (V_static + 1e-10),
            }
        }
    
    def compute_dissipation_functional(self, velocities: np.ndarray) -> float:
        """Compute dissipation functional R_noise.
        
        R_noise = (1/2) * Σ_k ξ_k * (dγ_k/dt)²
        
        This is NOT a potential - it's a dissipation functional.
        It affects dynamics through damping, not through gradient forces.
        
        Args:
            velocities: Phase velocities dγ/dt
            
        Returns:
            Dissipation functional value
        """
        # ξ_k = ν_k (noise penalty coefficients)
        R_noise = 0.5 * np.sum(self.nu * velocities**2)
        return R_noise
    
    def compute_monitored_energy(self,
                                phases: np.ndarray,
                                anchor_phases: np.ndarray,
                                velocities: np.ndarray,
                                equilibrium_shifts: Optional[np.ndarray] = None,
                                memory_loop: Optional['MemoryLoop'] = None,
                                include_eba: bool = False) -> dict:
        """Compute monitored energy for diagnostics and reporting.
        
        E_monitor = V_static + R_noise + V_EBA_diag
        
        Where:
        - V_static: actual potential generating forces
        - R_noise: dissipation functional (not a potential)
        - V_EBA_diag: topological diagnostic (not in dynamics yet)
        
        Args:
            phases: Current channel phases
            anchor_phases: Reference anchor phases
            velocities: Current phase velocities
            equilibrium_shifts: Equilibrium phase shifts
            memory_loop: Optional loop for EBA calculation
            include_eba: Whether to include EBA diagnostic
            
        Returns:
            Dictionary with all energy components
        """
        # Static potential (generates forces)
        static = self.compute_static_potential(phases, anchor_phases, equilibrium_shifts)
        
        # Dissipation functional
        R_noise = self.compute_dissipation_functional(velocities)
        
        # EBA diagnostic (if requested)
        if include_eba and memory_loop is not None:
            V_eba_diag = self.compute_eba_potential(memory_loop=memory_loop)
        else:
            V_eba_diag = 0.0
        
        # Total monitored energy
        E_monitor = static['V_static'] + R_noise + V_eba_diag
        
        return {
            'V_static': static['V_static'],
            'V_align': static['V_align'],
            'V_conflict': static['V_conflict'],
            'V_drift': static['V_drift'],
            'R_noise': R_noise,
            'V_eba_diag': V_eba_diag,
            'E_monitor': E_monitor,
            'static_components': static['components'],
        }
    
    def compute_force_from_potential(self,
                                    channel: int,
                                    phases: np.ndarray,
                                    anchor_phases: np.ndarray,
                                    equilibrium_shifts: Optional[np.ndarray] = None) -> float:
        """Compute force on channel k from potential gradient.
        
        F_k = -∂V/∂γ_k
        
        This includes contributions from all potential components.
        
        Args:
            channel: Channel index (0-7)
            phases: All channel phases
            anchor_phases: Reference anchors
            equilibrium_shifts: Equilibrium shifts
            
        Returns:
            Total force from potential gradient
        """
        if equilibrium_shifts is None:
            equilibrium_shifts = np.zeros((8, 8))
        
        # Force from alignment with identity
        F_align = self.alpha[channel] * np.sin(phases[channel] - self.identity.phase)
        
        # Force from conflicts with other channels
        # Include equilibrium shifts: sin(γ_k - γ_j - Δ^(0)_kj)
        F_conflict = 0.0
        for j in range(8):
            if j == channel:
                continue
            phase_diff = phases[channel] - phases[j] - equilibrium_shifts[channel, j]
            F_conflict += self.beta[channel, j] * np.sin(phase_diff)
        
        # Force from drift (quadratic, so linear gradient)
        drift = phases[channel] - anchor_phases[channel]
        # Wrap to [-π, π]
        drift = np.arctan2(np.sin(drift), np.cos(drift))
        # Gradient of V_drift = χ*drift² is 2χ*drift
        F_drift = 2.0 * self.chi[channel] * drift  # Positive gradient
        
        # Total force = -gradient (all components positive = pushing away from minima)
        return -(F_align + F_conflict + F_drift)
    
    def compute_global_memory_defect(self,
                                    phases: np.ndarray,
                                    equilibrium_shifts: Optional[np.ndarray] = None) -> float:
        """Compute D_mem: global defect between memory channels.
        
        Measures how far the entire memory configuration is from its
        equilibrium phase relationships.
        
        D_mem = sqrt(Σ_{k<j} [sin((γ_k - γ_j - Δ^(0)_kj)/2)]²)
        
        Args:
            phases: Current channel phases
            equilibrium_shifts: Equilibrium phase shifts Δ^(0)_kj
            
        Returns:
            Global memory defect (0 = perfect, higher = more defect)
        """
        if equilibrium_shifts is None:
            equilibrium_shifts = np.zeros((8, 8))
        
        defect_sum = 0.0
        count = 0
        
        for k in range(8):
            for j in range(k + 1, 8):  # k < j to avoid double counting
                phase_diff = phases[k] - phases[j] - equilibrium_shifts[k, j]
                # Use sin(Δ/2) for half-angle formula (better behaved)
                defect = np.sin(phase_diff / 2.0)
                defect_sum += defect**2
                count += 1
        
        # RMS defect across all pairs
        D_mem = np.sqrt(defect_sum / count) if count > 0 else 0.0
        
        return D_mem
    
    def compute_global_identity_defect(self,
                                      phases: np.ndarray) -> float:
        """Compute D_id: global defect relative to identity field.
        
        Measures how far all channels deviate from identity alignment,
        weighted by their coupling strengths.
        
        D_id = sqrt(Σ_k α_k * [sin((γ_k - γ_I)/2)]²) / sqrt(Σ_k α_k)
        
        Args:
            phases: Current channel phases
            
        Returns:
            Global identity defect (0 = perfect alignment, higher = more defect)
        """
        identity_phase = self.identity.phase
        
        weighted_defect_sum = 0.0
        weight_sum = 0.0
        
        for k in range(8):
            phase_diff = phases[k] - identity_phase
            # Weighted by alignment cost α_k
            weight = self.alpha[k]
            defect = np.sin(phase_diff / 2.0)
            
            weighted_defect_sum += weight * defect**2
            weight_sum += weight
        
        # Weighted RMS defect
        D_id = np.sqrt(weighted_defect_sum / weight_sum) if weight_sum > 0 else 0.0
        
        return D_id
    
    def analyze_stability(self, 
                         phases: np.ndarray,
                         anchor_phases: np.ndarray,
                         equilibrium_shifts: Optional[np.ndarray] = None) -> dict:
        """Analyze stability of current memory configuration.
        
        Args:
            phases: Current phases
            anchor_phases: Anchor phases
            equilibrium_shifts: Equilibrium phase shifts
            
        Returns:
            Dictionary with stability metrics including global defects
        """
        # Compute drifts
        drifts = phases - anchor_phases
        drifts = np.arctan2(np.sin(drifts), np.cos(drifts))
        
        # Check against allowed drifts
        max_drifts = np.array([CHANNEL_PARAMS[k].max_drift for k in range(8)])
        drift_ratios = np.abs(drifts) / max_drifts
        
        # Identify unstable channels
        unstable = drift_ratios > 1.0
        
        # Compute global defects
        D_mem = self.compute_global_memory_defect(phases, equilibrium_shifts)
        D_id = self.compute_global_identity_defect(phases)
        
        return {
            'drifts': drifts,
            'drift_ratios': drift_ratios,
            'max_drift_ratio': np.max(drift_ratios),
            'mean_drift_ratio': np.mean(drift_ratios),
            'unstable_channels': np.where(unstable)[0].tolist(),
            'num_unstable': int(np.sum(unstable)),
            'is_stable': not np.any(unstable),
            'D_mem': D_mem,
            'D_id': D_id,
            'global_coherence': 1.0 - (D_mem + D_id) / 2.0,  # Combined metric
        }


__all__ = [
    'MemoryPotential',
]
