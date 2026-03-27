from __future__ import annotations

from dataclasses import asdict, is_dataclass
import math
from typing import Any, Dict, List, Tuple

from ciel_omega.memory.orbital_holonomy import compute_retrieval_holonomy, sector_snapshot


def _to_payload(item: Any) -> Dict[str, Any]:
    if is_dataclass(item):
        return asdict(item)
    if isinstance(item, dict):
        return dict(item)
    if hasattr(item, "__dict__"):
        return dict(vars(item))
    return {"value": item}


def _extract_item(entry: Any) -> Tuple[Dict[str, Any], float]:
    if isinstance(entry, dict) and "item" in entry:
        payload = _to_payload(entry.get("item"))
        try:
            score = float(entry.get("score", 0.0) or 0.0)
        except Exception:
            score = 0.0
        return payload, score
    payload = _to_payload(entry)
    return payload, 0.0


def _channel_affinity(channel: str) -> str:
    mapping = {
        "perceptual": "runtime",
        "working": "runtime",
        "episodic": "memory",
        "semantic": "memory",
        "procedural": "memory",
        "affective": "relation",
    }
    return mapping.get(channel, "memory")


def _allowed_channels(scope: str) -> List[str]:
    if scope == "stabilize":
        return ["working", "episodic", "perceptual"]
    if scope == "narrow":
        return ["working", "episodic", "procedural"]
    if scope == "wide":
        return ["perceptual", "working", "episodic", "semantic", "procedural", "affective"]
    return ["working", "episodic", "procedural", "perceptual"]


def _entry_phase(payload: Dict[str, Any]) -> float:
    for key in ("phase", "phase_at_storage"):
        value = payload.get(key)
        if isinstance(value, (int, float)):
            return float(value % (2.0 * math.pi))
    ctx = payload.get("context") if isinstance(payload.get("context"), dict) else {}
    value = ctx.get("zeta_effective_phase")
    if isinstance(value, (int, float)):
        return float(value % (2.0 * math.pi))
    return 0.0


def _entry_score(channel: str, entry: Any, *, sector_memory: Any, orbital: Dict[str, Any], governor: Dict[str, Any]) -> Tuple[float, Dict[str, Any], Dict[str, Any], float]:
    payload, base_score = _extract_item(entry)
    score = float(base_score)
    score += 0.12 * float(payload.get("confidence", 0.0) or 0.0)
    score += 0.10 * float(payload.get("identity_alignment", 0.0) or 0.0)
    score += 0.06 * float(payload.get("salience", 0.0) or 0.0)
    score += 0.04 * float(payload.get("success_rate", 0.0) or 0.0)

    ctx = payload.get("context") if isinstance(payload.get("context"), dict) else {}
    result = payload.get("result") if isinstance(payload.get("result"), dict) else {}
    control = orbital.get("control") if isinstance(orbital.get("control"), dict) else {}
    diagnostics = orbital.get("diagnostics") if isinstance(orbital.get("diagnostics"), dict) else {}

    if ctx.get("control_mode") == control.get("mode"):
        score += 0.10
    if ctx.get("rh_severity") == orbital.get("rh_policy", {}).get("severity"):
        score += 0.06
    if _channel_affinity(channel) == diagnostics.get("dominant_residual_sector"):
        score += 0.08
    if _channel_affinity(channel) == diagnostics.get("dominant_vorticity_sector"):
        score += 0.05
    if governor.get("write_mode") == "durable" and bool(result.get("durable_write_allowed", False)):
        score += 0.04

    holonomic = compute_retrieval_holonomy(channel, entry_phase=_entry_phase(payload), holder=sector_memory, orbital=orbital)
    score += 0.18 * float(holonomic["phase_alignment"])
    score += 0.16 * float(holonomic["identity_attractor_score"])
    score += 0.18 * float(holonomic["holonomy_quality"])
    if bool(holonomic["loop_coherent"]):
        score += 0.06
    return float(score), payload, holonomic, float(base_score)


def govern_sector_retrieval(*, sector_memory: Any, query: str, governor: Dict[str, Any], orbital: Dict[str, Any]) -> Dict[str, Any]:
    top_k = int(governor.get("retrieval_top_k", 3) or 3)
    scope = str(governor.get("retrieval_scope", "focused"))
    channel_limit = 1 if scope == "stabilize" else (2 if scope in {"narrow", "focused"} else 3)
    raw = sector_memory.retrieve(query, top_k=max(top_k, 6))
    allowed = _allowed_channels(scope)
    snapshot = sector_snapshot(sector_memory)

    ranked: List[Dict[str, Any]] = []
    selected: Dict[str, List[Any]] = {}
    for channel in allowed:
        items = raw.get(channel) if isinstance(raw, dict) else None
        if not isinstance(items, list) or not items:
            continue
        decorated = sorted(
            [
                {
                    "score": row_score,
                    "entry": item,
                    "payload": payload,
                    "holonomic": holonomic,
                    "base_score": base,
                }
                for item in items
                for row_score, payload, holonomic, base in [_entry_score(channel, item, sector_memory=sector_memory, orbital=orbital, governor=governor)]
            ],
            key=lambda x: x["score"],
            reverse=True,
        )
        kept = [row["entry"] for row in decorated[:channel_limit]]
        if kept:
            selected[channel] = kept
        for row in decorated:
            payload = row["payload"]
            ranked.append(
                {
                    "channel": channel,
                    "score": float(row["score"]),
                    "base_score": float(row["base_score"]),
                    "text": payload.get("canonical_text") or payload.get("content") or payload.get("canonical_action") or payload.get("summary") or "",
                    **row["holonomic"],
                }
            )
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return {
        "scope": scope,
        "selected_channels": list(selected.keys()),
        "by_channel": selected,
        "ranked": ranked[:top_k],
        "raw": raw,
        "holonomic_context": {
            "identity_phase": snapshot.get("identity_phase"),
            "latest_loop_status": snapshot.get("latest_loop_status", {}),
        },
    }


__all__ = ["govern_sector_retrieval"]
