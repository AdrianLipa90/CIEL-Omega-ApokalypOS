"""CIEL/Ω Memory Architecture - M2: Episodic Memory

Memory of events and sequences. Records what happened, when, in what context,
and with what result. Medium timescale, good temporal localization.

τ=12, r=0.55, g=0.45, δ_max=0.16π

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

from __future__ import annotations

from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field
import numpy as np
import json
from pathlib import Path

from .base import BaseMemoryChannel, PhaseState, CHANNEL_PARAMS


@dataclass
class Episode:
    """Single episodic memory unit"""
    
    content: Any                    # What happened
    context: Dict[str, Any]         # Surrounding context
    result: Optional[Any]           # Outcome/result
    timestamp: float                # When it occurred
    phase_at_storage: float         # Phase when stored
    salience: float                 # Importance score
    identity_impact: float          # Impact on identity field
    
    # Consolidation tracking
    consolidation_score: float = 0.0
    promoted_to_semantic: bool = False
    
    # Links to other memories
    semantic_links: List[str] = field(default_factory=list)
    procedural_links: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            'content': str(self.content),
            'context': self.context,
            'result': str(self.result) if self.result else None,
            'timestamp': self.timestamp,
            'phase': self.phase_at_storage,
            'salience': self.salience,
            'identity_impact': self.identity_impact,
            'consolidation_score': self.consolidation_score,
            'promoted': self.promoted_to_semantic,
        }


class EpisodicMemory(BaseMemoryChannel):
    """M2: Event and sequence memory.
    
    Stores episodes with temporal context. Medium stability, medium
    coupling to identity. Episodes can consolidate to semantic memory
    if they prove stable and useful over time.
    
    This wraps and enhances existing LongTermMemory with phase dynamics.
    """
    
    def __init__(self, 
                 initial_state: Optional[PhaseState] = None,
                 storage_path: Optional[Path] = None):
        params = CHANNEL_PARAMS[2]  # M2
        super().__init__(params, initial_state)
        
        # Episode storage
        self.episodes: List[Episode] = []
        self.storage_path = storage_path
        
        # Indices for fast retrieval
        self._by_timestamp: Dict[float, Episode] = {}
        self._by_phase: Dict[float, List[Episode]] = {}  # Phase bins
        
        # Consolidation tracking
        self.consolidation_candidates: List[int] = []
        
        # Load from disk if path provided
        if storage_path and storage_path.exists():
            self._load_from_disk()
    
    def compute_input_force(self, input_data: Any) -> float:
        """Compute force from new episodic input.
        
        Episodic memory responds moderately fast to inputs.
        Force depends on:
        - Salience of new episode
        - Alignment with recent episodes
        - Impact on identity field
        """
        if not isinstance(input_data, dict):
            # Simple input - low force
            return 0.1
        
        salience = input_data.get('salience', 0.5)
        identity_impact = input_data.get('identity_impact', 0.3)
        
        # Force proportional to salience and impact
        force = 0.5 * salience + 0.5 * identity_impact
        
        # Modulate by recent episode density
        if len(self.episodes) > 0:
            recent_count = len([e for e in self.episodes[-20:]])
            # High density reduces force (saturation)
            density_factor = 1.0 / (1.0 + 0.1 * recent_count)
            force *= density_factor
        
        return force
    
    def store(self, content: Any, metadata: Optional[Dict] = None) -> None:
        """Store new episode.
        
        Args:
            content: Episode content (event description)
            metadata: Context, result, salience, etc.
        """
        metadata = metadata or {}
        
        episode = Episode(
            content=content,
            context=metadata.get('context', {}),
            result=metadata.get('result'),
            timestamp=metadata.get('timestamp', len(self.episodes)),
            phase_at_storage=self.state.phase,
            salience=metadata.get('salience', 0.5),
            identity_impact=metadata.get('identity_impact', 0.3),
        )
        
        self.episodes.append(episode)
        
        # Update indices
        self._by_timestamp[episode.timestamp] = episode
        phase_bin = int(episode.phase_at_storage * 10) / 10.0  # 0.1 rad bins
        if phase_bin not in self._by_phase:
            self._by_phase[phase_bin] = []
        self._by_phase[phase_bin].append(episode)
        
        # Check for consolidation candidacy
        if self._should_consolidate(episode):
            self.consolidation_candidates.append(len(self.episodes) - 1)
        
        # Persist to disk if path set
        if self.storage_path:
            self._save_to_disk()
    
    def retrieve(self, query: Any) -> Any:
        """Retrieve episodes matching query.
        
        Query can be:
        - time_window: (start, end) tuple
        - phase_window: (phase_min, phase_max) tuple
        - recent: int (last N episodes)
        - context_match: dict to match against context
        - min_salience: float threshold
        """
        if not isinstance(query, dict):
            # Return all episodes
            return self.episodes
        
        results = self.episodes.copy()
        
        # Filter by time window
        if 'time_window' in query:
            start, end = query['time_window']
            results = [e for e in results if start <= e.timestamp <= end]
        
        # Filter by phase window
        if 'phase_window' in query:
            phase_min, phase_max = query['phase_window']
            results = [e for e in results 
                      if phase_min <= e.phase_at_storage <= phase_max]
        
        # Get recent
        if 'recent' in query:
            n = query['recent']
            results = results[-n:] if len(results) >= n else results
        
        # Filter by minimum salience
        if 'min_salience' in query:
            threshold = query['min_salience']
            results = [e for e in results if e.salience >= threshold]
        
        # Filter by context match
        if 'context_match' in query:
            context_pattern = query['context_match']
            results = [e for e in results 
                      if self._context_matches(e.context, context_pattern)]
        
        return results
    
    def _context_matches(self, context: Dict, pattern: Dict) -> bool:
        """Check if episode context matches pattern"""
        for key, value in pattern.items():
            if key not in context:
                return False
            if context[key] != value:
                return False
        return True
    
    def _should_consolidate(self, episode: Episode) -> bool:
        """Check if episode should be considered for consolidation.
        
        Consolidation to semantic memory requires:
        - High salience
        - Low conflict with identity
        - Sufficient stability
        """
        if episode.salience < 0.7:
            return False
        
        if episode.identity_impact < 0.5:
            return False
        
        # Check phase stability (compare with recent episodes)
        if len(self.episodes) < 5:
            return False
        
        recent_phases = [e.phase_at_storage for e in self.episodes[-5:]]
        phase_variance = np.var(recent_phases)
        
        if phase_variance > 0.5:  # Too much variability
            return False
        
        return True
    
    def compute_consolidation_score(self, episode_idx: int) -> float:
        """Compute consolidation score for episode.
        
        Score based on:
        - Salience
        - Identity alignment
        - Temporal stability
        - Semantic linkage
        """
        if episode_idx >= len(self.episodes):
            return 0.0
        
        episode = self.episodes[episode_idx]
        
        # Base score from salience
        score = episode.salience
        
        # Bonus for identity alignment
        score += 0.3 * episode.identity_impact
        
        # Bonus for semantic links
        if len(episode.semantic_links) > 0:
            score += 0.2 * min(len(episode.semantic_links) / 3.0, 1.0)
        
        # Penalty for phase instability
        if episode_idx > 0:
            phase_diff = abs(episode.phase_at_storage - 
                           self.episodes[episode_idx-1].phase_at_storage)
            phase_diff = min(phase_diff, 2*np.pi - phase_diff)
            stability_penalty = phase_diff / np.pi
            score *= (1.0 - 0.5 * stability_penalty)
        
        episode.consolidation_score = score
        return score
    
    def get_consolidation_candidates(self, min_score: float = 0.8) -> List[Episode]:
        """Get episodes ready for consolidation to semantic memory"""
        candidates = []
        
        for idx in self.consolidation_candidates:
            if idx < len(self.episodes):
                score = self.compute_consolidation_score(idx)
                if score >= min_score:
                    candidates.append(self.episodes[idx])
        
        return candidates
    
    def mark_consolidated(self, episode: Episode) -> None:
        """Mark episode as consolidated to semantic memory"""
        episode.promoted_to_semantic = True
        if self.storage_path:
            self._save_to_disk()
    
    def _save_to_disk(self) -> None:
        """Persist episodes to disk"""
        if not self.storage_path:
            return
        
        data = {
            'episodes': [e.to_dict() for e in self.episodes],
            'state': {
                'phase': self.state.phase,
                'amplitude': self.state.amplitude,
                'reliability': self.state.reliability,
            }
        }
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def _load_from_disk(self) -> None:
        """Load episodes from disk"""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            data = json.loads(self.storage_path.read_text(encoding='utf-8'))
            
            # Restore state
            if 'state' in data:
                s = data['state']
                self.state.phase = s.get('phase', 0.0)
                self.state.amplitude = s.get('amplitude', 0.1)
                self.state.reliability = s.get('reliability', 0.5)
            
            # Restore episodes (simplified - full restore would need more work)
            # For now, just track count
            if 'episodes' in data:
                print(f"Loaded {len(data['episodes'])} episodes from disk")
                
        except Exception as e:
            print(f"Failed to load episodes: {e}")
    
    def get_statistics(self) -> Dict:
        """Get statistics about episodic memory"""
        if not self.episodes:
            return {'count': 0}
        
        return {
            'count': len(self.episodes),
            'mean_salience': np.mean([e.salience for e in self.episodes]),
            'mean_identity_impact': np.mean([e.identity_impact for e in self.episodes]),
            'promoted_count': sum(1 for e in self.episodes if e.promoted_to_semantic),
            'consolidation_candidates': len(self.consolidation_candidates),
            'phase_range': (
                min(e.phase_at_storage for e in self.episodes),
                max(e.phase_at_storage for e in self.episodes)
            ),
        }


__all__ = ['EpisodicMemory', 'Episode']
