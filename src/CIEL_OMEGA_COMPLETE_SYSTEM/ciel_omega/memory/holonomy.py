"""CIEL/Ω Memory Architecture - Holonomy and EBA Condition

Implements Euler-Berry-Aharonov-Bohm topological constraint for closed
memory loops. Ensures phase coherence across complete cycles through
relation → identity → memory → action → relation.

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

from __future__ import annotations

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from .base import CHANNEL_PARAMS

# Zeta Riemann seed: |ζ(-1)| = 1/12 — Ramanujan regularization.
# Replaces hard zeros so the system retains minimal persistence (non-zero trwanie).
_ZETA_SEED: float = 1.0 / 12.0

# Heisenberg soft clip: ΔxΔp ≥ ℏ/2 — replaces NaN/degenerate-zero in phase space.
# Prevents exact cancellation (xs=ys=0) from collapsing phase to undefined.
_H_CLIP: float = 1e-9


@dataclass
class MemoryLoop:
    """Represents a closed loop through memory channels"""
    
    channel_sequence: List[int]  # Ordered sequence of channel indices
    loop_type: str              # 'short', 'medium', 'deep'
    phase_trajectory: List[float]  # Phases at each step
    timestamps: List[float]     # Time at each step
    
    def is_closed(self, tolerance: float = 0.1) -> bool:
        """Check if loop returns close to starting phase"""
        if len(self.phase_trajectory) < 2:
            return False
        phase_diff = abs(self.phase_trajectory[-1] - self.phase_trajectory[0])
        phase_diff = min(phase_diff, 2*np.pi - phase_diff)
        return phase_diff < tolerance


class HolonomyCalculator:
    """Computes holonomy and EBA condition for memory loops.
    
    The EBA condition states that for a closed loop C:
    
    Φ_dyn(C) + Φ_Berry(C) + Φ_AB(C) = 2π*ν_E(C) + ε_EBA(C)
    
    where:
    - Φ_dyn: dynamical phase from evolution
    - Φ_Berry: geometric phase (solid angle on Bloch sphere)
    - Φ_AB: Aharonov-Bohm phase (non-local memory contributions)
    - ν_E: topological winding number (integer)
    - ε_EBA: defect (should be small for valid consolidation)
    """
    
    def __init__(self, coupling_strengths: Optional[np.ndarray] = None):
        """Initialize holonomy calculator.
        
        Args:
            coupling_strengths: 8x8 coupling matrix for AB phase calculation
        """
        from .coupling import COUPLING_MATRIX
        self.J = coupling_strengths if coupling_strengths is not None else COUPLING_MATRIX
        
    def compute_dynamical_phase(self, loop: MemoryLoop) -> float:
        """Compute dynamical phase Φ_dyn from trajectory.
        
        This is the accumulated phase change along the actual path taken.
        
        Φ_dyn = Σ Δγ_i
        
        Args:
            loop: Memory loop with phase trajectory
            
        Returns:
            Dynamical phase in radians
        """
        if len(loop.phase_trajectory) < 2:
            return _ZETA_SEED

        # Accumulate phase changes
        total_phase = _ZETA_SEED
        for i in range(1, len(loop.phase_trajectory)):
            delta = loop.phase_trajectory[i] - loop.phase_trajectory[i-1]
            # Don't unwrap - accumulate actual change including windings
            total_phase += delta
        
        return total_phase
    
    def compute_berry_phase(self, loop: MemoryLoop) -> float:
        """Compute Berry geometric phase Φ_Berry.
        
        For trajectory on Bloch sphere, Berry phase equals minus half
        the solid angle enclosed by the trajectory.
        
        Φ_Berry = -Ω/2
        
        We approximate solid angle from the phase trajectory using
        the fact that phase on Bloch sphere relates to solid angle.
        
        Args:
            loop: Memory loop with phase trajectory
            
        Returns:
            Berry phase in radians
        """
        if len(loop.phase_trajectory) < 3:
            return _ZETA_SEED

        phases = np.array(loop.phase_trajectory)
        area = _ZETA_SEED
        n = len(phases)
        
        for i in range(n):
            j = (i + 1) % n
            # Account for circular nature
            delta = phases[j] - phases[i]
            # Unwrap to [-π, π]
            delta = np.arctan2(np.sin(delta), np.cos(delta))
            area += phases[i] * delta
        
        # Berry phase is proportional to enclosed area
        # Factor of 1/2 from standard formula
        berry_phase = -area / 2.0
        
        return berry_phase
    
    def compute_ab_phase(self, loop: MemoryLoop, 
                        hidden_states: Optional[np.ndarray] = None) -> float:
        """Compute Aharonov-Bohm non-local phase Φ_AB.
        
        This represents phase contribution from memory sectors that were
        not locally active during the loop but affect global topology.
        
        Φ_AB = ∮ A_mem · dℓ
        
        where A_mem is the memory connection (not a local field).
        
        We approximate this using coupling strengths to channels not
        in the active loop.
        
        Args:
            loop: Memory loop
            hidden_states: Phases of non-active channels (8-array)
            
        Returns:
            AB phase in radians
        """
        if hidden_states is None:
            return _ZETA_SEED

        active_channels = set(loop.channel_sequence)
        hidden_channels = [k for k in range(8) if k not in active_channels]

        if not hidden_channels:
            return _ZETA_SEED

        ab_phase = _ZETA_SEED
        n_pairs = len(active_channels) * len(hidden_channels)

        for k in active_channels:
            for h in hidden_channels:
                coupling = self.J[k, h]
                if len(loop.phase_trajectory) > 0:
                    active_phase = np.mean([loop.phase_trajectory[i]
                                           for i, ch in enumerate(loop.channel_sequence)
                                           if ch == k])
                    hidden_phase = hidden_states[h]
                    phase_diff = hidden_phase - active_phase
                    ab_phase += coupling * np.sin(phase_diff)

        # Normalize by pair count so phi_AB stays bounded regardless of loop size
        return ab_phase / max(n_pairs, 1)
    
    def compute_winding_number(self, loop: MemoryLoop) -> int:
        """Compute topological winding number ν_E.
        
        This is the number of complete revolutions around the identity
        attractor, or the orbit class of the trajectory.
        
        Args:
            loop: Memory loop
            
        Returns:
            Integer winding number
        """
        if len(loop.phase_trajectory) < 2:
            return 0
        
        # Count net phase change in units of 2π
        total_change = self.compute_dynamical_phase(loop)
        
        # Round to nearest integer number of full rotations
        winding = int(np.round(total_change / (2 * np.pi)))
        
        return winding
    
    def compute_eba_defect(self,
                          loop: MemoryLoop,
                          hidden_states: Optional[np.ndarray] = None) -> Dict:
        """Compute full EBA defect ε_EBA for a loop.
        
        ε_EBA = Φ_dyn + Φ_Berry + Φ_AB - 2π*ν_E
        
        Args:
            loop: Memory loop to analyze
            hidden_states: Phases of channels not in loop
            
        Returns:
            Dictionary with all phase components and defect
        """
        # Compute all components
        phi_dyn = self.compute_dynamical_phase(loop)
        phi_berry = self.compute_berry_phase(loop)
        phi_ab = self.compute_ab_phase(loop, hidden_states)
        nu_e = self.compute_winding_number(loop)
        
        # Total phase
        phi_total = phi_dyn + phi_berry + phi_ab
        
        # Defect
        epsilon_eba = phi_total - 2 * np.pi * nu_e
        
        # Wrap to [-π, π]
        epsilon_eba = np.arctan2(np.sin(epsilon_eba), np.cos(epsilon_eba))
        
        return {
            'phi_dyn': phi_dyn,
            'phi_berry': phi_berry,
            'phi_ab': phi_ab,
            'nu_e': nu_e,
            'phi_total': phi_total,
            'epsilon_eba': epsilon_eba,
            'is_coherent': abs(epsilon_eba) < 0.1,  # Small defect = coherent
            'defect_magnitude': abs(epsilon_eba),
        }
    
    def check_consolidation_validity(self,
                                    loop: MemoryLoop,
                                    hidden_states: Optional[np.ndarray] = None,
                                    threshold: float = 0.15) -> bool:
        """Check if loop satisfies EBA condition for consolidation.
        
        For memory to be consolidated from one layer to another,
        the complete loop must have small EBA defect.
        
        Args:
            loop: Memory loop to check
            hidden_states: Hidden channel phases
            threshold: Maximum allowed |ε_EBA| for consolidation
            
        Returns:
            True if loop is valid for consolidation
        """
        result = self.compute_eba_defect(loop, hidden_states)
        return result['defect_magnitude'] < threshold


def define_standard_loops() -> Dict[str, List[int]]:
    """Define standard memory loop types.
    
    Returns:
        Dictionary mapping loop type to channel sequence
    """
    return {
        # Short consolidation loop: working → episodic → semantic → working
        'short': [1, 2, 3, 1],  # M1 → M2 → M3 → M1
        
        # Medium loop: relation → identity → episodic → semantic → procedural → action → relation
        # (Here we approximate relation/action as channels at boundaries)
        'medium': [0, 6, 2, 3, 4, 5, 0],  # M0 → M6 → M2 → M3 → M4 → M5 → M0
        
        # Deep loop: relation → identity → affective → identity_core → invariant → identity → relation
        'deep': [0, 6, 5, 6, 7, 6, 0],  # M0 → M6 → M5 → M6 → M7 → M6 → M0
        
        # Identity stabilization loop: working → affective → identity → invariant → identity → working
        'identity_stabilization': [1, 5, 6, 7, 6, 1],
        
        # Semantic consolidation loop: episodic → semantic → procedural → semantic → episodic
        'semantic_consolidation': [2, 3, 4, 3, 2],
    }


def create_loop_from_trajectory(channel_sequence: List[int],
                                phase_trajectory: List[float],
                                timestamps: Optional[List[float]] = None,
                                loop_type: str = 'custom') -> MemoryLoop:
    """Create MemoryLoop from trajectory data.
    
    Args:
        channel_sequence: Ordered channels visited
        phase_trajectory: Phases at each step
        timestamps: Optional times at each step
        loop_type: Type classification
        
    Returns:
        MemoryLoop instance
    """
    if timestamps is None:
        timestamps = list(range(len(phase_trajectory)))
    
    return MemoryLoop(
        channel_sequence=channel_sequence,
        loop_type=loop_type,
        phase_trajectory=phase_trajectory,
        timestamps=timestamps
    )


def compute_eba_potential_component(epsilon_eba: float,
                                    lambda_eba: float = 1.0) -> float:
    """Compute EBA contribution to memory potential.
    
    V_EBA = λ_EBA * (1 - cos(ε_EBA))
    
    This is added as a soft constraint to the memory potential.
    
    Args:
        epsilon_eba: EBA defect
        lambda_eba: Strength of EBA constraint
        
    Returns:
        Potential energy contribution
    """
    return lambda_eba * (1.0 - np.cos(epsilon_eba))


__all__ = [
    'MemoryLoop',
    'HolonomyCalculator',
    'define_standard_loops',
    'create_loop_from_trajectory',
    'compute_eba_potential_component',
]
