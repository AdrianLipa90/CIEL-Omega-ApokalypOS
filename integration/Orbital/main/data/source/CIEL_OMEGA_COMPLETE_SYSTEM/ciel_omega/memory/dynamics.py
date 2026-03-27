"""CIEL/Ω Memory Architecture - Dynamics Engine

Implements evolution equations for memory channels. Fast channels (M0, M1, M5)
use first-order dynamics, slow channels (M2, M3, M4, M6, M7) use second-order
with inertia and damping.

dγ/dt = F (first order)
μ d²γ/dt² = F - η dγ/dt (second order)

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Dict, List
from dataclasses import dataclass

from .base import CHANNEL_PARAMS, IdentityField, PhaseState
from .coupling import CouplingEngine
from .potential import MemoryPotential


@dataclass
class MemorySystemState:
    """Complete state of memory system at one timestep"""
    
    phases: np.ndarray          # 8 channel phases
    velocities: np.ndarray      # 8 phase velocities
    anchor_phases: np.ndarray   # 8 anchor phases
    identity_phase: float       # Identity attractor phase
    timestep: int              # Current timestep
    time: float                # Current time
    
    def copy(self) -> MemorySystemState:
        """Create deep copy of state"""
        return MemorySystemState(
            phases=self.phases.copy(),
            velocities=self.velocities.copy(),
            anchor_phases=self.anchor_phases.copy(),
            identity_phase=self.identity_phase,
            timestep=self.timestep,
            time=self.time
        )


class MemoryDynamicsEngine:
    """Integrates memory system evolution over time.
    
    Combines forces from:
    - Identity alignment
    - Inter-channel coupling
    - Potential gradients  
    - External inputs
    
    Then evolves each channel according to its order (1st or 2nd).
    
    CRITICAL STABILITY CONSTRAINTS:
    - Maximum safe timestep: DT_MAX = 0.2
    - Default timestep: DT_DEFAULT = 0.1
    - For dt > DT_MAX, automatic substepping is used
    - Warning threshold: DT_WARN_THRESHOLD = 0.25
    """
    
    # Timestep stability limits (empirically determined)
    DT_DEFAULT = 0.1
    DT_MAX = 0.2
    DT_WARN_THRESHOLD = 0.25
    
    def __init__(self, 
                 identity_field: Optional[IdentityField] = None,
                 coupling_engine: Optional[CouplingEngine] = None,
                 potential: Optional[MemoryPotential] = None):
        """Initialize dynamics engine.
        
        Args:
            identity_field: Central attractor
            coupling_engine: Coupling calculator
            potential: Potential energy calculator
        """
        self.identity = identity_field or IdentityField()
        self.coupling = coupling_engine or CouplingEngine()
        self.potential = potential or MemoryPotential(self.identity)
        
        # Compute equilibrium phase shifts WITH role amplitudes
        role_amps = self.coupling.get_default_role_amplitudes()
        self.equilibrium_shifts = self.coupling.compute_phase_shift_matrix(
            role_amplitudes=role_amps
        )
        
        # History tracking
        self.history: List[MemorySystemState] = []
        self.potential_history: List[Dict] = []
        
    def initialize_state(self, 
                        initial_phases: Optional[np.ndarray] = None,
                        initial_identity_phase: float = 0.0) -> MemorySystemState:
        """Create initial system state.
        
        Args:
            initial_phases: Starting phases for 8 channels, or None for random
            initial_identity_phase: Starting identity phase
            
        Returns:
            Initial state
        """
        if initial_phases is None:
            # Random initialization near identity
            initial_phases = initial_identity_phase + np.random.randn(8) * 0.1
            initial_phases = initial_phases % (2 * np.pi)
        
        # Set identity phase
        self.identity.phase = initial_identity_phase
        
        state = MemorySystemState(
            phases=initial_phases,
            velocities=np.zeros(8),
            anchor_phases=initial_phases.copy(),
            identity_phase=initial_identity_phase,
            timestep=0,
            time=0.0
        )
        
        self.history = [state.copy()]
        return state
    
    def compute_total_force(self,
                           channel: int,
                           state: MemorySystemState,
                           input_forces: Optional[np.ndarray] = None) -> float:
        """Compute total force acting on one channel.
        
        F_total = -∂V/∂γ_k + F_input
        
        All internal forces (identity alignment, coupling, drift) come
        from potential gradient. This ensures consistency with potential
        energy landscape.
        
        Args:
            channel: Channel index (0-7)
            state: Current system state
            input_forces: External input forces (8-array), or None
            
        Returns:
            Total force on channel
        """
        # Force from potential gradient (includes alignment, coupling, drift)
        F_potential = self.potential.compute_force_from_potential(
            channel,
            state.phases,
            state.anchor_phases,
            self.equilibrium_shifts
        )
        
        # External input force only
        F_input = input_forces[channel] if input_forces is not None else 0.0
        
        # Total = gradient + external input
        return F_potential + F_input
    
    def evolve_channel(self,
                      channel: int,
                      state: MemorySystemState,
                      total_force: float,
                      dt: float) -> tuple[float, float]:
        """Evolve single channel forward by dt.
        
        Args:
            channel: Channel index
            state: Current state
            total_force: Total force on channel
            dt: Timestep
            
        Returns:
            (new_phase, new_velocity) tuple
        """
        params = CHANNEL_PARAMS[channel]
        current_phase = state.phases[channel]
        current_velocity = state.velocities[channel]
        
        if params.order == 1:
            # First-order: dγ/dt = F
            new_velocity = total_force  # Instantaneous
            new_phase = (current_phase + new_velocity * dt) % (2 * np.pi)
            
        else:
            # Second-order: μ d²γ/dt² = F - η dγ/dt
            inertia = params.tau
            damping = 0.1 * params.tau  # 10% critical damping
            
            acceleration = (total_force - damping * current_velocity) / inertia
            new_velocity = current_velocity + acceleration * dt
            new_phase = (current_phase + new_velocity * dt) % (2 * np.pi)
        
        return new_phase, new_velocity
    
    def step(self,
             state: MemorySystemState,
             dt: float,
             input_forces: Optional[np.ndarray] = None) -> MemorySystemState:
        """Advance system by one timestep.
        
        Args:
            state: Current state
            dt: Timestep size
            input_forces: External forces on each channel
            
        Returns:
            New state after evolution
        """
        # Compute forces on all channels
        total_forces = np.zeros(8)
        for k in range(8):
            total_forces[k] = self.compute_total_force(k, state, input_forces)
        
        # Evolve all channels
        new_phases = np.zeros(8)
        new_velocities = np.zeros(8)
        
        for k in range(8):
            new_phases[k], new_velocities[k] = self.evolve_channel(
                k, state, total_forces[k], dt
            )
        
        # Create new state
        new_state = MemorySystemState(
            phases=new_phases,
            velocities=new_velocities,
            anchor_phases=state.anchor_phases.copy(),  # Anchors don't move
            identity_phase=state.identity_phase,       # Identity very slow
            timestep=state.timestep + 1,
            time=state.time + dt
        )
        
        # Record monitored energy for diagnostics
        energy_info = self.potential.compute_monitored_energy(
            new_phases,
            new_state.anchor_phases,
            new_velocities,
            self.equilibrium_shifts
        )
        
        # Store history
        self.history.append(new_state.copy())
        self.potential_history.append(energy_info)
        
        return new_state
    
    def integrate(self,
                  num_steps: int,
                  dt: float,
                  input_forces: Optional[np.ndarray] = None,
                  initial_state: Optional[MemorySystemState] = None,
                  use_substepping: bool = True) -> MemorySystemState:
        """Integrate system for multiple timesteps with adaptive substepping.
        
        If dt > DT_MAX and use_substepping=True, automatically subdivides
        each step to maintain numerical stability.
        
        Args:
            num_steps: Number of steps to take
            dt: Timestep size (will be subdivided if > DT_MAX)
            input_forces: Constant external forces, or None
            initial_state: Starting state, or None to use current
            use_substepping: Whether to automatically subdivide large timesteps
            
        Returns:
            Final state after integration
        """
        # Warn about potentially unstable timesteps
        if dt > self.DT_WARN_THRESHOLD:
            import warnings
            warnings.warn(
                f"Large timestep dt={dt:.2f} may cause numerical instability. "
                f"Recommended dt <= {self.DT_MAX}. "
                f"Using automatic substepping."
            )
        
        # Determine effective timestep with substepping
        if use_substepping and dt > self.DT_MAX:
            # Subdivide into steps of size <= DT_MAX
            n_substeps = int(np.ceil(dt / self.DT_MAX))
            dt_effective = dt / n_substeps
        else:
            n_substeps = 1
            dt_effective = dt
        
        # Initialize state
        if initial_state is not None:
            state = initial_state
        elif len(self.history) > 0:
            state = self.history[-1].copy()
        else:
            state = self.initialize_state()
        
        # Integrate with substepping
        for _ in range(num_steps):
            # Take substeps if needed
            for _ in range(n_substeps):
                state = self.step(state, dt_effective, input_forces)
        
        return state
    
    def update_anchors(self, state: MemorySystemState) -> MemorySystemState:
        """Update anchor phases to current positions (after consolidation).
        
        Args:
            state: Current state
            
        Returns:
            New state with updated anchors
        """
        new_state = state.copy()
        new_state.anchor_phases = state.phases.copy()
        return new_state
    
    def compute_stability_metrics(self, state: MemorySystemState) -> dict:
        """Compute stability metrics for current state.
        
        Args:
            state: State to analyze
            
        Returns:
            Dictionary with stability information including D_mem, D_id
        """
        # Pass equilibrium shifts for correct defect calculation
        stability = self.potential.analyze_stability(
            state.phases,
            state.anchor_phases,
            self.equilibrium_shifts  # FIXED: now passes shifts
        )
        
        # Add energy information
        energy_info = self.potential.compute_monitored_energy(
            state.phases,
            state.anchor_phases,
            state.velocities,
            self.equilibrium_shifts
        )
        
        stability['energy'] = energy_info
        
        # Add coherence measures
        from .base import PhaseState
        
        coherences = []
        for k in range(8):
            identity_coherence = np.cos(state.phases[k] - state.identity_phase)
            coherences.append(identity_coherence)
        
        stability['identity_coherences'] = np.array(coherences)
        stability['mean_coherence'] = np.mean(coherences)
        
        return stability
    
    def get_trajectory(self, channel: int) -> tuple[np.ndarray, np.ndarray]:
        """Get phase trajectory for one channel.
        
        Args:
            channel: Channel index (0-7)
            
        Returns:
            (times, phases) arrays
        """
        times = np.array([s.time for s in self.history])
        phases = np.array([s.phases[channel] for s in self.history])
        return times, phases
    
    def get_energy_trajectory(self) -> tuple[np.ndarray, dict]:
        """Get energy trajectory from history.
        
        Returns:
            (times, energies_dict) where energies_dict has keys:
            V_static, V_align, V_conflict, V_drift, R_noise, E_monitor
        """
        times = np.array([s.time for s in self.history[1:]])  # Skip initial
        
        energies = {
            'V_static': [],
            'V_align': [],
            'V_conflict': [],
            'V_drift': [],
            'R_noise': [],
            'E_monitor': [],
        }
        
        for e_info in self.potential_history:
            energies['V_static'].append(e_info.get('V_static', 0))
            energies['V_align'].append(e_info.get('V_align', 0))
            energies['V_conflict'].append(e_info.get('V_conflict', 0))
            energies['V_drift'].append(e_info.get('V_drift', 0))
            energies['R_noise'].append(e_info.get('R_noise', 0))
            energies['E_monitor'].append(e_info.get('E_monitor', 0))
        
        for key in energies:
            energies[key] = np.array(energies[key])
        
        return times, energies


__all__ = [
    'MemorySystemState',
    'MemoryDynamicsEngine',
]
