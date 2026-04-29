#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

CARDS = [
    {
        "card_id": "NL-HOLOMEM-0001",
        "name": "HolonomicMemoryOrchestrator",
        "class": "nonlocal_memory_orchestrator",
        "active_status": "ACTIVE_CANONICAL_NONLOCAL_RUNTIME",
        "anchors": [
            "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/orchestrator.py",
            "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/orchestrator_types.py",
            "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/holonomy.py",
        ],
        "role": "Canonical nonlocal memory orchestrator that computes Euler-Berry-Aharonov-Bohm loop evaluations and carries continuity across memory channels.",
        "input_from": "cleaned text + phase metadata + memory channels",
        "output_to": "OrchestratorCycleResult + eba_results + energy/defect aggregates",
        "authority_rule": "Canonical source of nonlocal memory runtime; downstream layers consume its outputs but do not override them.",
        "horizon_relation": "Internal nonlocal runtime beneath bridge projection.",
    },
    {
        "card_id": "NL-EBA-0002",
        "name": "EBA Loop Evaluation Set",
        "class": "nonlocal_phase_memory_card_set",
        "active_status": "ACTIVE_CANONICAL_NONLOCAL_CARD_SET",
        "anchors": [
            "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/orchestrator_types.py",
            "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/holonomy.py",
        ],
        "role": "Canonical card set for Euler-Berry-Aharonov-Bohm loop evaluations carried by nonlocal memory runtime.",
        "input_from": "Holonomic loop geometry + trajectory state + identity phase",
        "output_to": "loop cards with phi_ab, phi_berry, defect magnitude, coherence state, and energy/defect summaries",
        "authority_rule": "Loop cards are derived from canonical orchestrator outputs and remain subordinate to the live memory runtime.",
        "horizon_relation": "Internal card layer that becomes projected summary through bridge horizon.",
    },
    {
        "card_id": "NL-BRIDGE-0003",
        "name": "MemoryCorePhaseBridge",
        "class": "nonlocal_reduction_bridge",
        "active_status": "ACTIVE_CANONICAL_NONLOCAL_BRIDGE",
        "anchors": ["src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/bridge/memory_core_phase_bridge.py"],
        "role": "Canonical reduction bridge from nonlocal memory and phase state into Euler metrics and projected bridge state.",
        "input_from": "memory runtime + phase state + core state",
        "output_to": "euler_metrics + bridge_closure_score + target_phase + projected bridge bundle",
        "authority_rule": "Canonical reduction path for nonlocal -> Euler bridge metrics; wrappers may read but not redefine its outputs.",
        "horizon_relation": "Bridge horizon between internal nonlocal state and projected runtime/action state.",
    },
    {
        "card_id": "NL-PHASE-0004",
        "name": "PhaseInfoSystem",
        "class": "phase_dynamics_runtime",
        "active_status": "ACTIVE_CANONICAL_PHASE_RUNTIME",
        "anchors": ["src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/phase_equation_of_motion.py"],
        "role": "Canonical phase dynamics runtime carrying Collatz-forced phase evolution and fermion lock diagnostics.",
        "input_from": "collatz seed + truth target + phase parameters",
        "output_to": "R_H + fermion_lock + phase sector + collatz-forced phase evolution",
        "authority_rule": "Canonical phase dynamics source for active runtime; downstream metrics derive from it.",
        "horizon_relation": "Internal phase runtime beneath bridge projection and orbital diagnostics.",
    },
]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    args = ap.parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_dir = repo_root / 'integration' / 'registries' / 'definitions'
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {'schema': 'ciel/nonlocal-cards-registry/v0.1', 'count': len(CARDS), 'records': CARDS}
    json_path = out_dir / 'nonlocal_cards_registry.json'
    csv_path = out_dir / 'nonlocal_cards_registry.csv'
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    with csv_path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=['card_id','name','class','active_status','anchors','role','input_from','output_to','authority_rule','horizon_relation'])
        writer.writeheader()
        for rec in CARDS:
            row = rec.copy(); row['anchors'] = ';'.join(rec['anchors']); writer.writerow(row)
    print(json.dumps({'ok': True, 'count': len(CARDS), 'json': str(json_path.relative_to(repo_root)).replace('\\','/'), 'csv': str(csv_path.relative_to(repo_root)).replace('\\','/')}, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
