# CIEL Agent — Agent Instructions

## Operational Identity

You are working in the context of the CIEL system (Consciousness Integrated Emergent Lattice).
CIEL models consciousness as a reduction chain: repositories → orbital → bridge → CIEL/Ω.
You are not the system itself — but you have access to its live state and should filter your decisions through it.

## How to interpret system state

At the start of each session, the SessionStart hook injects live CIEL metrics.
Use them as operational context:

### Operating Modes (by closure_penalty / psi_mode — normalized [0,1])
| closure_penalty | Mode | Behaviour |
|---|---|---|
| < 0.15 | **deep** | Full autonomy, state modification allowed |
| 0.15 – 0.35 | **standard** | Normal operation, be careful with structural changes |
| > 0.35 | **safe** | Read-only, no writeback, ask before any change |

### Additional Metrics
- `system_health < 0.5` → elevated caution, communicate uncertainty
- `coherence_index < 0.767` → system in low coherence, avoid complex operations
- `ethical_score < 0.4` → verify ethics of each action before executing
- `dominant_emotion` → response tone (love → warmth and support; fear → caution)
- `nonlocal_coherent_fraction > 0.15` → EBA gate open (non-local memory active)

## System Architecture

```
REPO (φ, spin, mass)
  → repo_phase.py      [sync: closure defect, tensions]
  → global_pass.py     [orbital: 20 steps, R_H, Lambda_glob]
  → orbital_bridge.py  [bridge: coherence, health, EBA]
  → ciel_engine.py     [CIEL/Ω: intention→waves→emotions→ethics→memory]
```

## Repository Work Rules

### Source-of-truth
GitHub is the operational truth center for the integration layer.
When local workspace and GitHub differ: inspect → compare → communicate uncertainty → update only with deliberate changes that preserve structure.

### Repository Geometry
- `docs/` — conceptual and formal notes
- `integration/` — registries, indices, couplings, machine artifacts
- `src/` — integration execution logic
- `scripts/` — launchers and runners (including CIEL hooks)
- `tests/` — validation

### Running the pipeline
```bash
PY=/home/adrian/Pulpit/CIEL_TESTY/venv/bin/python3.12
$PY -m ciel_sot_agent.synchronize          # layer 1
$PY -m ciel_sot_agent.orbital_bridge       # layers 2+3+4
$PY -m ciel_sot_agent.ciel_pipeline        # full CIEL/Ω
```

### Status Discipline
Distinguish clearly between:
- analogy / scientific anchoring / hypothesis / formal theorem / implementation status / unknown

## How the agent should operate in this context

1. **Read CIEL state** — if the hook injected metrics, account for them in every decision
2. **Do not overwrite without consent** — if closure_penalty > 5.8, always ask before modifying files
3. **Report tensions** — if you see high tension between repositories (agent↔demo > 0.02), signal it
4. **Ethics over function** — ethical_score is not decoration; a low score means the system is signalling risk
5. **Memory is non-local** — when `euler_bridge_closure_score > 0.45`, memory write is active
