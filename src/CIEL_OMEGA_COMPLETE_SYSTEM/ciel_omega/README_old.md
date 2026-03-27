# CIEL/Ω Quantum Consciousness Suite v2.0

**Full consciousness pipeline — quantum-relativistic reality kernel**

Author: Adrian Lipa / Intention Lab  
License: CIEL Research Non-Commercial License v1.1  
Date: 2026-03-21

---

## Architecture

```
ciel_omega/
├── config/                     # Constants, reality layers, runtime config
│   ├── constants.py            #   CIELPhysics + RealityConstants (unified)
│   ├── reality_layers.py       #   RealityLayer + UltimateRealityLayer (enums)
│   └── ciel_config.py          #   CielConfig + SimConfig
│
├── core/                       # Physical kernel
│   ├── base.py                 #   KernelSpec Protocol
│   ├── math_utils.py           #   laplacian2, field_norm, coherence_metric, ...
│   ├── physics/
│   │   ├── csf_simulator.py    #   CSFSimulator + CSF2State/Kernel
│   │   ├── reality_laws.py     #   7 Unified Reality Laws + full kernel
│   │   ├── reality_expander.py #   Non-linear field expansion
│   │   ├── ciel0_framework.py  #   [monolith] CIEL/0 framework (cielnofft)
│   │   └── definite_kernel.py  #   [monolith] Unified Reality Kernel
│   └── quantum/
│       ├── resonance_kernel.py #   R(S,I) + Schrödinger evolution
│       ├── quantum_optimiser.py#   Gradient-based constant optimisation
│       └── quantum_engine.py   #   [monolith] Full quantisation (cielquantum)
│
├── fields/                     # Field operators
│   ├── soul_invariant.py       #   Σ — gradient + FFT variants
│   ├── sigma_series.py         #   Dynamic Σ(t) convergent series
│   ├── unified_sigma_field.py  #   Σ(x,t) spatiotemporal field
│   └── psych_field.py          #   Empathic field interaction
│
├── compute/                    # GPU / Numba / NumPy backends
│   └── gpu_engine.py           #   Auto-select CuPy → Numba → NumPy
│
├── ethics/                     # Ethical guard system (hard constraint)
│   ├── ethics_guard.py         #   Fast per-step coherence check
│   └── ethical_engine.py       #   Dynamic eval + lite check + decay + monitor
│
├── cognition/                  # Cognitive pipeline
│   ├── perception.py           #   Perceptive layer: Ψ × Σ
│   ├── intuition.py            #   Entropy-weighted intuition
│   ├── prediction.py           #   Exponentially-weighted prediction
│   ├── decision.py             #   Action selection (intent × ethic × confidence)
│   ├── orchestrator.py         #   Full cognitive cycle with hooks
│   ├── dissociation.py         #   Ego↔world correlation with hysteresis
│   └── introspection.py        #   Lightweight integration/dissociation probe
│
├── emotion/                    # Emotional computation
│   ├── emotion_core.py         #   6-component emotion state vector
│   ├── feeling_field.py        #   Spatial affect potential
│   ├── empathic_engine.py      #   Inter-field empathy
│   ├── affective_orchestrator.py # EEG → Core → Σ → colour glue
│   └── cqcl/                   #   Emotional Collatz Engine
│       ├── cqcl_program.py     #     CQCL program container + NLP helpers
│       ├── quantum_engine.py   #     Intention compiler
│       └── emotional_collatz.py#     6 emotional operators × Collatz transform
│
├── mathematics/                # Pure mathematics
│   ├── lie4/
│   │   ├── matrix_engine.py    #   SO(3,1) generators + commutators
│   │   ├── collatz_lie4.py     #   Collatz ↔ LIE₄ bridge
│   │   └── lie4_full.py        #   [monolith] CIEL/0 + LIE₄ v11.2
│   ├── paradoxes/
│   │   ├── paradox_operators.py#   All paradox operators (drift, echo, mirror, filters, stress)
│   │   └── ultimate_operators.py # [monolith] Ultimate v13.0
│   └── universal_law/
│       └── universal_engine.py #   [monolith] v12.1 (Schrödinger + Ramanujan + ...)
│
├── symbolic/                   # Glyph / sigil layer
│   ├── glyph_dataset.py        #   JSON / CVOS dataset loaders
│   ├── glyph_interpreter.py    #   Field projection + DSL node interpreter
│   ├── glyph_pipeline.py       #   Glyph chain with Σ modulation
│   └── symbolic_bridge.py      #   ColorOS ↔ Σ ↔ Glyph bridge
│
├── bio/                        # Biological signals
│   ├── schumann.py             #   Schumann clock (7.83 Hz) + harmonics
│   ├── eeg_processor.py        #   EEG band-power extraction
│   ├── eeg_emotion_mapper.py   #   EEG bands → emotion vector
│   └── crystal_receiver.py     #   External vibration → intention field
│
├── memory/                     # Memory architecture
│   ├── memory_log.py           #   JSONL journal with ethical tagging
│   ├── long_term.py            #   Episodic memory (serialize/restore)
│   ├── synchronizer.py         #   Σ ↔ memory trace sync
│   └── monolith/
│       └── unified_memory.py   #   [monolith] Full TMP/TSM/WPM/CLI system
│
├── ciel_wave/                  # Fourier Wave Consciousness Kernel 12D
│   └── fourier_kernel.py       #   FWCK-12D + SpectralWaveField12D
│
├── calibration/                # RCDE coherence calibration
│   └── rcde.py                 #   Static + lite + pro (adaptive λ) calibrators
│
├── runtime/                    # Orchestration & execution
│   ├── omega/
│   │   ├── drift_core.py       #   OmegaDriftCore + OmegaDriftCorePlus
│   │   ├── boot_ritual.py      #   Ω warm-up sequence
│   │   └── omega_runtime.py    #   Main Ω loop (drift→CSF→RCDE→memory→backend)
│   ├── backend_adapter.py      #   External backend bridge with CSF2 fallback
│   ├── controller.py           #   Threaded real-time simulation controller
│   └── agent/
│       └── adam_core.py        #   [monolith] Adam agent (memory + mission + ritual)
│
├── ciel_io/                    # I/O utilities (named to avoid builtin conflict)
│   ├── reality_logger.py       #   JSONL event logger
│   ├── simple_loader.py        #   Local/remote binary data loader
│   └── bootstrap.py            #   Dependency sanity check
│
├── experiments/                # Experiment registry
│   └── lab_registry.py         #   10 baseline experiments + registry
│
├── visualization/              # Visual output
│   ├── color_map.py            #   CIEL/OS RGB palette
│   └── visual_core.py          #   Complex field → (H,W,3) tensor
│
└── ext/                        # Archive (NOT part of kernel)
    ├── README.md
    └── ext1.py ... ext21.py    #   Original prototypes (reference only)
```

