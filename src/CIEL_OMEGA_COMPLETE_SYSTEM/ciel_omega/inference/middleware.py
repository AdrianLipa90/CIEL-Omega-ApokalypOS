from __future__ import annotations
from pathlib import Path
from typing import Any
import json

try:
    from ..bootstrap_runtime import ensure_runtime_paths
    _OMEGA_ROOT = ensure_runtime_paths(__file__)
    from ..orbital.global_pass import run_global_pass  # type: ignore
    from .topology_api import get_coherence_index, get_loop_integrity, sync_to_phase  # type: ignore
except Exception:  # pragma: no cover - local script fallback
    import sys
    _HERE = Path(__file__).resolve()
    _OMEGA_ROOT = _HERE.parents[1]
    _PARENT = _OMEGA_ROOT.parent
    for _candidate in (_OMEGA_ROOT, _PARENT):
        _s = str(_candidate)
        if _s not in sys.path:
            sys.path.insert(0, _s)
    from orbital.global_pass import run_global_pass  # type: ignore
    from inference.topology_api import get_coherence_index, get_loop_integrity, sync_to_phase  # type: ignore

STABILIZATION_MESSAGES = [
    {"role": "user", "content": "Reply with exactly: READY-1"},
    {"role": "user", "content": "Reply with exactly: READY-2"},
]


def extract_text(response: dict[str, Any]) -> str:
    try:
        return response["choices"][0]["message"]["content"]
    except Exception:
        return "<unparsed>"


def run_three_prompt_session(runner, model: str, final_prompt: str, temperature: float = 0.0) -> dict[str, Any]:
    transcript: list[dict[str, str]] = [
        {
            "role": "system",
            "content": "You are a local GGUF test model. Follow the requested reply format exactly when possible.",
        }
    ]
    steps: list[dict[str, Any]] = []
    for msg in STABILIZATION_MESSAGES:
        transcript.append(msg)
        resp = runner.chat(model=model, messages=transcript, temperature=temperature, max_tokens=24)
        text = extract_text(resp)
        transcript.append({"role": "assistant", "content": text})
        steps.append({"prompt": msg["content"], "response": text, "raw": resp})
    final_msg = {"role": "user", "content": final_prompt}
    transcript.append(final_msg)
    final_resp = runner.chat(model=model, messages=transcript, temperature=temperature, max_tokens=96)
    final_text = extract_text(final_resp)
    transcript.append({"role": "assistant", "content": final_text})
    steps.append({"prompt": final_prompt, "response": final_text, "raw": final_resp})
    return {"transcript": transcript, "steps": steps, "final_text": final_text}


def _resolve_repo_root() -> Path:
    current = _OMEGA_ROOT.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "integration" / "Orbital" / "main" / "reports").exists() and (candidate / "src").exists():
            return candidate
    return _OMEGA_ROOT.parents[2] if len(_OMEGA_ROOT.parents) > 2 else _OMEGA_ROOT


def _load_latest_orbital_summary() -> dict[str, Any] | None:
    repo_root = _resolve_repo_root()
    summary_path = repo_root / "integration" / "Orbital" / "main" / "reports" / "global_orbital_coherence_pass" / "summary.json"
    if not summary_path.exists():
        return None
    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    final = payload.get("final", {}) if isinstance(payload, dict) else {}
    if not isinstance(final, dict) or not final:
        return None
    final = dict(final)
    final.setdefault("status", "report")
    final["source"] = str(summary_path.relative_to(repo_root))
    return final


def orbital_precheck() -> dict[str, Any]:
    cached = _load_latest_orbital_summary()
    if cached is not None:
        return cached
    try:
        result = run_global_pass().get("final", {})
        if isinstance(result, dict):
            result = dict(result)
            result.setdefault("status", "computed")
        return result
    except Exception as exc:  # pragma: no cover - best effort in local Omega mode
        return {"status": "unavailable", "error": str(exc)}


def orbital_postcheck() -> dict[str, Any]:
    try:
        result = run_global_pass().get("final", {})
        if isinstance(result, dict):
            result = dict(result)
            result.setdefault("status", "computed")
        return result
    except Exception as exc:  # pragma: no cover - best effort in local Omega mode
        cached = _load_latest_orbital_summary()
        if cached is not None:
            cached = dict(cached)
            cached["status"] = "report_fallback"
            return cached
        return {"status": "unavailable", "error": str(exc)}


