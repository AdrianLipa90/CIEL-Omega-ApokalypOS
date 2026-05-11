import type { Layer } from "./modules";

export interface DemoStep {
  step: number;
  description: string;
}

export interface Demo {
  id: string;
  name: string;
  file: string;
  description: string;
  layers: Layer[];
  steps: DemoStep[];
}

export const DEMOS: Demo[] = [
  {
    id: "demo-complete",
    name: "Complete CIEL/Ω System",
    file: "demo_ciel_omega_complete.py",
    description:
      "The unified system demo. Runs the full 8-layer consciousness pipeline end-to-end with a single text intention. Returns a complete output including emotional profile, vocabulary metrics, planetary archetype, and ethics evaluation.",
    layers: ["Core Physics", "Emotion & CQCL", "Cognition", "Ethics", "Memory", "LLM Runtime", "Mathematics", "Vocabulary", "Bio & Sensing"],
    steps: [
      { step: 1, description: "Instantiate CompleteCIELOmegaSystem() with default configuration" },
      { step: 2, description: "[Layer 1] CQCL compiles 'Kocham życie' → joy=0.50, love=0.50, 301-step Collatz path" },
      { step: 3, description: "[Layer 2] Ψ field initialized (48×48), Σ=0.047, Coherence=0.314" },
      { step: 4, description: "[Layer 3] Reality Laws applied: R(S,Ψ)=0.0002, Interference=mixed, Entanglement evaluated" },
      { step: 5, description: "[Layer 4] Ethics Guard: ERI=0.0001 → CORRECTION applied to Ψ" },
      { step: 6, description: "[Layer 5] Cognition: Conscious awareness=True, Decision=respond" },
      { step: 7, description: "[Layer 6] Affective: Mood=0.900, Planet=Earth (Schumann 7.83 Hz)" },
      { step: 8, description: "[Layer 7] Ω-Drift: Schumann sync active, Σ nudged 0.047→0.046" },
      { step: 9, description: "[Layer 8] Memory saved, Lie₄ invariants computed, output synchronized" },
    ],
  },
  {
    id: "demo-unified-euler",
    name: "Unified Euler Integration",
    file: "demo_unified_euler.py",
    description:
      "Demonstrates the EBA (Euler-Braid-Affective) closure constraint system running over a text cycle. Shows sector-wise phase closure metrics for memory, core, vocabulary, and affect channels, with active correction and rollback.",
    layers: ["Core Physics", "Memory", "Vocabulary"],
    steps: [
      { step: 1, description: "UnifiedSystem.create(identity_phase=0.25) — bridge and orchestrator instantiated" },
      { step: 2, description: "run_text_cycle('Euler-constraint integration test.', metadata={salience:0.8, confidence:0.76, novelty:0.61})" },
      { step: 3, description: "EBA constraint evaluates: memory closure, core closure, vocabulary closure, affect closure" },
      { step: 4, description: "Pairwise phase tension computed between all sector pairs" },
      { step: 5, description: "Active correction applied only where closure metric improves; rollback otherwise" },
      { step: 6, description: "print(out['euler_metrics']) — unified closure score, sector reports, correction log" },
    ],
  },
  {
    id: "demo-holonomic",
    name: "Holonomic Memory Orchestrator",
    file: "demo_holonomic_orchestrator.py",
    description:
      "Exercises the full 9-channel memory stack (M0–M8) through the HolonomicMemoryOrchestrator. Demonstrates cross-channel synchronization, holonomy residual computation, and EBA loop integration.",
    layers: ["Memory", "Core Physics"],
    steps: [
      { step: 1, description: "Initialize HolonomicMemoryOrchestrator with all 9 channels (M0–M8)" },
      { step: 2, description: "Feed 5 sequential field state snapshots through M0 PerceptualMemory" },
      { step: 3, description: "Consolidation cascade: M0 → M1 WorkingMemory → M2 Episodic" },
      { step: 4, description: "Holonomy residual computed from the closed loop in configuration space" },
      { step: 5, description: "M7 BraidInvariantMemory updated with linking numbers and scars" },
      { step: 6, description: "M8 AuditJournal appended with the full cycle record (SQLite)" },
      { step: 7, description: "EBA loop integration evaluated — conservative/non-coherent in demo conditions (known limit)" },
    ],
  },
  {
    id: "demo-m0-perceptual",
    name: "M0 Perceptual Memory",
    file: "demo_m0_perceptual_memory.py",
    description:
      "Isolated demo of the M0 PerceptualMemory channel. Shows rapid field snapshot ingestion, short-term retention behavior, and the consolidation trigger threshold to M1 WorkingMemory.",
    layers: ["Memory"],
    steps: [
      { step: 1, description: "Initialize PerceptualMemory with retention window configuration" },
      { step: 2, description: "Ingest 10 rapid Ψ field snapshots at simulated 50ms intervals" },
      { step: 3, description: "Observe automatic expiry of snapshots beyond retention window" },
      { step: 4, description: "Consolidation threshold reached → transfer most salient snapshots to M1" },
      { step: 5, description: "Verify M0 buffer cleared and M1 working memory updated" },
    ],
  },
  {
    id: "demo-m3-semantic",
    name: "M3 Semantic Memory",
    file: "demo_m3_semantic_memory.py",
    description:
      "Demonstrates semantic memory storage and retrieval. Processed concepts are mapped to vocabulary ontology entries and stored in M3. Shows symbol-grounded retrieval via the vocabulary_tools resolver.",
    layers: ["Memory", "Vocabulary"],
    steps: [
      { step: 1, description: "Run text cycle: 'Resonance between conscious fields'" },
      { step: 2, description: "CQCL extracts semantic tokens: [Resonance, conscious, fields]" },
      { step: 3, description: "SymbolResolver maps tokens to vocabulary entries: R(Ψ₁,Ψ₂) = entry 001" },
      { step: 4, description: "SemanticMemory stores concept-to-vocabulary bindings with ERI context" },
      { step: 5, description: "Retrieval query: 'concepts related to resonance' → returns M3 entries with similarity scores" },
    ],
  },
  {
    id: "demo-m5-affective",
    name: "M5 Affective-Ethical Memory",
    file: "demo_m5_affective_memory.py",
    description:
      "Demonstrates the Affective-Ethical Memory channel. Shows how ERI scores and affective state traces are stored longitudinally, and how the Ethics Guard uses them to detect behavioral drift.",
    layers: ["Memory", "Ethics"],
    steps: [
      { step: 1, description: "Run 5 text cycles with varying emotional inputs" },
      { step: 2, description: "Each cycle: ERI score and affective vector stored in M5 with timestamp" },
      { step: 3, description: "EthicsGuard queries M5 for longitudinal ERI trend (last 10 entries)" },
      { step: 4, description: "Trend analysis: if ERI declining → preemptive correction applied before processing" },
      { step: 5, description: "M8 AuditJournal records all Ethics Guard interventions with M5 context" },
    ],
  },
  {
    id: "demo-vocabulary-resolve",
    name: "Vocabulary Resolve",
    file: "demo_vocabulary_resolve.py",
    description:
      "Exercises the 115-entry Vocabulary of Consciousness. Resolves symbols to their mathematical definitions, demonstrates planetary archetype assignment, and verifies all vocabulary entries load correctly.",
    layers: ["Vocabulary", "Bio & Sensing"],
    steps: [
      { step: 1, description: "VocabularyOrchestrator.load() — 115 entries loaded from core, extended, field_dynamics, transcendent, planetary_archetypes" },
      { step: 2, description: "SymbolResolver.resolve('R') → entry 001: R(Ψ₁,Ψ₂) = |⟨Ψ₁|Ψ₂⟩|² / (‖Ψ₁‖·‖Ψ₂‖)" },
      { step: 3, description: "SymbolResolver.resolve('ERI') → entry 005: ERI = R·A·S" },
      { step: 4, description: "SymbolResolver.resolve('Love') → entry 006: Love = lim_{t→∞} R(Ψᵢ,Ψⱼ)" },
      { step: 5, description: "PlanetaryArchetypes.from_eeg(delta=0.8) → Jupiter archetype assigned" },
      { step: 6, description: "All 115 entries verified — no missing definitions" },
    ],
  },
  {
    id: "demo-m6-identity",
    name: "M6 Identity Memory",
    file: "demo_m6_identity_memory.py",
    description:
      "Demonstrates the identity trace memory layer. Shows how the stable self-model (Σ trajectory) is maintained across sessions and how Ω-Drift accumulates without resetting identity.",
    layers: ["Memory", "Core Physics"],
    steps: [
      { step: 1, description: "Initialize IdentityMemory with identity_phase=0.25 and Σ₀=0.050" },
      { step: 2, description: "Run 20 processing cycles, each nudging Σ by RCDE calibration" },
      { step: 3, description: "Observe monotonic drift: Σ trajectory 0.050 → 0.038 over 20 cycles" },
      { step: 4, description: "Session end: identity state serialized to M6.1a identity trace store" },
      { step: 5, description: "New session: load M6 → UnifiedSystem restores Σ=0.038 without reset" },
      { step: 6, description: "Verify Ω-Drift continuity: post-load behavior consistent with pre-serialization" },
    ],
  },
];
