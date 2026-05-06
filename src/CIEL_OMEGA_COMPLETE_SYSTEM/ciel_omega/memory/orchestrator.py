"""Holonomic memory orchestrator for the implemented CIEL/Ω memory channels.

This is the runtime glue that closes the memory sector:
M0 -> M1 -> M2 -> (M3, M4, M5) -> M6/M7 -> M8
with EBA loop checks and audit logging.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional
import math

import numpy as np

from .base import IdentityField
from .perceptual_memory import PerceptualMemory
from .working_memory import WorkingMemory
from .episodic import EpisodicMemory, Episode
from .semantic_memory import SemanticMemory
from .procedural_memory import ProceduralMemory
from .affective_memory import AffectiveEthicalMemory
from .identity_memory import IdentityMemory
from .braid_invariant import BraidInvariantMemory
from .audit_journal import AuditJournalMemory
from .dynamics import MemoryDynamicsEngine
from .holonomy import HolonomyCalculator, create_loop_from_trajectory, define_standard_loops
from .orbital_shell import OrbitalRecord, OrbitalShellIndex
from .orchestrator_types import (
    ConsolidationEvents,
    EBAEvaluation,
    OrchestratorCycleResult,
    OrchestratorSnapshot,
)


class HolonomicMemoryOrchestrator:
    """Conservative runtime orchestrator for the implemented memory channels.

    It does not replace IdentityField. It routes content through the existing
    channels, performs conservative candidate/consolidation checks, evaluates
    EBA loop closure, and records decisions in M8.
    """

    def __init__(self, identity_phase: float = 0.0):
        self.identity_field = IdentityField(initial_phase=identity_phase)
        self.m0 = PerceptualMemory(self.identity_field)
        self.m1 = WorkingMemory(self.identity_field)
        self.m2 = EpisodicMemory()
        self.m3 = SemanticMemory(self.identity_field)
        self.m4 = ProceduralMemory(self.identity_field)
        self.m5 = AffectiveEthicalMemory(self.identity_field)
        self.m6 = IdentityMemory(self.identity_field)
        self.m7 = BraidInvariantMemory()
        self.m8 = AuditJournalMemory()

        self.dynamics = MemoryDynamicsEngine(identity_field=self.identity_field)
        self.holonomy = HolonomyCalculator()
        self.loops = define_standard_loops()

        # Orbital shell index — populated in process_input, queried in retrieve
        self.orbital_index = OrbitalShellIndex(attractor_phase=identity_phase)
        self._orbital_record_counter = 0

        self.state = self.dynamics.initialize_state(
            initial_phases=np.array([
                self.m0.state.phase,
                self.m1.state.phase,
                self.m2.state.phase,
                self.m3.state.phase,
                self.m4.state.phase,
                self.m5.state.phase,
                self.m6.state.phase,
                self.m7.state.phase,
            ], dtype=float),
            initial_identity_phase=self.identity_field.phase,
        )
        self.current_time = 0.0
        self.cycle_index = 0
        self.last_eba: Dict[str, EBAEvaluation] = {}

    # ------------------------------------------------------------------
    # Pickle migration — survives class evolution without reset
    # ------------------------------------------------------------------
    _STATE_VERSION = 3  # bump when adding fields that need migration

    def __getstate__(self) -> dict:
        state = self.__dict__.copy()
        state['_pickle_version'] = self._STATE_VERSION
        return state

    def __setstate__(self, state: dict) -> None:
        version = state.pop('_pickle_version', 0)
        self.__dict__.update(state)
        # v0 → v1: working_memory gained _pending_consolidation
        if not hasattr(self.m1, '_pending_consolidation'):
            self.m1._pending_consolidation = []
        # v1 → v2: (reserved for future fields)
        # v2 → v3: orbital shell index
        if not hasattr(self, 'orbital_index'):
            ip = self.identity_field.phase if hasattr(self, 'identity_field') else 0.0
            self.orbital_index = OrbitalShellIndex(attractor_phase=ip)
        if not hasattr(self, '_orbital_record_counter'):
            self._orbital_record_counter = 0
        # Always ensure last_eba exists
        if not hasattr(self, 'last_eba'):
            self.last_eba = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_input_forces(self, salience: float, confidence: float, novelty: float) -> np.ndarray:
        return np.array([
            self.m0.compute_input_force({'salience': salience, 'confidence': confidence, 'novelty': novelty}),
            self.m1.compute_input_force({'salience': salience, 'identity_alignment': 0.7}),
            self.m2.compute_input_force({'salience': salience, 'identity_impact': 0.5}),
            0.0,
            0.0,
            0.0,
            0.0,
            self.m7.compute_input_force(None),
        ], dtype=float)

    def _apply_state_to_channels(self) -> None:
        channels = [self.m0, self.m1, self.m2, self.m3, self.m4, self.m5, self.m6, self.m7]
        for idx, ch in enumerate(channels):
            ch.state.phase = float(self.state.phases[idx] % (2 * np.pi))
            ch.velocity = float(self.state.velocities[idx])
        self.identity_field.phase = float(self.state.identity_phase % (2 * np.pi))

    def _step_dynamics(self, salience: float, confidence: float, novelty: float, dt: float) -> None:
        input_forces = self._build_input_forces(salience, confidence, novelty)
        self.state = self.dynamics.integrate(1, dt, input_forces=input_forces, initial_state=self.state)
        self.current_time = self.state.time
        self._apply_state_to_channels()

    @staticmethod
    def _normalize_content(content: Any) -> str:
        if isinstance(content, dict):
            return str(content.get('content', content))
        return str(content)

    def _make_episode(self, content: Any, metadata: Dict[str, Any]) -> Episode:
        content_text = self._normalize_content(content)
        phase = float(metadata.get('phase', self.m2.state.phase))
        context = dict(metadata.get('context', {}))
        for key in ('goal', 'action', 'task', 'objective', 'modality', 'polarity'):
            if key in metadata and key not in context:
                context[key] = metadata[key]
        result = metadata.get('result')
        salience = float(np.clip(metadata.get('salience', 0.7), 0.0, 1.0))
        identity_impact = float(np.clip(metadata.get('identity_impact', 0.5), 0.0, 1.0))
        episode = Episode(
            content=content_text,
            context=context,
            result=result,
            timestamp=float(metadata.get('timestamp', self.current_time)),
            phase_at_storage=phase,
            salience=salience,
            identity_impact=identity_impact,
        )
        self.m2.episodes.append(episode)
        self.m2._by_timestamp[episode.timestamp] = episode
        phase_bin = int(episode.phase_at_storage * 10) / 10.0
        self.m2._by_phase.setdefault(phase_bin, []).append(episode)

        # Index into orbital shell — track attractor phase from identity field
        self.orbital_index.attractor_phase = self.identity_field.phase
        self._orbital_record_counter += 1
        orec = OrbitalRecord.from_phase(
            record_id=f"ep_{self.cycle_index}_{self._orbital_record_counter}",
            content=episode,
            phi_record=episode.phase_at_storage,
            phi_attractor=self.identity_field.phase,
            p_phase=float(np.clip(episode.salience, 0.0, 1.0)),
            source_module="M2",
            confidence=episode.consolidation_score or episode.salience,
            timestamp=episode.timestamp,
        )
        self.orbital_index.insert(orec)
        if self.m2._should_consolidate(episode):
            self.m2.consolidation_candidates.append(len(self.m2.episodes) - 1)
        return episode

    def _current_eba_defect(self) -> float:
        """Mean EBA defect magnitude from the last loop evaluation (previous cycle)."""
        if not self.last_eba:
            return 0.5
        defects = [ev.defect_magnitude for ev in self.last_eba.values()]
        return float(np.mean(defects)) if defects else 0.5

    def _update_semantic(self, episode: Episode, current_time: float, events: ConsolidationEvents) -> Optional[str]:
        trace = self.m3.observe_episode(episode, eba_defect=self._current_eba_defect())
        key = trace.semantic_key
        candidate = self.m3.check_semantic_candidate_creation(key)
        if candidate:
            events.semantic_candidate = key
            self.m8.log_decision(f"Semantic candidate detected: {key}", metadata={'channel': 'M3', 'score': self.m3.compute_consolidation_score(key).compute_total()})
            if candidate.is_mature(
                self.m3.MIN_CONFIRMATIONS,
                self.m3.MIN_MATURE_ALIGNMENT,
                self.m3.MIN_MATURE_STABILITY,
                self.m3.MAX_CONTRADICTION,
            ):
                item = self.m3.consolidate_candidate(key, current_time)
                if item:
                    events.semantic_item = key
                    self.m8.log_promotion(item.canonical_text, 2, 3, item.confidence, 'semantic consolidation')
        return key

    def _update_procedural(self, episode: Episode, current_time: float, events: ConsolidationEvents) -> Optional[str]:
        trace = self.m4.observe_episode(episode)
        key = trace.procedure_key
        candidate = self.m4.check_candidate_creation(key)
        if candidate:
            events.procedural_candidate = key
            self.m8.log_decision(f"Procedural candidate detected: {key}", metadata={'channel': 'M4', 'score': self.m4.compute_consolidation_score(key).compute_total()})
            if candidate.is_mature(
                self.m4.MIN_CONFIRMATIONS,
                self.m4.MIN_MATURE_ALIGNMENT,
                self.m4.MIN_MATURE_STABILITY,
                self.m4.MIN_SUCCESS_RATE,
                self.m4.MAX_CONTRADICTION,
            ):
                item = self.m4.consolidate_candidate(key, current_time)
                if item:
                    events.procedural_item = key
                    self.m8.log_promotion(item.canonical_action, 2, 4, item.confidence, 'procedural consolidation')
        return key

    def _update_affective(self, episode: Episode, current_time: float, events: ConsolidationEvents) -> Optional[str]:
        trace = self.m5.observe_episode(episode)
        key = trace.affective_key
        candidate = self.m5.check_candidate_creation(key)
        if candidate:
            events.affective_candidate = key
            self.m8.log_decision(f"Affective candidate detected: {key}", metadata={'channel': 'M5', 'score': self.m5.compute_consolidation_score(key).compute_total()})
            if candidate.is_mature(
                self.m5.MIN_CONFIRMATIONS,
                self.m5.MIN_MATURE_ALIGNMENT,
                self.m5.MIN_MATURE_STABILITY,
                self.m5.MAX_CONTRADICTION,
            ):
                item = self.m5.consolidate_candidate(key, current_time)
                if item:
                    events.affective_item = key
                    self.m8.log_promotion(item.canonical_text, 2, 5, item.confidence, 'affective consolidation')
        return key

    def _update_identity_and_braid(self, current_time: float, episode: Episode, events: ConsolidationEvents, metadata: Dict[str, Any]) -> None:
        self.m6.observe_identity_field(current_time)
        anchor_key = metadata.get('anchor_key')
        if anchor_key:
            candidate = self.m6.check_anchor_candidate_creation(current_time, str(anchor_key), self.identity_field.phase)
            if candidate is not None:
                events.identity_candidate = candidate.anchor_key
                self.m8.log_decision(f"Identity candidate detected: {candidate.anchor_key}", metadata={'channel': 'M6', 'confirmations': candidate.candidate_confirmation_count})
        braid_payload = {
            'episode_timestamp': episode.timestamp,
            'phase_vector': self.state.phases.copy().tolist(),
            'content': episode.content,
        }
        self.m7.update_phase_history()
        self.m7.store(braid_payload, {'timestamp': current_time})
        events.braid_recorded = True

    def _evaluate_loops(self) -> Dict[str, EBAEvaluation]:
        results: Dict[str, EBAEvaluation] = {}
        hidden = self.state.phases.copy()
        for loop_name, seq in self.loops.items():
            phases = [float(self.state.phases[ch]) for ch in seq]
            timestamps = [self.current_time + i * 1e-3 for i in range(len(seq))]
            loop = create_loop_from_trajectory(seq, phases, timestamps=timestamps, loop_type=loop_name)
            res = self.holonomy.compute_eba_defect(loop, hidden_states=hidden)
            results[loop_name] = EBAEvaluation(
                loop_type=loop_name,
                epsilon_eba=float(res['epsilon_eba']),
                defect_magnitude=float(res['defect_magnitude']),
                is_coherent=bool(res['is_coherent']),
                phi_dyn=float(res['phi_dyn']),
                phi_berry=float(res['phi_berry']),
                phi_ab=float(res['phi_ab']),
                nu_e=int(res['nu_e']),
            )
            if not res['is_coherent']:
                self.m8.log_defect(7, 'eba', float(res['defect_magnitude']), f"{loop_name} loop defect")
        self.last_eba = results
        return results

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process_input(self, content: Any, metadata: Optional[Dict[str, Any]] = None, dt: float = 0.1) -> OrchestratorCycleResult:
        metadata = dict(metadata or {})
        normalized_content = self._normalize_content(content)
        salience = float(np.clip(metadata.get('salience', 0.7), 0.0, 1.0))
        confidence = float(np.clip(metadata.get('confidence', 0.7), 0.0, 1.0))
        novelty = float(np.clip(metadata.get('novelty', 0.7), 0.0, 1.0))

        self._step_dynamics(salience, confidence, novelty, dt)

        current_time = float(metadata.get('timestamp', self.current_time))
        modality = str(metadata.get('modality', 'text'))

        m0_trace = self.m0.observe(normalized_content, current_time, modality=modality,
                                   phase=self.m0.state.phase, salience=salience,
                                   confidence=confidence)
        m1_trace = self.m1.observe(normalized_content, current_time,
                                   phase=self.m1.state.phase, salience=salience,
                                   confidence=confidence, source_ids=[m0_trace.source_id])

        # Drain M1 consolidation queue — traces that aged out of working memory
        # are promoted to M2 episodic rather than silently evicted
        for pending in self.m1._pending_consolidation:
            pending_meta = {
                'timestamp': pending.timestamp,
                'phase': pending.phase,
                'salience': pending.salience,
                'confidence': pending.confidence,
                'modality': 'consolidated',
                'source': 'M1_overflow',
            }
            self._make_episode(pending.content, pending_meta)
            self.m8.log_decision(
                f"M1 overflow consolidation: {pending.working_key[:40]}",
                metadata={'channel': 'M1', 'reason': 'trace_window_overflow'},
            )
        self.m1._pending_consolidation.clear()

        metadata.setdefault('phase', self.m2.state.phase)
        metadata.setdefault('timestamp', current_time)
        metadata.setdefault('identity_impact', max(m0_trace.identity_alignment, m1_trace.identity_alignment))
        episode = self._make_episode(content, metadata)

        events = ConsolidationEvents()
        semantic_key = self._update_semantic(episode, current_time, events)
        procedural_key = self._update_procedural(episode, current_time, events)
        affective_key = self._update_affective(episode, current_time, events)
        self._update_identity_and_braid(current_time, episode, events, metadata)

        # Weak phase coupling: gently attract channel phases toward target_phase
        # from orbital (passed via metadata). Coupling strength κ=0.02 — non-invasive.
        target_phase = float(metadata.get('target_phase', 0.0))
        if target_phase != 0.0:
            _kappa = 0.02
            _diff = (target_phase - self.state.phases + np.pi) % (2 * np.pi) - np.pi
            self.state.phases = self.state.phases + _kappa * _diff

        eba = self._evaluate_loops()
        stability = self.dynamics.compute_stability_metrics(self.state)
        energy = stability['energy']
        defects = {
            'D_mem': float(stability.get('D_mem', 0.0)),
            'D_id': float(stability.get('D_id', 0.0)),
            'mean_coherence': float(stability.get('mean_coherence', 0.0)),
        }

        self.cycle_index += 1
        self.m8.log_decision(
            f"Processed cycle {self.cycle_index}",
            orchestrator_state={
                'cycle': self.cycle_index,
                'content': normalized_content,
                'semantic_key': semantic_key,
                'procedural_key': procedural_key,
                'affective_key': affective_key,
                'energy': {k: float(v) if isinstance(v, (int, float, np.floating)) else v for k, v in energy.items() if k != 'static_components'},
                'defects': defects,
            },
        )

        notes: List[str] = []
        if events.semantic_item:
            notes.append('semantic_consolidated')
        if events.procedural_item:
            notes.append('procedural_consolidated')
        if events.affective_item:
            notes.append('affective_consolidated')
        if events.identity_candidate:
            notes.append('identity_candidate_detected')

        return OrchestratorCycleResult(
            cycle_index=self.cycle_index,
            timestamp=current_time,
            content=normalized_content,
            perceptual_key=m0_trace.percept_key,
            working_key=m1_trace.working_key,
            episode_timestamp=episode.timestamp,
            semantic_key=semantic_key,
            procedural_key=procedural_key,
            affective_key=affective_key,
            consolidations=events,
            eba_results=eba,
            energy={
                'V_static': float(energy['V_static']),
                'R_noise': float(energy['R_noise']),
                'V_EBA_diag': float(energy['V_eba_diag']),
                'E_monitor': float(energy['E_monitor']),
            },
            defects=defects,
            notes=notes,
        )

    def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Orbital-shell retrieve — inter-shell transition, not sequential scan.

        Query phase is estimated from the identity field's current phase plus
        a perturbation proportional to query hash.  The orbital index returns
        records whose binding energy is closest to the query's orbital energy,
        expanding to neighbouring shells until top_k candidates are found.

        Falls back to legacy retrieve for channels not yet indexed (M0/M1/M3-M5).
        """
        # Estimate query phase: hash the string into [-π, π]
        q_hash = hash(query) & 0xFFFFFF
        phi_query = self.identity_field.phase + (q_hash / 0xFFFFFF - 0.5) * math.pi
        phi_query = (phi_query + math.pi) % (2 * math.pi) - math.pi

        self.orbital_index.attractor_phase = self.identity_field.phase
        orbital_records = self.orbital_index.retrieve(phi_query, n=top_k)

        # Unpack episodes from orbital records
        orbital_episodes = []
        for orec in orbital_records:
            orbital_episodes.append({
                'record_id': orec.record_id,
                'shell': orec.shell,
                'shell_name': ['K','L','M','N','O','P','Q','R','S'][orec.shell],
                'E_bind': round(orec.E_bind, 4),
                'r_phase': round(orec.r_phase, 4),
                'condensed': orec.condensed,
                'source_module': orec.source_module,
                'confidence': orec.confidence,
                'content': str(orec.content.content) if hasattr(orec.content, 'content') else str(orec.content),
            })

        return {
            'orbital': orbital_episodes,
            'shell_summary': self.orbital_index.shell_summary(),
            # Legacy channels — still useful for structured queries
            'perceptual': self.m0.retrieve(query, top_k=top_k, include_decayed=True),
            'working': self.m1.retrieve(query, top_k=top_k, include_decayed=True),
            'semantic': self.m3.retrieve(query, self.identity_field, top_k=top_k),
        }

    def retrieve_legacy(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Full sequential retrieve across all channels (pre-orbital)."""
        return {
            'perceptual': self.m0.retrieve(query, top_k=top_k, include_decayed=True),
            'working': self.m1.retrieve(query, top_k=top_k, include_decayed=True),
            'episodic': self.m2.retrieve({'recent': top_k}),
            'semantic': self.m3.retrieve(query, self.identity_field, top_k=top_k),
            'procedural': self.m4.retrieve(query, self.identity_field, top_k=top_k),
            'affective': self.m5.retrieve(query, self.identity_field, top_k=top_k),
        }

    def snapshot(self) -> OrchestratorSnapshot:
        stability = self.dynamics.compute_stability_metrics(self.state)
        energy = stability['energy']
        counts = {
            'm0_items': len(self.m0.items),
            'm1_items': len(self.m1.items),
            'm2_episodes': len(self.m2.episodes),
            'm3_items': len(self.m3.items),
            'm4_items': len(self.m4.items),
            'm5_items': len(self.m5.items),
            'm6_candidates': len(self.m6.anchor_candidates),
            'm7_units': len(self.m7.units),
            'm8_entries': len(self.m8.entries),
        }
        latest_loop_status = {name: res.is_coherent for name, res in self.last_eba.items()}
        return OrchestratorSnapshot(
            timestamp=self.current_time,
            cycle_index=self.cycle_index,
            identity_phase=self.identity_field.phase,
            energy={
                'V_static': float(energy['V_static']),
                'R_noise': float(energy['R_noise']),
                'V_EBA_diag': float(energy['V_eba_diag']),
                'E_monitor': float(energy['E_monitor']),
            },
            defects={
                'D_mem': float(stability.get('D_mem', 0.0)),
                'D_id': float(stability.get('D_id', 0.0)),
                'mean_coherence': float(stability.get('mean_coherence', 0.0)),
            },
            counts=counts,
            latest_loop_status=latest_loop_status,
        )

    def run_sequence(self, events: List[Dict[str, Any]], dt: float = 0.1) -> List[OrchestratorCycleResult]:
        results = []
        for event in events:
            content = event.get('content', '')
            metadata = {k: v for k, v in event.items() if k != 'content'}
            results.append(self.process_input(content, metadata, dt=dt))
        return results
