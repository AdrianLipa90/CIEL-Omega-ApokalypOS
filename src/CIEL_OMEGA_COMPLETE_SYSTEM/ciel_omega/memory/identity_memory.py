"""CIEL/Ω Memory Architecture - M6 Identity Memory Channel

M6 stores historical traces of identity stabilization. It is NOT a duplicate
of IdentityField - rather, it records the slow evolution of identity over time.

Key principles:
- IdentityField remains the attractor and operator
- M6 records historical osads (deposits) of identity stabilization
- Very slow updates, high thresholds, conservative
- Single episodes cannot modify M6 core
- Requires long windows and multiple confirmations

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

from __future__ import annotations

import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import deque

from .base import BaseMemoryChannel, PhaseState, IdentityField
from .identity_types import (
    IdentityTrace,
    IdentityAnchorCandidate,
    IdentityMemorySnapshot,
    IdentityConsolidationScore,
)


class IdentityMemory(BaseMemoryChannel):
    """M6 Identity Memory channel - historical record of identity evolution.
    
    This is a MEMORY CHANNEL, not the identity attractor itself.
    IdentityField remains the source of truth for current identity.
    
    M6 observes IdentityField over long windows and records:
    - Traces of identity stabilization
    - Candidates for anchor updates
    - Snapshots of identity state
    
    M6 has very conservative update rules:
    - Very high τ (slow dynamics)
    - Very small max_drift (resists change)
    - High consolidation thresholds
    - Requires multiple confirmations (N_min >= 3)
    - Long observation windows
    """
    
    # M6.1: Two-level consolidation thresholds
    # Level A: Detection (candidate created)
    DETECTION_THRESHOLD = 0.60     # C_M6 must exceed this for detection
    MIN_TRACE_SUPPORT = 3          # Minimum traces in evaluation window
    MIN_TIME_SPAN = 10.0           # Minimum duration for pattern
    
    # Level B: Maturity (candidate ready for promotion)
    MIN_CONFIRMATIONS = 3          # Minimum independent confirmation cycles
    MIN_MATURE_ALIGNMENT = 0.75    # Alignment threshold for maturity
    MIN_MATURE_STABILITY = 0.85    # Stability threshold for maturity (raised from 0.80 in M6.1)
    MAX_MATURE_CONTRADICTION = 0.30  # Maximum contradiction for maturity (M6 observer model)
    
    TRACE_WINDOW_SIZE = 100        # Keep last N traces
    
    def __init__(self, identity_field: IdentityField):
        """Initialize M6 Identity Memory channel.
        
        Args:
            identity_field: Reference to the identity attractor (NOT owned by M6)
        """
        # M6 has conservative phase dynamics (from CHANNEL_PARAMS[6])
        from .base import CHANNEL_PARAMS
        super().__init__(params=CHANNEL_PARAMS[6])
        
        # Reference to identity field (M6 observes, does not control)
        self.identity_field = identity_field
        
        # Historical traces of identity evolution
        self.traces: deque[IdentityTrace] = deque(maxlen=self.TRACE_WINDOW_SIZE)
        
        # Anchor candidates (not yet accepted)
        self.anchor_candidates: Dict[str, IdentityAnchorCandidate] = {}
        
        # Snapshots for long-term storage
        self.snapshots: List[IdentityMemorySnapshot] = []
        
        # Observation statistics
        self.observation_count = 0
        self.last_observation_time = 0.0
        
        # Consolidation history
        self.consolidation_scores: List[IdentityConsolidationScore] = []
    
    def observe_identity_field(self, 
                              current_time: float,
                              equilibrium_shifts: Optional[np.ndarray] = None) -> IdentityTrace:
        """Observe current IdentityField and record a trace.
        
        This is the PRIMARY way M6 updates - by observing IdentityField,
        not by direct input.
        
        Args:
            current_time: Current simulation time
            equilibrium_shifts: Phase shifts for computing alignment
            
        Returns:
            New IdentityTrace record
        """
        # Measure alignment between M6 phase and IdentityField phase
        phase_diff = self.state.phase - self.identity_field.phase
        phase_diff = np.arctan2(np.sin(phase_diff), np.cos(phase_diff))  # Wrap to [-π, π]
        alignment = 1.0 - abs(phase_diff) / np.pi  # [0, 1]
        
        # Compute local identity defect (how far M6 is from field)
        D_id_local = abs(np.sin(phase_diff / 2.0))
        
        # Confidence based on recent trace stability
        confidence = self._compute_trace_confidence()
        
        # Evidence count from recent window
        source_evidence = min(len(self.traces), 10)
        
        # Create trace with explicit phase_diff
        trace = IdentityTrace(
            timestamp=current_time,
            phase=self.identity_field.phase,
            phase_diff=phase_diff,  # Store explicit wrapped difference
            alignment_to_field=alignment,
            D_id_local=D_id_local,
            confidence=confidence,
            source_evidence_count=source_evidence
        )
        
        # Store trace
        self.traces.append(trace)
        self.observation_count += 1
        self.last_observation_time = current_time
        
        return trace
    
    def compute_consolidation_score(self,
                                    eba_quality: float = 0.0) -> IdentityConsolidationScore:
        """Compute consolidation score C_M6 from recent traces.
        
        C_M6 = w_a*A + w_s*S + w_c*C + w_e*E - w_x*X
        
        Args:
            eba_quality: EBA closure quality (if available)
            
        Returns:
            Decomposed consolidation score
        """
        if len(self.traces) < 2:
            # Not enough data
            return IdentityConsolidationScore(
                alignment=0.0, stability=0.0, confidence=0.0,
                eba_quality=0.0, contradiction=1.0
            )
        
        # Component A: Mean alignment to IdentityField over window
        recent_traces = list(self.traces)[-20:]  # Last 20 traces
        alignment = np.mean([t.alignment_to_field for t in recent_traces])
        
        # Component S: Temporal stability using circular concentration of IdentityField phases
        # Measures whether IdentityField itself is stable over observation window
        identity_phases = [t.phase for t in recent_traces]
        
        # Circular concentration: R = |mean(e^(iφ))|
        if identity_phases:
            complex_mean = np.mean([np.exp(1j * phi) for phi in identity_phases])
            circular_concentration = abs(complex_mean)
            
            # Apply R^7 penalty matching 8-dimensional phase space (tensor-scalar field)
            # For R=0.999 → R^7=0.993, for R=0.97 → R^7=0.807
            circular_concentration = circular_concentration ** 7
        else:
            circular_concentration = 0.0
        
        # Hybrid stability: 70% circular concentration + 30% mean alignment
        # Balances IdentityField phase coherence with M6 alignment quality
        stability = 0.7 * circular_concentration + 0.3 * alignment
        
        # Component C: Confidence from support count
        support_count = len(recent_traces)
        confidence = min(1.0, support_count / self.MIN_TRACE_SUPPORT)
        
        # Component E: EBA quality (passed in, or 0 if not available)
        # Component X: Contradiction (high D_id_local = high contradiction)
        mean_d_id = np.mean([t.D_id_local for t in recent_traces])
        contradiction = mean_d_id
        
        score = IdentityConsolidationScore(
            alignment=alignment,
            stability=stability,
            confidence=confidence,
            eba_quality=eba_quality,
            contradiction=contradiction
        )
        
        # Store for history
        self.consolidation_scores.append(score)
        
        return score
    
    def check_anchor_candidate_creation(self,
                                       current_time: float,
                                       anchor_key: str,
                                       proposed_phase: float) -> Optional[IdentityAnchorCandidate]:
        """Check if conditions are met to create/update an anchor candidate.
        
        M6.1: Implements two-level validation:
        - Level A (Detection): Creates candidate if basic criteria met
        - Level B (Maturity): Candidate becomes mature with sustained confirmation
        
        Does NOT automatically accept the candidate - just creates/updates it.
        
        Args:
            current_time: Current time
            anchor_key: Semantic key for anchor
            proposed_phase: Proposed stable phase
            
        Returns:
            Created/updated candidate, or None if detection criteria not met
        """
        # Compute consolidation score
        score = self.compute_consolidation_score()
        
        # Level A: Detection criteria
        # Check if score exceeds detection threshold
        if score.compute_total() < self.DETECTION_THRESHOLD:
            return None
        
        # Check if we have enough trace support
        trace_count = len(self.traces)
        if trace_count < self.MIN_TRACE_SUPPORT:
            return None
        
        # Check time span
        if len(self.traces) >= 2:
            time_span = self.traces[-1].timestamp - self.traces[0].timestamp
        else:
            time_span = 0.0
        
        if time_span < self.MIN_TIME_SPAN:
            return None
        
        # Detection criteria met - create or update candidate
        if anchor_key in self.anchor_candidates:
            # Update existing candidate
            candidate = self.anchor_candidates[anchor_key]
            
            # Increment confirmation count (independent validation cycle)
            candidate.candidate_confirmation_count += 1
            
            # Update trace support from current window
            candidate.trace_support_count = trace_count
            
            # Update quality metrics
            candidate.time_span = time_span
            candidate.mean_alignment = score.alignment
            candidate.mean_stability = score.stability
            candidate.contradiction_score = score.contradiction
            candidate.last_updated = current_time
        else:
            # Create new candidate
            candidate = IdentityAnchorCandidate(
                anchor_key=anchor_key,
                proposed_phase=proposed_phase,
                trace_support_count=trace_count,  # Traces in current window
                candidate_confirmation_count=1,    # First confirmation
                time_span=time_span,
                mean_alignment=score.alignment,
                mean_stability=score.stability,
                contradiction_score=score.contradiction,
                accepted=False,
                created_at=current_time,
                last_updated=current_time
            )
            self.anchor_candidates[anchor_key] = candidate
        
        return candidate
    
    def take_snapshot(self, current_time: float) -> IdentityMemorySnapshot:
        """Create snapshot of current M6 state.
        
        Args:
            current_time: Current time
            
        Returns:
            Snapshot of M6 state
        """
        # Collect anchor vector from identity field
        anchor_vector = {
            anchor: 0.0  # Placeholder - would need actual anchor phases
            for anchor in self.identity_field.anchors
        }
        
        # Compute statistics from recent window
        if len(self.traces) >= 2:
            recent = list(self.traces)[-20:]
            window_stats = {
                'mean_alignment': np.mean([t.alignment_to_field for t in recent]),
                'std_alignment': np.std([t.alignment_to_field for t in recent]),
                'mean_d_id': np.mean([t.D_id_local for t in recent]),
                'observation_count': len(recent),
            }
        else:
            window_stats = {}
        
        # Compute overall confidence and stability
        if self.consolidation_scores:
            latest_score = self.consolidation_scores[-1]
            confidence = latest_score.confidence
            stability = latest_score.stability
        else:
            confidence = 0.0
            stability = 0.0
        
        snapshot = IdentityMemorySnapshot(
            timestamp=current_time,
            phase=self.state.phase,
            amplitude=self.state.amplitude,
            confidence=confidence,
            stability=stability,
            anchor_vector=anchor_vector,
            source_window_stats=window_stats
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_mature_candidates(self) -> List[IdentityAnchorCandidate]:
        """Get anchor candidates that meet maturity criteria (Level B).
        
        M6.1: Mature candidates have passed both detection and sustained
        confirmation with high quality metrics.
        
        Returns:
            List of mature candidates ready for potential promotion
        """
        return [
            candidate for candidate in self.anchor_candidates.values()
            if candidate.is_mature(
                min_confirmations=self.MIN_CONFIRMATIONS,
                min_alignment=self.MIN_MATURE_ALIGNMENT,
                min_stability=self.MIN_MATURE_STABILITY,
                max_contradiction=self.MAX_MATURE_CONTRADICTION
            )
        ]
    
    def _compute_trace_confidence(self) -> float:
        """Compute confidence based on recent trace stability."""
        if len(self.traces) < 2:
            return 0.0
        
        # Look at last few traces
        recent = list(self.traces)[-5:]
        
        # High confidence if alignment is consistently high
        alignments = [t.alignment_to_field for t in recent]
        mean_align = np.mean(alignments)
        std_align = np.std(alignments)
        
        # Confidence increases with high mean and low variance
        confidence = mean_align * (1.0 - std_align)
        
        return max(0.0, min(1.0, confidence))
    
    def get_statistics(self) -> Dict:
        """Get statistics about M6 state.
        
        M6.1: Reports both detected and mature candidates separately.
        
        Returns:
            Dictionary with statistics
        """
        if not self.traces:
            return {
                'trace_count': 0,
                'observation_count': 0,
                'detected_candidates': 0,
                'mature_candidates': 0,
                'snapshot_count': 0,
            }
        
        recent_traces = list(self.traces)[-20:]
        
        # Count detected vs mature candidates
        detected_count = len(self.anchor_candidates)
        mature_count = len(self.get_mature_candidates())
        
        return {
            'trace_count': len(self.traces),
            'observation_count': self.observation_count,
            'detected_candidates': detected_count,
            'mature_candidates': mature_count,
            'snapshot_count': len(self.snapshots),
            'mean_alignment': np.mean([t.alignment_to_field for t in recent_traces]),
            'mean_d_id_local': np.mean([t.D_id_local for t in recent_traces]),
            'current_confidence': self._compute_trace_confidence(),
        }
    
    def __repr__(self) -> str:
        stats = self.get_statistics()
        return (f"IdentityMemory(traces={stats['trace_count']}, "
                f"detected={stats['detected_candidates']}, "
                f"mature={stats['mature_candidates']}, "
                f"align={stats.get('mean_alignment', 0):.3f})")
    
    # Required abstract methods from BaseMemoryChannel
    
    def store(self, item: any, **kwargs) -> bool:
        """Store operation for M6 - creates trace or snapshot.
        
        M6 doesn't store arbitrary items like M2. Instead, it records
        observations of IdentityField as traces.
        
        Args:
            item: Ignored for M6
            **kwargs: Can include 'current_time' for observation
            
        Returns:
            True if observation recorded
        """
        current_time = kwargs.get('current_time', self.last_observation_time + 1.0)
        self.observe_identity_field(current_time)
        return True
    
    def retrieve(self, query: any, **kwargs) -> List:
        """Retrieve operation for M6 - returns relevant traces or snapshots.
        
        Args:
            query: 'traces', 'snapshots', 'candidates', or 'recent'
            **kwargs: Additional parameters
            
        Returns:
            List of requested items
        """
        if query == 'traces':
            return list(self.traces)
        elif query == 'snapshots':
            return self.snapshots
        elif query == 'candidates':
            return list(self.anchor_candidates.values())
        elif query == 'recent':
            n = kwargs.get('n', 10)
            return list(self.traces)[-n:]
        else:
            # Default: return recent traces
            return list(self.traces)[-10:]
    
    def compute_input_force(self, input_data: any) -> float:
        """Compute input force for M6.
        
        M6 does NOT receive direct input forces. It only observes IdentityField.
        This method returns zero to enforce that M6 is not driven by external input.
        
        Args:
            input_data: Ignored
            
        Returns:
            0.0 (M6 is not directly forced)
        """
        # M6 is NOT directly driven by input
        # Flow is: R → IdentityField → M6 (observation only)
        return 0.0


__all__ = ['IdentityMemory']