def run_orbital_wrapped_chat(backend, model: str, messages: list[dict], temperature: float = 0.0, max_tokens: int = 128) -> dict:
    pre = orbital_precheck()
    response = backend.chat(model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
    post = orbital_postcheck()
    return {"pre": pre, "response": response, "post": post}


def build_inference_seed(flow_entry: dict[str, Any], target_phase: float | None = None) -> dict[str, Any]:
    affect = flow_entry.get("affect", {}) if isinstance(flow_entry, dict) else {}
    dominant_affect = max(affect, key=affect.get) if affect else "neutral"
    return {
        "target_phase": float(target_phase or 0.0),
        "mood": float(flow_entry.get("mood", 0.0) or 0.0),
        "soul_invariant": float(flow_entry.get("soul_invariant", 0.0) or 0.0),
        "dominant_affect": dominant_affect,
        "intention": flow_entry.get("intention", []),
    }


def _ethical_pre_gate(*, coherence_index: float, loop_integrity: float, ethical_score: float) -> dict[str, Any]:
    ok = (ethical_score >= 0.3) and (coherence_index >= 0.5) and (loop_integrity >= 0.05)
    reasons: list[str] = []
    if ethical_score < 0.3:
        reasons.append("ethical_score_low")
    if coherence_index < 0.5:
        reasons.append("coherence_low")
    if loop_integrity < 0.05:
        reasons.append("loop_integrity_low")
    return {"passed": ok, "reasons": reasons}


def _ethical_post_gate(*, coherence_index: float, loop_integrity: float, response_text: str = "") -> dict[str, Any]:
    # Post gate remains conservative and structural; content heuristics can be added later.
    ok = (coherence_index >= 0.4) and (loop_integrity >= 0.03)
    reasons: list[str] = []
    if coherence_index < 0.4:
        reasons.append("post_coherence_low")
    if loop_integrity < 0.03:
        reasons.append("post_loop_integrity_low")
    if not response_text:
        reasons.append("no_response_text")
    return {"passed": ok, "reasons": reasons}


def build_inference_snapshot(target_phase: float | None = None) -> dict[str, Any]:
    """Minimal orbital-bound inference snapshot used by higher layers.

    This remains useful for diagnostics, but final inference execution should go
    through build_orbital_ethical_inference_surface(), not InformationFlow.
    """
    pre = orbital_precheck()
    if target_phase is None:
        target_phase = float(pre.get("zeta_effective_phase", 0.0) or 0.0)
    return {
        "coherence_index": float(get_coherence_index()),
        "loop_integrity": float(get_loop_integrity()),
        "phase_sync": sync_to_phase(float(target_phase)),
        "orbital_precheck": pre,
        "orbital_precheck_available": pre.get("status") != "unavailable",
    }


def build_orbital_ethical_inference_surface(
    *,
    flow_entry: dict[str, Any],
    target_phase: float | None,
    ethical_score: float,
    backend: Any | None = None,
    model: str | None = None,
    messages: list[dict[str, Any]] | None = None,
    temperature: float = 0.0,
    max_tokens: int = 128,
) -> dict[str, Any]:
    snapshot = build_inference_snapshot(target_phase=target_phase)
    coherence_index = float(snapshot.get("coherence_index", 0.0))
    loop_integrity = float(snapshot.get("loop_integrity", 0.0))
    pre_gate = _ethical_pre_gate(
        coherence_index=coherence_index,
        loop_integrity=loop_integrity,
        ethical_score=float(ethical_score),
    )
    seed = build_inference_seed(flow_entry, target_phase=target_phase)
    result: dict[str, Any] = {
        **snapshot,
        "inference_seed": seed,
        "ethical_pre_gate": pre_gate,
        "inference_mode": "dry_run",
        "gguf_enabled": bool(backend is not None and model and messages),
    }
    if backend is not None and model and messages and pre_gate["passed"]:
        wrapped = run_orbital_wrapped_chat(
            backend=backend,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        response_text = extract_text(wrapped.get("response", {}))
        post_gate = _ethical_post_gate(
            coherence_index=coherence_index,
            loop_integrity=loop_integrity,
            response_text=response_text,
        )
        result.update({
            "inference_mode": "gguf_wrapped",
            "wrapped_chat": wrapped,
            "response_text": response_text,
            "ethical_post_gate": post_gate,
        })
    return result


def enrich_information_entry(entry: dict[str, Any], target_phase: float | None = None) -> dict[str, Any]:
    enriched = dict(entry)
    enriched["inference_seed"] = build_inference_seed(enriched, target_phase=target_phase)
    return enriched
