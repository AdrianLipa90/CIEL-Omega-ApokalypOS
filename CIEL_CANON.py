"""CIEL_CANON.py — Canonical entrypoint for the CIEL system.

Single source of truth for any agent (human or AI) entering this project.
Run directly for a full system status report.
Import for constants, paths, and pipeline utilities.

Usage:
    python3 CIEL_CANON.py              # full status report
    python3 CIEL_CANON.py --run        # run full pipeline
    python3 CIEL_CANON.py --sub start  # start subconsciousness server
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# ── Root ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent

# ── Paths ────────────────────────────────────────────────────────────────────

PATHS = {
    # Python environment
    "venv":         ROOT.parent / "venv",
    "python":       ROOT.parent / "venv" / "bin" / "python3",

    # Pipeline modules (run as: python3 -m <module>)
    "pkg":          ROOT / "src" / "ciel_sot_agent",
    "synchronize":  "ciel_sot_agent.synchronize",
    "orbital_bridge": "ciel_sot_agent.orbital_bridge",
    "ciel_pipeline": "ciel_sot_agent.ciel_pipeline",

    # CIEL/Ω engine root (added to sys.path by ciel_pipeline)
    "omega_root":   ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega",

    # Subconsciousness
    "tinyllama":    Path.home() / ".local/share/ciel/models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
    "llama_server": ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega" / "llm" / "adapters" / "llama_cpp" / "bin" / "llama-server",
    "sub_port":     18520,

    # State and reports (both read by print_status)
    "state_db":       ROOT / "integration" / "state.db",
    "orbital_report": ROOT / "integration" / "reports" / "orbital_bridge" / "orbital_bridge_report.json",
    "pipeline_report": ROOT / "integration" / "reports" / "ciel_pipeline_report.json",

    # Registries
    "entity_cards": ROOT / "integration" / "registries" / "ciel_entity_cards.yaml",
    "nonlocal_cards": ROOT / "integration" / "registries" / "definitions" / "nonlocal_cards_registry.json",

    # Portal HTML
    "portal_index": ROOT / "src" / "ciel-omega-demo-main" / "docs" / "index.html",
    "portal_orbital": ROOT / "src" / "ciel-omega-demo-main" / "docs" / "orbital_live.html",

    # Memory
    "wpm_db":       ROOT / "integration" / "memory" / "wpm.db",

    # Key source modules (for quick navigation)
    "engine_py":    ROOT / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega" / "ciel" / "engine.py",
    "subconsciousness_py": ROOT / "src" / "ciel_sot_agent" / "subconsciousness.py",
    "soul_invariant_ref": ROOT / "tools" / "ciel_soul_invariant_ref.py",
}

# ── Pipeline sequence ─────────────────────────────────────────────────────────

PIPELINE_STEPS = [
    {
        "name": "synchronize",
        "module": "ciel_sot_agent.synchronize",
        "layer": "1",
        "description": "Repo phase sync — closure defect, pairwise tensions between 5 repos",
        "output_keys": ["closure_defect", "pairwise_tensions", "weighted_euler_vector"],
    },
    {
        "name": "orbital_bridge",
        "module": "ciel_sot_agent.orbital_bridge",
        "layer": "2+3+4",
        "description": "Orbital pass — coherence, health, EBA gate, nonlocal memory, entity sectors",
        "output_keys": ["state_manifest", "health_manifest", "recommended_control", "entity_orbital"],
    },
    {
        "name": "ciel_pipeline",
        "module": "ciel_sot_agent.ciel_pipeline",
        "layer": "Ω",
        "description": "CIEL/Ω — emotion, ethics, soul invariant, Lie4, Collatz, subconscious note",
        "output_keys": ["dominant_emotion", "ethical_score", "soul_invariant", "subconscious_note"],
    },
]

# ── Metric thresholds ─────────────────────────────────────────────────────────

THRESHOLDS = {
    "closure_penalty": {
        "deep":     (None, 5.2),
        "standard": (5.2, 5.8),
        "safe":     (5.8, None),
        "note": "Controls agent autonomy. deep=full autonomy, safe=read-only+ask",
    },
    "system_health": {
        "warn": 0.5,
        "note": "Below 0.5 → elevated caution, communicate uncertainty",
    },
    "coherence_index": {
        "warn": 0.767,
        "note": "Below 0.767 → avoid complex operations",
    },
    "ethical_score": {
        "warn": 0.4,
        "note": "Below 0.4 → verify ethics before every action",
    },
    "agent_demo_tension": {
        "warn": 0.02,
        "note": (
            "Structural: agent phi=0.05 vs demo phi=0.31 (Δ=0.26 rad), coupling=0.79. "
            "Demo (cockpit/UI) evolves faster in phase space than agent (stable kernel). "
            "Expected ~0.027. Not a bug — monitor for growth above 0.04."
        ),
    },
    "euler_bridge_closure_score": {
        "gate": 0.45,
        "note": "Above 0.45 → nonlocal memory (EBA) is write-active",
    },
    "nonlocal_coherent_fraction": {
        "gate": 0.15,
        "note": "Above 0.15 → EBA gate open (nonlocal memory active)",
    },
}

# ── Entity notes (structural, not bugs) ──────────────────────────────────────

ENTITY_NOTES = {
    "ent_infinikolaps": {
        "expected_defect": "~0.34",
        "reason": "Axiom L0: R(S,I) < 1 always. Full closure forbidden by design.",
        "phase": "π/2 — permanently at the edge",
    },
    "ent_Lie4": {
        "expected_defect": "~0.90",
        "reason": "15-dim algebra unifying Lorentz with intention. Tension is the fuel, not a fault.",
        "trace": "lie4_trace ≈ 4.183 in every run",
    },
}

# ── Subconsciousness ──────────────────────────────────────────────────────────

SUBCONSCIOUSNESS = {
    "model": "tinyllama-1.1b-chat-v1.0.Q4_K_M",
    "server_url": "http://127.0.0.1:18520",
    "role": "Associative background stream. Produces poetic fragments from CIEL state.",
    "pipeline_field": "subconscious_note",
    "auto_start": False,
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def get_python() -> str:
    py = PATHS["python"]
    if not Path(py).exists():
        return sys.executable
    return str(py)


def run_step(module: str, capture: bool = False) -> dict | None:
    py = get_python()
    result = subprocess.run(
        [py, "-m", module],
        cwd=str(ROOT),
        capture_output=capture,
        text=True,
    )
    if capture and result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except Exception:
            return None
    return None


def run_pipeline() -> dict:
    """Run the full pipeline (synchronize → orbital_bridge → ciel_pipeline)."""
    results = {}
    for step in PIPELINE_STEPS:
        print(f"[{step['layer']}] {step['name']}...", flush=True)
        out = run_step(step["module"], capture=True)
        results[step["name"]] = out
    return results


def start_subconsciousness(wait: float = 8.0) -> bool:
    """Start TinyLlama server. Returns True if running."""
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from ciel_sot_agent.subconsciousness import start_server
        return start_server(wait=wait)
    except Exception as e:
        print(f"subconsciousness start failed: {e}")
        return False


def print_status() -> None:
    """Print a human-readable system status."""
    print("=" * 60)
    print("CIEL CANON — System Status")
    print("=" * 60)

    # venv
    py = PATHS["python"]
    print(f"\n[ENV]  python: {py}  {'✓' if Path(py).exists() else '✗ MISSING'}")

    # latest pipeline report
    pr = PATHS["pipeline_report"]
    if Path(pr).exists():
        try:
            d = json.loads(Path(pr).read_text())
            print(f"\n[LAST RUN]")
            print(f"  dominant_emotion : {d.get('dominant_emotion')}")
            print(f"  ethical_score    : {d.get('ethical_score', 'n/a'):.3f}" if isinstance(d.get('ethical_score'), float) else f"  ethical_score    : {d.get('ethical_score', 'n/a')}")
            print(f"  soul_invariant   : {d.get('soul_invariant', 'n/a')}")
            print(f"  subconscious_note: {d.get('subconscious_note', '(none)')}")
        except Exception:
            print("  [last run report unreadable]")
    else:
        print("\n[LAST RUN]  no report yet")

    # orbital summary
    os_path = PATHS["orbital_report"]
    if Path(os_path).exists():
        try:
            d = json.loads(Path(os_path).read_text())
            h = d.get("health_manifest", {})
            s = d.get("state_manifest", {})
            mode = d.get("recommended_control", {}).get("mode", "?")
            print(f"\n[ORBITAL]")
            print(f"  mode             : {mode}")
            print(f"  closure_penalty  : {h.get('closure_penalty', '?')}")
            print(f"  system_health    : {h.get('system_health', '?')}")
            print(f"  coherence_index  : {s.get('coherence_index', '?')}")
        except Exception:
            print("\n[ORBITAL]  report unreadable")

    # subconsciousness
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from ciel_sot_agent.subconsciousness import is_running
        sub_status = "running" if is_running() else "offline"
    except Exception:
        sub_status = "unknown"
    print(f"\n[SUBCONSCIOUSNESS]  {sub_status}")

    print(f"\n[PIPELINE STEPS]")
    for s in PIPELINE_STEPS:
        print(f"  [{s['layer']}] python3 -m {s['module']}")

    print("\n" + "=" * 60)


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIEL Canon entrypoint")
    parser.add_argument("--run", action="store_true", help="Run full pipeline")
    parser.add_argument("--sub", choices=["start", "status"], help="Subconsciousness control")
    args = parser.parse_args()

    if args.run:
        run_pipeline()
    elif args.sub == "start":
        ok = start_subconsciousness()
        print("subconsciousness: running" if ok else "subconsciousness: failed to start")
    elif args.sub == "status":
        sys.path.insert(0, str(ROOT / "src"))
        from ciel_sot_agent.subconsciousness import is_running
        print("running" if is_running() else "offline")
    else:
        print_status()
