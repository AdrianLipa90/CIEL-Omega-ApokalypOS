"""CIEL/Ω Memory Architecture - Identity Memory Types

Data structures for M6 IdentityMemory channel. This channel stores
historical traces of identity stabilization, not the current identity
attractor (which remains IdentityField).

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional
import numpy as np


@dataclass
class IdentityTrace:
    """Single trace point in identity evolution history.
    
    Records a snapshot of identity field alignment at a specific time.
    Used to track slow changes in identity over long windows.
    """
    
    timestamp: float              # Time of observation
    phase: float                  # γ_I at this time
    phase_diff: float            # Δφ = γ_M6 - γ_I (wrapped to [-π, π])
    alignment_to_field: float     # How aligned M6 is to IdentityField
    D_id_local: float            # Local identity defect at this time
    confidence: float            # Confidence in this trace (0-1)
    source_evidence_count: int   # Number of supporting observations
    
    def __repr__(self) -> str:
        return (f"IdentityTrace(t={self.timestamp:.1f}, "
                f"γ_I={self.phase:.3f}, "
                f"Δφ={self.phase_diff:.3f}, "
                f"align={self.alignment_to_field:.3f}, "
                f"conf={self.confidence:.3f})")


@dataclass
class IdentityAnchorCandidate:
    """Candidate for a new or updated identity anchor.
    
    Created when a pattern shows sustained alignment over long window.
    Does NOT automatically modify IdentityField - requires explicit approval.
    
    M6.1: Separates two levels of validation:
    - trace_support_count: Number of traces in evaluation window
    - candidate_confirmation_count: Number of independent validation cycles
    """
    
    anchor_key: str               # Semantic key (e.g., "commitment:research")
    proposed_phase: float         # Proposed stable phase for this anchor
    trace_support_count: int     # Number of traces in current evaluation window
    candidate_confirmation_count: int  # Number of independent confirmations
    time_span: float             # Duration over which pattern held
    mean_alignment: float        # Average alignment to IdentityField
    mean_stability: float        # Average phase stability (M6.1: circular concentration)
    contradiction_score: float   # How much this contradicts existing anchors
    accepted: bool               # Whether this has been promoted to anchor
    created_at: float            # Timestamp of creation
    last_updated: float          # Last confirmation timestamp
    
    def is_detected(self, min_trace_support: int = 3) -> bool:
        """Check if candidate meets detection criteria (Level A)"""
        return self.trace_support_count >= min_trace_support
    
    def is_mature(self, 
                  min_confirmations: int,
                  min_alignment: float,
                  min_stability: float,
                  max_contradiction: float) -> bool:
        """Check if candidate meets maturity criteria (Level B)
        
        Mature candidates are ready for potential promotion to anchors.
        Requires multiple independent confirmations and high quality metrics.
        
        NOTE: Thresholds must be explicitly provided by IdentityMemory.
        This ensures single source of truth for maturity criteria.
        
        Args:
            min_confirmations: Minimum confirmation cycles required
            min_alignment: Minimum alignment threshold
            min_stability: Minimum stability threshold  
            max_contradiction: Maximum contradiction allowed
        """
        return (self.candidate_confirmation_count >= min_confirmations and
                self.mean_alignment >= min_alignment and
                self.mean_stability >= min_stability and
                self.contradiction_score <= max_contradiction and
                not self.accepted)
    
    def __repr__(self) -> str:
        status = "✓" if self.accepted else f"conf={self.candidate_confirmation_count}"
        return (f"AnchorCandidate({self.anchor_key}, "
                f"traces={self.trace_support_count}, {status})")


@dataclass
class IdentityMemorySnapshot:
    """Persistent snapshot of M6 state at a point in time.
    
    Used for long-term storage and retrieval of identity evolution.
    """
    
    timestamp: float             # When snapshot was taken
    phase: float                 # M6 phase at this time
    amplitude: float             # M6 amplitude
    confidence: float            # Overall confidence in identity
    stability: float             # How stable identity has been
    anchor_vector: Dict[str, float]  # Current anchor phases
    source_window_stats: Dict[str, float]  # Statistics from observation window
    
    def __repr__(self) -> str:
        n_anchors = len(self.anchor_vector)
        return (f"IdentitySnapshot(t={self.timestamp:.1f}, "
                f"γ={self.phase:.3f}, "
                f"conf={self.confidence:.3f}, "
                f"anchors={n_anchors})")


@dataclass
class IdentityConsolidationScore:
    """Decomposed consolidation score for M6 updates.
    
    C_M6 = w_a*A + w_s*S + w_c*C + w_e*E - w_x*X
    """
    
    alignment: float             # A: alignment to IdentityField
    stability: float             # S: temporal stability
    confidence: float            # C: confidence/support count
    eba_quality: float          # E: EBA closure quality
    contradiction: float        # X: contradiction/drift penalty
    
    # Weights (can be tuned)
    w_a: float = 0.3
    w_s: float = 0.25
    w_c: float = 0.2
    w_e: float = 0.15
    w_x: float = 0.3
    
    def compute_total(self) -> float:
        """Compute total consolidation score"""
        return (self.w_a * self.alignment +
                self.w_s * self.stability +
                self.w_c * self.confidence +
                self.w_e * self.eba_quality -
                self.w_x * self.contradiction)
    
    def __repr__(self) -> str:
        total = self.compute_total()
        return (f"ConsolidationScore(total={total:.3f}, "
                f"A={self.alignment:.2f}, S={self.stability:.2f}, "
                f"C={self.confidence:.2f})")


__all__ = [
    'IdentityTrace',
    'IdentityAnchorCandidate',
    'IdentityMemorySnapshot',
    'IdentityConsolidationScore',
]
