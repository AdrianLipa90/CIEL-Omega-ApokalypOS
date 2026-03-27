"""CIEL/Ω Memory Architecture - M8: Audit/Journal Memory

Not a phase oscillator - orthogonal to memory disk. Records provenance,
decisions, conflicts, and system evolution for analysis and debugging.

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.
"""

from __future__ import annotations

from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime


@dataclass
class JournalEntry:
    """Single audit log entry"""
    
    timestamp: float
    entry_type: str  # decision, promotion, rejection, conflict, repair, etc.
    source_channel: Optional[int]  # Which channel initiated this
    target_channel: Optional[int]  # Which channel was affected
    
    # Content
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # System state at time of entry
    system_state: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            'timestamp': self.timestamp,
            'type': self.entry_type,
            'source': self.source_channel,
            'target': self.target_channel,
            'description': self.description,
            'metadata': self.metadata,
            'state': self.system_state,
        }


class AuditJournalMemory:
    """M8: Decision trace and provenance tracking.
    
    This is NOT a phase oscillator like M0-M7. It's an external ledger
    that records:
    - Orchestrator decisions
    - Memory consolidations/promotions
    - Rejections and conflicts
    - Holonomy defects
    - Repair actions
    
    Used for debugging, analysis, and understanding system evolution.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.entries: List[JournalEntry] = []
        self.storage_path = storage_path
        
        # Indices for fast lookup
        self._by_type: Dict[str, List[JournalEntry]] = {}
        self._by_channel: Dict[int, List[JournalEntry]] = {}
        
        # Statistics
        self.stats = {
            'total_entries': 0,
            'by_type': {},
            'by_channel': {},
        }
        
        # Load from disk if exists
        if storage_path and storage_path.exists():
            self._load_from_disk()
    
    def log_decision(self, 
                    description: str,
                    orchestrator_state: Optional[Dict] = None,
                    metadata: Optional[Dict] = None) -> None:
        """Log orchestrator decision"""
        self._add_entry(
            entry_type='decision',
            description=description,
            metadata=metadata or {},
            system_state=orchestrator_state
        )
    
    def log_promotion(self,
                     memory_content: Any,
                     source_channel: int,
                     target_channel: int,
                     score: float,
                     reason: str) -> None:
        """Log memory promotion to higher channel"""
        self._add_entry(
            entry_type='promotion',
            source_channel=source_channel,
            target_channel=target_channel,
            description=f"Promoted from M{source_channel} to M{target_channel}: {reason}",
            metadata={
                'content': str(memory_content),
                'score': score,
                'reason': reason,
            }
        )
    
    def log_rejection(self,
                     memory_content: Any,
                     channel: int,
                     reason: str,
                     defect: Optional[float] = None) -> None:
        """Log memory rejection"""
        self._add_entry(
            entry_type='rejection',
            source_channel=channel,
            description=f"Rejected in M{channel}: {reason}",
            metadata={
                'content': str(memory_content),
                'reason': reason,
                'defect': defect,
            }
        )
    
    def log_conflict(self,
                    channels: List[int],
                    description: str,
                    resolution: Optional[str] = None) -> None:
        """Log conflict between memory channels"""
        self._add_entry(
            entry_type='conflict',
            description=description,
            metadata={
                'channels': channels,
                'resolution': resolution,
            }
        )
    
    def log_defect(self,
                  channel: int,
                  defect_type: str,
                  magnitude: float,
                  description: str) -> None:
        """Log detected holonomy or consistency defect"""
        self._add_entry(
            entry_type='defect',
            source_channel=channel,
            description=f"Defect in M{channel} ({defect_type}): {description}",
            metadata={
                'defect_type': defect_type,
                'magnitude': magnitude,
            }
        )
    
    def log_repair(self,
                  channel: int,
                  action: str,
                  result: str) -> None:
        """Log repair action taken"""
        self._add_entry(
            entry_type='repair',
            target_channel=channel,
            description=f"Repair in M{channel}: {action}",
            metadata={
                'action': action,
                'result': result,
            }
        )
    
    def log_consolidation(self,
                         source_channel: int,
                         target_channel: int,
                         num_memories: int,
                         success_rate: float) -> None:
        """Log batch consolidation operation"""
        self._add_entry(
            entry_type='consolidation',
            source_channel=source_channel,
            target_channel=target_channel,
            description=f"Consolidated {num_memories} memories from M{source_channel} to M{target_channel}",
            metadata={
                'num_memories': num_memories,
                'success_rate': success_rate,
            }
        )
    
    def _add_entry(self,
                  entry_type: str,
                  description: str,
                  source_channel: Optional[int] = None,
                  target_channel: Optional[int] = None,
                  metadata: Optional[Dict] = None,
                  system_state: Optional[Dict] = None) -> None:
        """Internal method to add entry"""
        entry = JournalEntry(
            timestamp=len(self.entries),  # Simple incrementing timestamp
            entry_type=entry_type,
            source_channel=source_channel,
            target_channel=target_channel,
            description=description,
            metadata=metadata or {},
            system_state=system_state,
        )
        
        self.entries.append(entry)
        
        # Update indices
        if entry_type not in self._by_type:
            self._by_type[entry_type] = []
        self._by_type[entry_type].append(entry)
        
        if source_channel is not None:
            if source_channel not in self._by_channel:
                self._by_channel[source_channel] = []
            self._by_channel[source_channel].append(entry)
        
        # Update stats
        self.stats['total_entries'] += 1
        self.stats['by_type'][entry_type] = self.stats['by_type'].get(entry_type, 0) + 1
        if source_channel is not None:
            self.stats['by_channel'][source_channel] = self.stats['by_channel'].get(source_channel, 0) + 1
        
        # Persist
        if self.storage_path:
            self._append_to_disk(entry)
    
    def get_entries(self, 
                   entry_type: Optional[str] = None,
                   channel: Optional[int] = None,
                   time_window: Optional[tuple] = None,
                   recent: Optional[int] = None) -> List[JournalEntry]:
        """Retrieve entries matching criteria"""
        results = self.entries.copy()
        
        if entry_type:
            results = self._by_type.get(entry_type, [])
        
        if channel is not None:
            results = [e for e in results 
                      if e.source_channel == channel or e.target_channel == channel]
        
        if time_window:
            start, end = time_window
            results = [e for e in results if start <= e.timestamp <= end]
        
        if recent:
            results = results[-recent:] if len(results) >= recent else results
        
        return results
    
    def get_provenance(self, memory_id: Any) -> List[JournalEntry]:
        """Get full provenance chain for a memory"""
        # Search for entries mentioning this memory
        provenance = []
        memory_str = str(memory_id)
        
        for entry in self.entries:
            if 'content' in entry.metadata:
                if memory_str in str(entry.metadata['content']):
                    provenance.append(entry)
        
        return provenance
    
    def analyze_channel_activity(self, channel: int) -> Dict:
        """Analyze activity for specific channel"""
        entries = self._by_channel.get(channel, [])
        
        if not entries:
            return {'channel': channel, 'activity': 'none'}
        
        by_type = {}
        for entry in entries:
            by_type[entry.entry_type] = by_type.get(entry.entry_type, 0) + 1
        
        return {
            'channel': channel,
            'total_entries': len(entries),
            'by_type': by_type,
            'first_activity': entries[0].timestamp,
            'last_activity': entries[-1].timestamp,
        }
    
    def generate_report(self, time_window: Optional[tuple] = None) -> str:
        """Generate human-readable audit report"""
        entries = self.entries
        if time_window:
            start, end = time_window
            entries = [e for e in entries if start <= e.timestamp <= end]
        
        lines = []
        lines.append("="*70)
        lines.append("AUDIT JOURNAL REPORT")
        lines.append("="*70)
        lines.append("")
        
        lines.append(f"Total Entries: {len(entries)}")
        lines.append("")
        
        lines.append("By Type:")
        for entry_type, count in sorted(self.stats['by_type'].items()):
            lines.append(f"  {entry_type:20s}: {count:5d}")
        lines.append("")
        
        lines.append("By Channel:")
        for channel, count in sorted(self.stats['by_channel'].items()):
            from .coupling import CHANNEL_NAMES
            name = CHANNEL_NAMES[channel] if channel < 8 else f"M{channel}"
            lines.append(f"  {name:25s}: {count:5d}")
        lines.append("")
        
        lines.append("Recent Activity (last 10 entries):")
        lines.append("-"*70)
        for entry in entries[-10:]:
            lines.append(f"[{entry.timestamp:6.0f}] {entry.entry_type:15s}: {entry.description[:50]}")
        
        lines.append("="*70)
        
        return "\n".join(lines)
    
    def _save_to_disk(self) -> None:
        """Save all entries to disk"""
        if not self.storage_path:
            return
        
        data = {
            'entries': [e.to_dict() for e in self.entries],
            'stats': self.stats,
        }
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
    
    def _append_to_disk(self, entry: JournalEntry) -> None:
        """Append single entry to disk (more efficient than full save)"""
        # For simplicity, just do full save for now
        # In production, use append-only log format
        self._save_to_disk()
    
    def _load_from_disk(self) -> None:
        """Load entries from disk"""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            data = json.loads(self.storage_path.read_text(encoding='utf-8'))
            
            if 'stats' in data:
                self.stats = data['stats']
            
            # Note: Full entry restoration would require more careful reconstruction
            # For now, just track we loaded something
            if 'entries' in data:
                print(f"Loaded {len(data['entries'])} journal entries from disk")
                
        except Exception as e:
            print(f"Failed to load journal: {e}")


__all__ = ['AuditJournalMemory', 'JournalEntry']
