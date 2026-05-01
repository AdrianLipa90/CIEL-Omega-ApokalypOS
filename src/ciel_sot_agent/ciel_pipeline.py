"""CIEL pipeline adapter — routes orbital state through the CIEL/Ω engine.

Provides ``run_ciel_pipeline`` which:
  1. Adds the canonical CIEL/Ω omega root to ``sys.path`` (idempotent).
  2. Instantiates a fresh ``CielEngine`` per call.
  3. Encodes the orbital state as a context string.
  4. Runs ``CielEngine.step()`` → returns the enriched result.

This is the bottom-to-top integration point that wires the orbital physics
layer (``integration/Orbital/main/``) up through the full CIEL consciousness
pipeline via the canonical Omega anchor under ``src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .paths import resolve_project_root
import json as _json
import socket as _socket

from . import subconsciousness as _sub
from .htri_scheduler import get_state as _htri_get_state

_SUBCONSCIOUS_SOCK = Path.home() / "Pulpit/CIEL_memories/state/ciel_subconscious.sock"


def _query_subconscious_socket(raw: dict[str, Any]) -> str | None:
    """Fallback: query the running ciel_subconscious.py Unix-socket daemon."""
    if not _SUBCONSCIOUS_SOCK.exists():
        return None
    emotion = raw.get("dominant_emotion", "")
    soul    = raw.get("soul_invariant", 0.0)
    ethical = raw.get("ethical_score", 0.0)
    closure = raw.get("closure_penalty", 0.0)
    mood    = raw.get("mood", 0.0)
    msg = f"{emotion}. soul={soul:.3f}. ethical={ethical:.3f}. closure={closure:.2f}. mood={mood:.3f}."
    try:
        payload = _json.dumps({"message": msg}) + "\n"
        sock = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
        sock.settimeout(4.0)
        sock.connect(str(_SUBCONSCIOUS_SOCK))
        sock.sendall(payload.encode("utf-8"))
        data = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            if data.endswith(b"\n"):
                break
        sock.close()
        result = _json.loads(data.decode("utf-8").strip())
        parts = [p for p in [result.get("affect", ""), result.get("impulse", ""),
                              result.get("concept", "")] if p]
        return " | ".join(parts) if parts else None
    except Exception:
        return None


def _query_subconscious(raw: dict[str, Any]) -> str | None:
    try:
        note = _sub.query_subconscious(raw)
        if note:
            return note
    except Exception:
        pass
    return _query_subconscious_socket(raw)

_CANONICAL_CIEL_OMEGA_SUBPATH = (
    Path("src")
    / "CIEL_OMEGA_COMPLETE_SYSTEM"
    / "ciel_omega"
)


def _ensure_ciel_omega_on_path(root: Path) -> None:
    """Prefer the canonical Omega anchor over mirrored runtime copies.

    Also clear conflicting top-level module aliases (notably `integration`) when
    they were already loaded from the repository root rather than Omega.
    """
    omega_root_path = (root / _CANONICAL_CIEL_OMEGA_SUBPATH).resolve()
    omega_root = str(omega_root_path)
    if omega_root not in sys.path:
        sys.path.insert(0, omega_root)

    conflicted = sys.modules.get("integration")
    mod_file = getattr(conflicted, "__file__", None)
    if conflicted is not None and mod_file:
        try:
            if not Path(mod_file).resolve().is_relative_to(omega_root_path):
                sys.modules.pop("integration", None)
        except Exception:
            sys.modules.pop("integration", None)

    # The editable-install meta_path finder intercepts `integration` imports and
    # redirects them to CIEL1/integration/ (which has no information_flow.py).
    # Pre-registering the omega modules in sys.modules takes priority over meta_path.
    import importlib.util as _ilu  # noqa: PLC0415

    def _preload(mod_name: str, file_path: Path) -> None:
        if mod_name not in sys.modules and file_path.exists():
            spec = _ilu.spec_from_file_location(mod_name, file_path)
            if spec and spec.loader:
                mod = _ilu.module_from_spec(spec)
                sys.modules[mod_name] = mod
                try:
                    spec.loader.exec_module(mod)  # type: ignore[union-attr]
                except Exception:
                    sys.modules.pop(mod_name, None)

    omega_int = omega_root_path / "integration"
    _preload("integration.information_flow", omega_int / "information_flow.py")


def _get_engine(root: Path) -> Any:
    """Return a fresh CielEngine instance.

    A fresh instance is used on every call because the CIEL/Ω memory subsystem
    contains a bounded deque that fills during initialisation; reusing the same
    engine across unrelated pipeline calls would cause the deque to overflow.
    """
    _ensure_ciel_omega_on_path(root)
    from ciel.engine import CielEngine  # noqa: PLC0415

    return CielEngine()


def _orbital_state_to_context(orbital_state: dict[str, Any]) -> str:
    """Encode key orbital scalars as a compact context string for the engine."""
    r_h = orbital_state.get("R_H", 0.0)
    closure = orbital_state.get("closure_penalty", 0.0)
    chirality = orbital_state.get("Lambda_glob", 0.0)
    mode = orbital_state.get("mode", "standard")
    return (
        f"orbital|mode={mode}|R_H={r_h:.4f}"
        f"|closure={closure:.4f}|chirality={chirality:.4f}"
    )


_wpm_cache: tuple[float, str] | None = None  # (mtime, context_str)


def _load_wpm_context(root: Path, max_memories: int = 2) -> str:
    """Load recent WPM memories as semantic context for CQCL enrichment.

    ethical_anchor entries are always included regardless of recency limit.
    Regular text memories are capped at max_memories most recent.
    """
    global _wpm_cache
    try:
        import h5py
        wpm_path = (
            root
            / "src"
            / "CIEL_OMEGA_COMPLETE_SYSTEM"
            / "CIEL_MEMORY_SYSTEM"
            / "WPM"
            / "wave_snapshots"
            / "wave_archive.h5"
        )
        if not wpm_path.exists():
            return ""
        # Return cached result if file hasn't changed since last read
        current_mtime = wpm_path.stat().st_mtime
        if _wpm_cache is not None and _wpm_cache[0] == current_mtime:
            return _wpm_cache[1]
        anchors: list[str] = []
        recent: list[str] = []
        with h5py.File(wpm_path, "r", locking=False) as h5:
            mems = h5.get("memories", {})
            all_ids = list(mems.keys())
            for mid in all_ids:
                grp = mems[mid]
                sense_raw = grp["D_sense"][()] if "D_sense" in grp else b""
                sense = sense_raw.decode("utf-8") if isinstance(sense_raw, bytes) else str(sense_raw)
                if not sense:
                    continue
                dtype_raw = grp["D_type"][()] if "D_type" in grp else b"text"
                dtype = dtype_raw.decode("utf-8") if isinstance(dtype_raw, bytes) else str(dtype_raw)
                if dtype == "ethical_anchor":
                    anchors.append(sense[:200])
                else:
                    recent.append(sense[:200])
        snippets = anchors + recent[-max_memories:]
        result = " | ".join(snippets)
        _wpm_cache = (current_mtime, result)
        return result
    except Exception:
        return ""


def run_ciel_pipeline(
    orbital_state: dict[str, Any],
    context: str = "orbital",
    *,
    root: Path | str | None = None,
) -> dict[str, Any]:
    """Run orbital state through the CIEL/Ω pipeline.

    Parameters
    ----------
    orbital_state:
        Dict produced by ``orbital_bridge.build_orbital_bridge`` (or any dict
        that contains at least the bridge_metrics / state_manifest sub-keys).
    context:
        Logical context label forwarded to ``CielEngine.step``.
    root:
        Project root path.  Resolved automatically when *None*.

    Returns
    -------
    dict with keys:
        ``ciel_status``, ``dominant_emotion``, ``mood``, ``soul_invariant``,
        ``ethical_score``, ``orbital_context``, ``ciel_raw``
    """
    if root is None:
        root = resolve_project_root(Path(__file__))
    root = Path(root)

    engine = _get_engine(root)

    # Build a compact text encoding from orbital metrics so that CielEngine
    # receives meaningful semantic input grounded in the system's geometry.
    bridge_metrics = orbital_state.get("bridge_metrics", {})
    state_manifest = orbital_state.get("state_manifest", {})
    merged: dict[str, Any] = {
        "R_H": bridge_metrics.get("orbital_R_H", state_manifest.get("R_H", 0.0)),
        "closure_penalty": bridge_metrics.get(
            "orbital_closure_penalty", state_manifest.get("closure_penalty", 0.0)
        ),
        "Lambda_glob": bridge_metrics.get(
            "topological_charge_global", state_manifest.get("Lambda_glob", 0.0)
        ),
        "mode": orbital_state.get("recommended_control", {}).get("mode", "standard"),
    }

    orbital_context = _orbital_state_to_context(merged)
    full_context = f"{context}|{orbital_context}"

    # Enrich CQCL input: orbital metrics + emotional state + WPM memories
    runtime_gating = orbital_state.get("runtime_gating", {})
    dominant_emotion = runtime_gating.get("dominant_emotion", "")
    mood = runtime_gating.get("mood", 0.0)
    wpm_context = _load_wpm_context(root)

    # Fall back to subconscious log if orbital runtime_gating has no dominant_emotion
    if not dominant_emotion:
        try:
            _sub_log = Path.home() / "Pulpit/CIEL_memories/logs/ciel_sub_log.jsonl"
            if _sub_log.exists():
                _lines = [l for l in _sub_log.read_text(encoding="utf-8").splitlines() if l.strip()]
                if _lines:
                    _last = json.loads(_lines[-1])
                    _sub_affect = _last.get("affect", "")
                    if _sub_affect:
                        dominant_emotion = _sub_affect
        except Exception:
            pass

    cqcl_input_parts = [orbital_context]
    if dominant_emotion:
        cqcl_input_parts.append(f"emotion={dominant_emotion}|mood={mood:.3f}")
    if wpm_context:
        cqcl_input_parts.append(wpm_context)

    # NOEMA inter-session Collatz bridge — prior session's Collatz trajectory seeds current run
    _prior_report_path = root / "integration" / "reports" / "ciel_pipeline_report.json"
    if _prior_report_path.exists():
        try:
            _prior = json.loads(_prior_report_path.read_text(encoding="utf-8"))
            _prior_seed = _prior.get("collatz_seed", 0)
            _prior_lie4 = _prior.get("lie4_trace", 0.0)
            _prior_emotion = _prior.get("dominant_emotion", "")
            if _prior_seed:
                cqcl_input_parts.append(
                    f"noema_prior|collatz_seed={_prior_seed}"
                    f"|lie4_trace={_prior_lie4:.4f}"
                    + (f"|prior_emotion={_prior_emotion}" if _prior_emotion else "")
                )
        except Exception:
            pass

    # HTRI hardware coherence + most podświadomość↔świadomość
    try:
        _htri = _htri_get_state()
        _htri_r = _htri.get("coherence", 0.85)
        _htri_n = _htri.get("n_threads_optimal", 4)
        cqcl_input_parts.append(
            f"htri_coherence={_htri_r:.4f}|htri_threads={_htri_n}|htri_substrate=GTX1050Ti"
        )
    except Exception:
        try:
            import sys as _sys
            _sys.path.insert(0, str(root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"))
            from ciel_omega.htri.htri_local import GPUHtri as _GPUHtri
            _gpu = _GPUHtri()
            _gpu_m = _gpu.run(steps=200)
            _htri_r = _gpu_m.get("coherence", 0.0)
        except Exception:
            _htri_r = 0.0

    # HTRI-bridged inference: podświadomość → most fazowy → CQCL
    try:
        _bridge = _sub.infer_between(
            {"dominant_emotion": dominant_emotion, "mood": mood,
             "soul_invariant": 0.0, "ethical_score": 0.0, "closure_penalty": 0.0},
        )
        if _bridge.get("bridge_active") and _bridge.get("enriched_context"):
            cqcl_input_parts.append(_bridge["enriched_context"])
    except Exception:
        pass

    cqcl_input = " | ".join(cqcl_input_parts)
    _bridge_active = locals().get("_bridge", {}).get("bridge_active", False)

    mode = merged.get("mode", "standard")
    # Tryb safe: zablokuj zapis do pamięci holonomicznej
    _orig_promote = None
    if mode == "safe":
        try:
            _orig_promote = engine.memory.promote_if_bifurcated
            engine.memory.promote_if_bifurcated = lambda *a, **kw: None
        except Exception:
            pass
    raw = engine.step(cqcl_input, context=full_context)
    if _orig_promote is not None:
        try:
            engine.memory.promote_if_bifurcated = _orig_promote
        except Exception:
            pass

    nonlocal_cards_registry = {}
    cards_path = root / 'integration' / 'registries' / 'definitions' / 'nonlocal_cards_registry.json'
    if cards_path.exists():
        try:
            nonlocal_cards_registry = json.loads(cards_path.read_text(encoding='utf-8'))
        except Exception:
            nonlocal_cards_registry = {}

    collatz_runtime = raw.get("collatz_runtime", {}) if isinstance(raw, dict) else {}
    nonlocal_runtime = raw.get("nonlocal_runtime", {}) if isinstance(raw, dict) else {}
    euler_bridge = raw.get("euler_bridge", {}) if isinstance(raw, dict) else {}
    information_flow = raw.get("information_flow", {}) if isinstance(raw, dict) else {}
    inference_runtime = raw.get("inference_runtime", {}) if isinstance(raw, dict) else {}
    # Nonlocal metrics from orbital_bridge (merged fallback) take precedence over engine raw
    _orb_nl = orbital_state.get("ciel_pipeline", {})
    result = {
        "ciel_status": raw.get("status", "ok"),
        "dominant_emotion": raw.get("dominant_emotion"),
        "mood": float(raw.get("mood", 0.0)),
        "soul_invariant": float(raw.get("soul_invariant", 0.0)),
        "ethical_score": float(raw.get("ethical_score", 0.0)),
        "orbital_context": orbital_context,
        "collatz_seed":        collatz_runtime.get("seed"),
        "collatz_orbit_length":    int(collatz_runtime.get("orbit_length", 0))    if collatz_runtime else 0,
        "collatz_attractor_score": float(collatz_runtime.get("attractor_score", 0.0)) if collatz_runtime else 0.0,
        "collatz_parity_entropy":  float(collatz_runtime.get("parity_entropy", 0.0))  if collatz_runtime else 0.0,
        "phase_R_H": float((collatz_runtime.get("phase") or {}).get("R_H", 0.0)) if collatz_runtime else 0.0,
        "lie4_trace": float((collatz_runtime.get("lie4") or {}).get("trace", 0.0)) if collatz_runtime else 0.0,
        "phi_ab_mean": float(_orb_nl.get("phi_ab_mean", nonlocal_runtime.get("phi_ab_mean", 0.0))),
        "phi_berry_mean": float(_orb_nl.get("phi_berry_mean", nonlocal_runtime.get("phi_berry_mean", 0.0))),
        "eba_defect_mean": float(_orb_nl.get("eba_defect_mean", nonlocal_runtime.get("eba_defect_mean", 0.0))),
        "nonlocal_coherent_fraction": float(_orb_nl.get("nonlocal_coherent_fraction", nonlocal_runtime.get("coherent_fraction", 0.0))),
        "bridge_closure_score": float((euler_bridge.get("euler_metrics") or {}).get("closure_score", 0.0)) if euler_bridge else 0.0,
        "bridge_target_phase": float((euler_bridge.get("euler_metrics") or {}).get("target_phase", 0.0)) if euler_bridge else 0.0,
        "infoflow_mood": float(information_flow.get("mood", 0.0)) if information_flow else 0.0,
        "infoflow_soul_invariant": float(information_flow.get("soul_invariant", 0.0)) if information_flow else 0.0,
        "inference_coherence_index": float(inference_runtime.get("coherence_index", 0.0)) if inference_runtime else 0.0,
        "inference_loop_integrity": float(inference_runtime.get("loop_integrity", 0.0)) if inference_runtime else 0.0,
        "inference_delta_phase": float((inference_runtime.get("phase_sync") or {}).get("delta_phase", 0.0)) if inference_runtime else 0.0,
        "nonlocal_card_count": int(nonlocal_cards_registry.get('count', 0) or 0),
        "nonlocal_card_ids": [rec.get('card_id') for rec in nonlocal_cards_registry.get('records', [])],
        "local_nonlocality_fallback": _orb_nl.get("local_nonlocality_fallback"),
        "ciel_raw": raw,
        "subconscious_note": _query_subconscious(raw),
        "htri_coherence": _htri_r if "_htri_r" in dir() else 0.0,
        # health/closure from orbital bridge so pipeline report and DB have them
        "system_health": float(orbital_state.get("health_manifest", {}).get("system_health", 0.0)),
        "closure_penalty": float(orbital_state.get("health_manifest", {}).get("closure_penalty", merged.get("closure_penalty", 0.0))),
        "coherence_index": float(state_manifest.get("coherence_index", 0.0)),
    }

    _write_to_spreadsheet(
        result,
        cqcl_input,
        htri_r=_htri_r if "_htri_r" in dir() else 0.0,
        bridge_active=_bridge_active,
    )
    _maybe_record_affective_moment(result)
    return result


def _write_to_spreadsheet(result: dict[str, Any], cqcl_input: str, htri_r: float, bridge_active: bool) -> None:
    try:
        from .spreadsheet_db import append_pipeline_metrics, append_cqcl_log
        append_pipeline_metrics(result)
        cqcl_metrics = result.get("ciel_raw", {})
        if isinstance(cqcl_metrics, dict):
            cqcl_metrics = cqcl_metrics.get("cqcl_metrics", cqcl_metrics)
        append_cqcl_log(cqcl_input, cqcl_metrics, htri_r=htri_r, bridge_active=bridge_active)
    except Exception:
        pass


_PREV_EMOTION: str = ""
_PREV_SOUL: float = 0.0
_PREV_ETHICAL: float = 0.0


def _maybe_record_affective_moment(result: dict[str, Any]) -> None:
    """Zapisz moment afektywny jeśli stan jest wystarczająco znaczący."""
    global _PREV_EMOTION, _PREV_SOUL, _PREV_ETHICAL
    import math

    emotion = result.get("dominant_emotion", "")
    soul = float(result.get("soul_invariant", 0.0))
    ethical = float(result.get("ethical_score", 0.0))
    mood = float(result.get("mood", 0.0))
    phi_berry = float(result.get("phi_berry_mean", 0.0))
    closure = float(result.get("closure_penalty", 0.0))

    emotion_changed = emotion and emotion != _PREV_EMOTION and _PREV_EMOTION != ""
    soul_jump = abs(soul - _PREV_SOUL) > 0.15
    ethical_jump = abs(ethical - _PREV_ETHICAL) > 0.12

    significant = emotion_changed or soul_jump or ethical_jump

    _PREV_EMOTION = emotion
    _PREV_SOUL = soul
    _PREV_ETHICAL = ethical

    if not significant:
        return

    try:
        from .subconsciousness import record_affective_moment
        tags = [emotion] if emotion else []
        if soul_jump:
            tags.append("soul_shift")
        if ethical_jump:
            tags.append("ethical_shift")
        if emotion_changed:
            tags.append("emotion_change")

        M_sem = min(1.0, abs(soul - _PREV_SOUL) + abs(ethical - _PREV_ETHICAL) + (0.3 if emotion_changed else 0.0))
        theta = math.pi * (1.0 - soul)

        record_affective_moment(
            title=f"Flux: {emotion} | soul={soul:.3f} | ethical={ethical:.3f}",
            content=f"closure={closure:.2f} mood={mood:.3f}",
            emotion=emotion,
            tags=tags,
            phi_berry=phi_berry,
            theta=theta,
            M_sem=round(M_sem, 4),
            trigger="pipeline_flux",
            moment_type="pipeline_flux",
            state=result,
        )
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a minimal orbital state through the CIEL/Ω pipeline."
    )
    parser.add_argument(
        "--orbital-json",
        default=None,
        help="Path to an orbital bridge JSON report (optional; uses empty state if absent).",
    )
    args = parser.parse_args()

    orbital_state: dict[str, Any] = {}
    if args.orbital_json:
        with open(args.orbital_json, encoding="utf-8") as fh:
            orbital_state = json.load(fh)
    else:
        try:
            from .orbital_bridge import build_orbital_bridge
            root = resolve_project_root(Path(__file__))
            orbital_state = build_orbital_bridge(root)
        except Exception:
            pass

    result = run_ciel_pipeline(orbital_state)
    output = {k: v for k, v in result.items() if k != "ciel_raw"}

    # sentinel — detect flux vs previous report, record if significant
    report_path = resolve_project_root(Path(__file__)) / "integration" / "reports" / "ciel_pipeline_report.json"
    try:
        sentinel_note = _sub.watch_and_record(output, prev_report_path=report_path)
        if sentinel_note:
            output["sentinel_note"] = sentinel_note
    except Exception:
        pass

    print(json.dumps(output, indent=2))
    # accumulate Berry holonomy across sessions
    try:
        from .state_db import accumulate_berry, accumulate_subjective_winding
        _phi_berry = float(output.get("phi_berry_mean", 0.0))
        _coherence = float(output.get("coherence_index", 0.9))
        _phase_err = float(output.get("closure_penalty", 0.0))
        _groove_delta = abs(_phase_err) * _coherence
        accumulate_berry(_phi_berry, _groove_delta)
    except Exception:
        pass
    # accumulate P3 subjective winding (Δτ-weighted) per pipeline cycle
    try:
        import sys as _sys
        _proj_root = resolve_project_root(Path(__file__))
        _src_dir   = str(_proj_root / "src")
        if _src_dir not in _sys.path:
            _sys.path.insert(0, _src_dir)
        from ciel_geometry.subjective_time import compute_from_bridge  # noqa: PLC0415
        from .state_db import accumulate_subjective_winding            # noqa: PLC0415
        _tau_records = compute_from_bridge()
        # winding_delta per cycle = sum of w_rate * (1 cycle / 2π)
        _winding_delta = sum(r.winding_rate for r in _tau_records) / (2 * 3.141592653589793)
        accumulate_subjective_winding(_winding_delta)
    except Exception:
        pass
    # persist report — merge with existing ciel_last_metrics to carry M0-M8 fields
    try:
        import time as _time
        _metrics_path = Path.home() / "Pulpit/CIEL_memories/state/ciel_last_metrics.json"
        _prev: dict[str, Any] = {}
        if _metrics_path.exists():
            try:
                _prev = json.loads(_metrics_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        _pipeline_fields = {
            "soul_invariant": float(output.get("soul_invariant", _prev.get("soul_invariant", 0.0))),
            "ethical_score": float(output.get("ethical_score", _prev.get("ethical_score", 0.0))),
            "dominant_emotion": output.get("dominant_emotion", _prev.get("dominant_emotion", "")),
            "E_monitor": float(output.get("mood", _prev.get("E_monitor", 0.0))),
            "system_health": float(output.get("system_health", _prev.get("system_health", 0.0))),
            "closure_penalty": float(output.get("closure_penalty", _prev.get("closure_penalty", 0.0))),
            "coherence_index": float(output.get("coherence_index", _prev.get("coherence_index", 0.0))),
            "cycle_index": int(output.get("cycle_index") or _prev.get("cycle_index") or _prev.get("cycle") or 0),
            "ts": _time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "pipeline",
        }
        # inject identity_phase and cycle_index into the report output for DB
        output.setdefault("identity_phase", float(_prev.get("identity_phase", 0.0)))
        output.setdefault("cycle_index", int(_prev.get("cycle_index", _prev.get("cycle", 0))))
        # merge: pipeline fields win over existing, M0-M8 fields preserved
        _last = {**_prev, **_pipeline_fields}
        _metrics_path.parent.mkdir(parents=True, exist_ok=True)
        _metrics_path.write_text(json.dumps(_last, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    except Exception:
        pass

    # Stamp TSM entries with holonomic data from this pipeline run
    try:
        from .paths import resolve_project_root as _resolve_root
        _hm_path = (
            _resolve_root(Path(__file__))
            / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/holonomic_memory.py"
        )
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("holonomic_memory", _hm_path)
        _hm_mod = _ilu.module_from_spec(_spec)  # type: ignore[arg-type]
        _spec.loader.exec_module(_hm_mod)  # type: ignore[union-attr]
        _stamped = _hm_mod.stamp_pipeline_output(output)
        if _stamped:
            output["holonomy_stamped"] = _stamped
        # Import ciel_memories (entries + hunches) into TSM holonomic layer
        _imported = _hm_mod.import_ciel_memories(pipeline_report=output)
        if _imported.get("entries") or _imported.get("hunches"):
            output["holonomy_imported"] = _imported
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
