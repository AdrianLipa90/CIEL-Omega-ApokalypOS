from __future__ import annotations

from typing import Any, Dict

from ciel_omega.memory.orbital_holonomy import compute_consolidation_holonomy


def _base_gate_threshold(*, mode: str, severity: str) -> float:
    if severity == "high":
        return 0.72
    if mode == "deep" and severity == "low":
        return 0.52
    if severity == "low":
        return 0.58
    return 0.64


def _consolidation_profile(*, orbital: Dict[str, Any], sector_memory: Any | None, event_phase: float | None, threshold: float, require_loop_coherence: bool) -> Dict[str, Any]:
    channels = ("semantic", "procedural", "affective")
    metrics: Dict[str, Any] = {}
    allowed = []
    blocked = []
    focus = None
    best_quality = -1.0

    for channel in channels:
        if sector_memory is not None and event_phase is not None:
            hol = compute_consolidation_holonomy(channel, entry_phase=float(event_phase), holder=sector_memory, orbital=orbital)
        else:
            hol = {
                "phase_alignment": 0.0,
                "identity_attractor_score": 0.0,
                "closure_quality": 0.0,
                "eba_quality": 0.0,
                "holonomy_quality": 0.0,
                "holonomy_defect": 3.141592653589793,
                "loop_coherent": False,
                "loop_type": f"consolidation_{channel}",
                "entry_phase": float(event_phase or 0.0),
                "current_phase": 0.0,
                "orbital_phase": 0.0,
                "identity_phase": 0.0,
            }
        quality = float(hol.get("holonomy_quality", 0.0) or 0.0)
        coherent = bool(hol.get("loop_coherent", False))
        allowed_here = quality >= threshold and ((not require_loop_coherence) or coherent)
        metrics[channel] = {
            **hol,
            "allowed": allowed_here,
            "threshold": float(threshold),
        }
        if allowed_here:
            allowed.append(channel)
        else:
            blocked.append(channel)
        if quality > best_quality:
            best_quality = quality
            focus = channel

    return {
        "metrics": metrics,
        "allowed": allowed,
        "blocked": blocked,
        "focus": focus,
        "best_quality": float(best_quality if best_quality >= 0.0 else 0.0),
    }


def build_memory_governor(
    *,
    orbital: Dict[str, Any],
    runtime_policy: Dict[str, Any],
    sector_snapshot: Dict[str, Any] | None = None,
    sector_memory: Any | None = None,
    event_phase: float | None = None,
) -> Dict[str, Any]:
    final = orbital.get("final") if isinstance(orbital, dict) else {}
    control = orbital.get("control") if isinstance(orbital, dict) else {}
    rh_policy = orbital.get("rh_policy") if isinstance(orbital, dict) else {}
    snapshot = sector_snapshot or {}
    counts = snapshot.get("counts") if isinstance(snapshot, dict) else {}
    defects = snapshot.get("defects") if isinstance(snapshot, dict) else {}

    r_h = float((final or {}).get("R_H", 1.0) or 1.0)
    closure = float((final or {}).get("closure_penalty", 0.0) or 0.0)
    mean_coh = float((defects or {}).get("mean_coherence", 0.0) or 0.0)
    d_mem = float((defects or {}).get("D_mem", 0.0) or 0.0)
    m2_count = int((counts or {}).get("m2_episodes", 0) or 0)
    severity = str((rh_policy or {}).get("severity", "medium"))
    mode = str((control or {}).get("mode", "standard"))

    retrieval_top_k = 3
    retrieval_scope = "focused"
    if mode == "deep":
        retrieval_top_k = 6
        retrieval_scope = "wide"
    elif mode == "safe":
        retrieval_top_k = 2
        retrieval_scope = "narrow"

    if severity == "high":
        retrieval_top_k = min(retrieval_top_k, 2)
        retrieval_scope = "stabilize"
    elif severity == "low":
        retrieval_top_k = max(retrieval_top_k, 4)

    write_mode = "durable" if runtime_policy.get("durable_write_allowed", False) else "ephemeral"
    require_loop_coherence = severity != "low" or mode == "safe"
    gate_threshold = _base_gate_threshold(mode=mode, severity=severity)
    consolidation_profile = _consolidation_profile(
        orbital=orbital,
        sector_memory=sector_memory,
        event_phase=event_phase,
        threshold=gate_threshold,
        require_loop_coherence=require_loop_coherence,
    )

    consolidation_mode = "stabilize"
    if severity == "low" and closure < 6.0 and mean_coh >= 0.15 and consolidation_profile["allowed"]:
        consolidation_mode = "promote"
    elif severity == "medium":
        consolidation_mode = "buffer"

    replay_window = 128
    if m2_count > 128 or d_mem > 2.5:
        replay_window = 96
    if mode == "deep" and severity == "low":
        replay_window = 192

    return {
        "retrieval_top_k": int(retrieval_top_k),
        "retrieval_scope": retrieval_scope,
        "write_mode": write_mode,
        "consolidation_mode": consolidation_mode,
        "replay_window": int(replay_window),
        "require_trusted_source": bool(runtime_policy.get("require_trusted_source_for_promotion", False)),
        "consolidation_gate_threshold": float(gate_threshold),
        "require_loop_coherence": bool(require_loop_coherence),
        "allowed_consolidations": consolidation_profile["allowed"],
        "blocked_consolidations": consolidation_profile["blocked"],
        "consolidation_focus": consolidation_profile["focus"],
        "consolidation_holonomy": consolidation_profile["metrics"],
        "channel_thresholds": {
            "semantic": float(gate_threshold),
            "procedural": float(gate_threshold + (0.02 if mode == "safe" else 0.0)),
            "affective": float(gate_threshold + (0.03 if severity != "low" else 0.0)),
        },
        "orbital_state": orbital,
        "notes": [
            f"orbital_mode={mode}",
            f"rh_severity={severity}",
            f"R_H={r_h:.4f}",
            f"closure_penalty={closure:.4f}",
            f"memory_defect={d_mem:.4f}",
            f"consolidation_focus={consolidation_profile['focus']}",
            f"allowed_consolidations={','.join(consolidation_profile['allowed']) or 'none'}",
        ],
    }