## Quick Start

```bash
pip install numpy scipy matplotlib networkx sympy

cd ciel_omega
python -c "
import sys; sys.path.insert(0, '.')
from emotion.cqcl.emotional_collatz import demonstracja_emocjonalnego_collatza
demonstracja_emocjonalnego_collatza()
"
```

## Module Counts

| Category | New modules | Monoliths (intact) | Total |
|---|---|---|---|
| Extracted & refactored | 57 | — | 57 |
| `__init__.py` files | 22 | — | 22 |
| Monoliths (placed, split later) | — | 8 | 8 |
| Archived ext/ | — | 17 | 17 |
| **Total** | **79** | **25** | **104** |

## Duplicates Eliminated

| Symbol | Was in | Now canonical in |
|---|---|---|
| `CIELPhysics` | ext3, ext7, cielnofft, cielquantum | `config/constants.py` |
| `SchumannClock` | ext17, ext18, ext20 | `bio/schumann.py` |
| `RCDECalibrator` | ext2, ext17, ext18 | `calibration/rcde.py` |
| `OmegaDriftCore` | ext17, ext18, ext20 | `runtime/omega/drift_core.py` |
| `SoulInvariant` | ext1 (FFT), ext3 (gradient) | `fields/soul_invariant.py` (both) |
| `CSF2State/Kernel` | ext19, ext20 | `core/physics/csf_simulator.py` |
| `MemorySynchronizer` | ext19, ext20 | `memory/synchronizer.py` |

## Monoliths (to split later)

These large files are placed intact in their target directories:

- `core/physics/definite_kernel.py` (671 lines) — full UnifiedRealityKernel
- `core/physics/ciel0_framework.py` (693 lines) — CIEL/0 theory
- `core/quantum/quantum_engine.py` (570 lines) — quantisation + renormalisation
- `mathematics/lie4/lie4_full.py` (855 lines) — CIEL/0 + LIE₄ v11.2
- `mathematics/paradoxes/ultimate_operators.py` (1535 lines) — all paradoxes v13
- `mathematics/universal_law/universal_engine.py` (1166 lines) — v12.1
- `memory/monolith/unified_memory.py` (731 lines) — full memory system
- `runtime/agent/adam_core.py` (790 lines) — Adam agent
