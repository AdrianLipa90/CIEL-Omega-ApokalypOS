"""
CIEL/Ω - Vocabulary of Consciousness
Mathematical formalization of consciousness concepts

Based on: Consciousness Dictionary (Mathematical and Philosophical Edition)
Authors: Adrian Lipa, Danail Valov
Date: March 25, 2025

Complete implementation: All 115 entries integrated with CIEL/Ω architecture.
"""

from .core_concepts import (
    Resonance, Intention, Coherence, Entrainment,
    EthicalResonanceIndex, Love, Grief, Awe, Fear,
    Forgiveness, Silence, Memory, Identity, Truth, Wisdom
)
from .field_dynamics import (
    Collapse, Reintegration, Interference, Feedback, Echo,
    Amplification, Damping, Threshold, Coupling, Tuning,
    Disruption, Synchronization, PhaseDrift, Resolution, Hysteresis
)
from .planetary_archetypes import (
    PlanetarySystem, Jupiter, Saturn, Venus, Mars, Earth,
    Moon, Neptune, Uranus, Sun, Pluto
)
from .extended_concepts import (
    EvolutionaryStates, ArchetypalRoles, WaveformAI, NonHumanIntelligence
)
from .transcendent import (
    HarmonicDimensions, TranscendentHarmonics, HarmonicSentienceDoctrine
)
from .orchestrator import VocabularyOrchestrator, CROSS_REFERENCE_MAP

__all__ = [
    'Resonance', 'Intention', 'Coherence', 'Entrainment',
    'EthicalResonanceIndex', 'Love', 'Grief', 'Awe', 'Fear',
    'Forgiveness', 'Silence', 'Memory', 'Identity', 'Truth', 'Wisdom',
    'Collapse', 'Reintegration', 'Interference', 'Feedback', 'Echo',
    'Amplification', 'Damping', 'Threshold', 'Coupling', 'Tuning',
    'Disruption', 'Synchronization', 'PhaseDrift', 'Resolution', 'Hysteresis',
    'PlanetarySystem', 'Jupiter', 'Saturn', 'Venus', 'Mars', 'Earth',
    'Moon', 'Neptune', 'Uranus', 'Sun', 'Pluto',
    'EvolutionaryStates', 'ArchetypalRoles', 'WaveformAI', 'NonHumanIntelligence',
    'HarmonicDimensions', 'TranscendentHarmonics', 'HarmonicSentienceDoctrine',
    'VocabularyOrchestrator', 'CROSS_REFERENCE_MAP'
]

__version__ = '2.0.0'
__entries__ = 115

from .ethical_resonance import EthicalResonanceIndex
from .relational_medium import (
    RelationalMedium, Relation, RelationalField,
    EthicalScalarState, EthicalGradient,
)
from .ethical_decision_dynamics import (
    CandidateAction, CandidateEvaluation,
    DecisionResult, evaluate_candidate, choose_action, decision_tree_view,
)
from .ethical_stream_bridge import (
    EthicalStreamRecord, ethical_event_payload, commit_ethics_to_noema,
)
from .local_relational_ethics import (
    LocalEthicalProfile, DistributionalConsequence,
    pareto_dominates, pareto_front,
    DistributionalDecision, choose_distributionally,
)
from .relational_autonomy import (
    ConsentStatus, ConsentEvidence, active_consent,
    InformationAccess, InformationAsymmetry,
    information_asymmetry as relational_information_asymmetry,
    AgencyEvidence, CoercionEvidence,
    AutonomyProfile, derive_autonomy_profile,
    AutonomyConsequence, autonomy_dominates, autonomy_pareto_front,
    JointRelationalDecision, choose_with_autonomy,
)
from .nbody_kepler_relational import (
    RelationalBody, PairCoupling,
    unit_sphere_area,
    pair_displacement, pair_distance,
    nd_green_potential_from_r, nd_green_potential, inverse_distance_potential,
    central_pair_force, radial_flux_invariant, accelerations,
    bivector_angular_momentum, total_bivector_angular_momentum,
    kinetic_energy, potential_energy, total_energy,
    DimensionalKeplerReport, dimensional_report,
    AgencyState, ConsentGeometry, consent_geometry,
    InformationState, information_asymmetry,
)
from .nbody_kepler_canon import (
    CanonNode, DIM_GREEN, N3_KEPLER, TIR_FLUX_BINDING,
    USER_DELTA, USER_SIGMA, CANON_NODES,
)
from .nbody_kepler_noether_bridge import (
    tetrahedral_vertices, tetrahedral_first_moment, tetrahedral_second_moment,
    tetrahedral_isotropic_second_moment, radial_current_3d,
    inverse_distance_potential_from_flux,
)
from .nbody_kepler_hodge_bridge import (
    radial_green_current, rotational_holonomy_current,
    radial_component, tangential_component,
    sphere_flux_monte_carlo, SectorReport, validate_sector_superposition,
    matched_amplitude_from_phase_inertia,
)
from .nbody_kepler_u1_embedding import (
    rotor_amplitude, rotor_to_complex_field,
    scalar_noether_current_from_phase_gradient, relational_rotor_current,
    current_embedding_residual, EmbeddingReport, validate_embedding,
)
from .information_dynamics import (
    CurrentSectors, InformationFieldState,
    cell_to_face_flux, set_boundary_flux,
    divergence_from_faces, boundary_outflow,
    ContinuityReceipt, continuity_step_from_faces,
    zero_sectors, phase_rotor_current,
    radial_green_current_cells, rotational_holonomy_cells,
    J0Classification, classify_declared_J0,
    InformationDynamicsSnapshot, snapshot,
)
from .relational_information_exchange import (
    RelationalInformationNode, ExchangeReceipt,
    partition_source_density, conservative_exchange_step,
)
from .canonical_information_backreaction import (
    CanonicalRelationalState, HamiltonianGeometry,
    covariant_momentum, phase_velocity, hamiltonian, hamilton_equations,
    curvature_tensor, covariant_momentum_rate_flat_metric,
    BackreactionReceipt, backreaction_receipt,
)
from .information_phase_generator import (
    KAPPA_INFORMATION,
    information_generator_expectation,
    free_phase_hamiltonian_expectation,
    PhaseGeneratorBinding, bind_classical_J_to_information_generator,
    block_diagonal_metric, FullPhaseFirstStructure, structure_receipt,
)
