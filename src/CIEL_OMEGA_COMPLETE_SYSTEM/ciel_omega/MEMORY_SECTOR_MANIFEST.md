CIEL/Omega Memory Sector - Consolidated Runtime
Version: v3.1.7_MEMORY_SECTOR_COMPLETE

Included runtime channels:
- M0 PerceptualMemory
- M1 WorkingMemory
- M2 EpisodicMemory
- M3 SemanticMemory
- M4 ProceduralMemory
- M5 AffectiveEthicalMemory
- M6.1a IdentityMemory (identity trace memory layer)
- M7 BraidInvariantMemory
- M8 AuditJournalMemory

Included core:
- memory/base.py
- memory/coupling.py
- memory/potential.py
- memory/dynamics.py
- memory/holonomy.py
- memory/orchestrator.py
- memory/orchestrator_types.py

Included demos/tests:
- demo_holonomic_orchestrator.py
- test_holonomic_orchestrator.py
- test_memory_sector_integration.py
- plus per-channel demos/tests

Known limits:
- HolonomicMemoryOrchestrator exists and runs, but EBA loops remain conservative / often non-coherent in demo runs.
- TODO/vocabulary is present as semantic backlog, not runtime dependency.
- Legacy top-level demos (demo_full_pipeline.py, demo_ciel_omega_complete.py) remain historical and are not the authoritative memory entrypoints.
