"""Flask route handlers for the CIEL Quiet Orbital Control GUI."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from flask import Flask, Response, current_app, jsonify, render_template, request

_LOG = logging.getLogger(__name__)
PREFERENCES_PATH = Path("integration") / "reports" / "sapiens_client" / "gui_preferences.json"


def _root() -> Path:
    return Path(current_app.config.get("CIEL_ROOT", Path.cwd()))


def _load_orbital_bridge_report() -> dict[str, Any]:
    root = _root()
    report_path = root / "integration" / "reports" / "orbital_bridge" / "orbital_bridge_report.json"
    if report_path.exists():
        try:
            return json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            _LOG.warning("Could not read orbital bridge report at %s: %s", report_path, exc)
    return {}


def _load_manifest() -> dict[str, Any]:
    root = _root()
    manifest_path = root / "integration" / "sapiens" / "panel_manifest.json"
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            _LOG.warning("Could not read panel manifest at %s: %s", manifest_path, exc)
    return {}


def _default_preferences() -> dict[str, Any]:
    return {
        "schema": "ciel-gui-preferences/v1",
        "communication_mode": "guided",
        "orchestration_mode": "safe",
        "memory_policy": "session-first",
        "selected_model_key": "tinyllama-1.1b-chat-q4",
        "live_refresh_ms": 15000,
        "show_live_vitals": True,
        "show_eeg_overlay": True,
    }


def _load_preferences() -> dict[str, Any]:
    root = _root()
    path = root / PREFERENCES_PATH
    if not path.exists():
        return _default_preferences()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return _default_preferences()
    return {**_default_preferences(), **data}


def _save_preferences(prefs: dict[str, Any]) -> dict[str, Any]:
    root = _root()
    path = root / PREFERENCES_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    merged = {**_default_preferences(), **prefs}
    path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    return merged


def _control_options() -> dict[str, Any]:
    try:
        from ..gguf_manager import KNOWN_MODELS

        models = [
            {"key": key, "name": spec.name, "description": spec.description, "tags": list(spec.tags)}
            for key, spec in KNOWN_MODELS.items()
        ]
    except Exception:
        models = []

    return {
        "schema": "ciel-gui-control-options/v1",
        "communication_modes": ["guided", "dialogic", "clinical", "analysis"],
        "orchestration_modes": ["safe", "guided", "standard", "deep"],
        "memory_policies": ["session-first", "long-horizon", "strict-minimal"],
        "refresh_presets_ms": [5000, 10000, 15000, 30000],
        "model_options": models,
    }


def register_routes(app: Flask) -> None:
    @app.route("/")
    def index() -> str:
        bridge = _load_orbital_bridge_report()
        manifest = _load_manifest()
        prefs = _load_preferences()
        context = {
            "system_mode": bridge.get("recommended_control", {}).get("mode", "guided"),
            "backend_status": "online" if bridge else "offline",
            "manifest_version": manifest.get("schema", "—"),
            "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
            "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
            "selected_model_key": prefs.get("selected_model_key", "tinyllama-1.1b-chat-q4"),
        }
        return render_template("index.html", **context)

    @app.route("/api/status")
    def api_status() -> Response:
        bridge = _load_orbital_bridge_report()
        manifest = _load_manifest()
        prefs = _load_preferences()
        payload = {
            "schema": "ciel-gui-status/v1",
            "system_mode": bridge.get("recommended_control", {}).get("mode", "guided"),
            "writeback_gate": bridge.get("recommended_control", {}).get("writeback_gate", False),
            "backend_status": "online" if bridge else "offline",
            "manifest_version": manifest.get("schema", ""),
            "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
            "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
            "closure_penalty": bridge.get("health_manifest", {}).get("closure_penalty", 0.0),
            "energy_budget": "warm",
            "preferences": prefs,
        }
        return jsonify(payload)

    @app.route("/api/panel")
    def api_panel() -> Response:
        root = _root()
        bridge = _load_orbital_bridge_report()
        prefs = _load_preferences()
        options = _control_options()

        session_path = root / "integration" / "reports" / "sapiens_client" / "session.json"
        session_data: dict[str, Any] = {}
        if session_path.exists():
            try:
                session_data = json.loads(session_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                _LOG.warning("Could not read session file at %s: %s", session_path, exc)

        transcript_path = root / "integration" / "reports" / "sapiens_client" / "transcript.md"
        transcript = ""
        if transcript_path.exists():
            try:
                transcript = transcript_path.read_text(encoding="utf-8")[:4096]
            except OSError as exc:
                _LOG.warning("Could not read transcript at %s: %s", transcript_path, exc)

        payload = {
            "schema": "ciel-gui-panel/v2",
            "control": {
                "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
                "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
                "mode": bridge.get("recommended_control", {}).get("mode", "guided"),
                "recommended_action": bridge.get("health_manifest", {}).get("recommended_action", "guided interaction"),
            },
            "communication": {
                "session": session_data,
                "transcript_preview": transcript[:512] if transcript else "",
            },
            "support": {
                "health_manifest": bridge.get("health_manifest", {}),
                "recommended_control": bridge.get("recommended_control", {}),
            },
            "preferences": prefs,
            "options": options,
        }
        return jsonify(payload)

    @app.route("/api/control/options")
    def api_control_options() -> Response:
        return jsonify(_control_options())

    @app.route("/api/preferences", methods=["GET", "POST"])
    def api_preferences() -> Response:
        if request.method == "GET":
            return jsonify(_load_preferences())
        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict):
            return jsonify({"error": "invalid preferences payload"}), 400
        updated = _save_preferences(payload)
        return jsonify({"status": "saved", "preferences": updated})

    @app.route("/api/models")
    def api_models() -> Response:
        try:
            from ..gguf_manager import GGUFManager

            mgr = GGUFManager()
            return jsonify(
                {
                    "schema": "ciel-gui-models/v1",
                    "models_dir": str(mgr.models_dir),
                    "models": mgr.list_models(),
                    "default_installed": mgr.is_installed(),
                    "selected_model_key": _load_preferences().get("selected_model_key", "tinyllama-1.1b-chat-q4"),
                }
            )
        except Exception:
            return jsonify({"error": "model manager unavailable", "models": []}), 500

    @app.route("/api/models/select", methods=["POST"])
    def api_models_select() -> Response:
        data = request.get_json(silent=True) or {}
        selected = str(data.get("model_key", "")).strip()
        if not selected:
            return jsonify({"status": "error", "error": "model_key is required"}), 400
        prefs = _load_preferences()
        prefs["selected_model_key"] = selected
        prefs = _save_preferences(prefs)
        return jsonify({"status": "selected", "preferences": prefs})

    @app.route("/api/models/ensure", methods=["POST"])
    def api_models_ensure() -> Response:
        try:
            from ..gguf_manager import GGUFManager

            mgr = GGUFManager()
            prefs = _load_preferences()
            selected_key = prefs.get("selected_model_key", mgr.default_model_key)
            if mgr.is_installed(selected_key):
                path = mgr.model_path(selected_key)
                return jsonify({"status": "already_installed", "path": str(path), "model_key": selected_key})
            path = mgr.ensure_model(selected_key)
            return jsonify({"status": "installed", "path": str(path), "model_key": selected_key})
        except Exception:
            return jsonify({"status": "error", "error": "model installation failed"}), 500

    @app.route("/api/orchestrate", methods=["POST"])
    def api_orchestrate() -> Response:
        data = request.get_json(silent=True) or {}
        action = str(data.get("action", "")).strip()
        if not action:
            return jsonify({"status": "error", "error": "action is required"}), 400
        return jsonify({"status": "queued", "action": action, "note": "execution delegated to backend runtime modules"})

    @app.errorhandler(404)
    def not_found(_err) -> tuple[Response, int]:
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(_err) -> tuple[Response, int]:
        return jsonify({"error": "internal server error"}), 500
