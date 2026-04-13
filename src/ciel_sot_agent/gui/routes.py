"""Flask route handlers for the CIEL Quiet Orbital Control GUI.

Routes
------
GET  /               — Main dashboard (HTML)
GET  /api/status     — System status JSON (top status bar data)
GET  /api/panel      — Full panel state JSON
GET  /api/models     — Installed GGUF models JSON
POST /api/models/ensure  — Ensure the default model is installed (async-safe)
GET  /api/control/options — Control and orchestration options
GET/POST /api/preferences — GUI preferences read/write
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from flask import Flask, Response, current_app, jsonify, render_template, request

_LOG = logging.getLogger(__name__)


def _root() -> Path:
    return Path(current_app.config.get("CIEL_ROOT", Path.cwd()))


def _load_orbital_bridge_report() -> dict[str, Any]:
    """Load the latest orbital bridge report if available."""
    root = _root()
    report_path = root / "integration" / "reports" / "orbital_bridge" / "orbital_bridge_report.json"
    if report_path.exists():
        try:
            return json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            _LOG.warning("Could not read orbital bridge report at %s: %s", report_path, exc)
    return {}


def _load_manifest() -> dict[str, Any]:
    """Load panel manifest if available."""
    root = _root()
    manifest_path = root / "integration" / "sapiens" / "panel_manifest.json"
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            _LOG.warning("Could not read panel manifest at %s: %s", manifest_path, exc)
    return {}




def _settings_path() -> Path:
    return _root() / "integration" / "sapiens" / "settings_defaults.json"


def _preferences_path() -> Path:
    return _root() / "integration" / "reports" / "sapiens_client" / "gui_preferences.json"


def _load_settings_defaults() -> dict[str, Any]:
    path = _settings_path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            _LOG.warning("Could not read settings defaults at %s: %s", path, exc)
    return {}


def _load_preferences() -> dict[str, Any]:
    path = _preferences_path()
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            _LOG.warning("Could not read GUI preferences at %s: %s", path, exc)
    return {
        "schema": "ciel-gui-preferences/v1",
        "selected_model": None,
        "preferred_mode": "guided",
        "orchestration_level": "balanced",
        "live_vitals_enabled": True,
        "memory_retention": "session-first",
    }


def _persist_preferences(payload: dict[str, Any]) -> dict[str, Any]:
    path = _preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    cleaned = {
        "schema": "ciel-gui-preferences/v1",
        "selected_model": payload.get("selected_model"),
        "preferred_mode": payload.get("preferred_mode", "guided"),
        "orchestration_level": payload.get("orchestration_level", "balanced"),
        "live_vitals_enabled": bool(payload.get("live_vitals_enabled", True)),
        "memory_retention": payload.get("memory_retention", "session-first"),
    }
    path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
    return cleaned

def register_routes(app: Flask) -> None:
    """Register all routes onto *app*."""

    @app.route("/")
    def index() -> str:
        """Serve the main dashboard HTML."""
        bridge = _load_orbital_bridge_report()
        manifest = _load_manifest()
        context = {
            "system_mode": bridge.get("recommended_control", {}).get("mode", "guided"),
            "backend_status": "online" if bridge else "offline",
            "manifest_version": manifest.get("schema", "—"),
            "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
            "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
        }
        return render_template("index.html", **context)

    @app.route("/api/status")
    def api_status() -> Response:
        """Return top status bar data as JSON."""
        bridge = _load_orbital_bridge_report()
        manifest = _load_manifest()
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
        }
        return jsonify(payload)

    @app.route("/api/panel")
    def api_panel() -> Response:
        """Return full panel state JSON, reading from pre-built report files."""
        root = _root()
        bridge = _load_orbital_bridge_report()
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

        packet_path = root / "integration" / "reports" / "sapiens_client" / "latest_packet.json"
        packet: dict[str, Any] = {}
        if packet_path.exists():
            try:
                packet = json.loads(packet_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                _LOG.warning("Could not read latest packet at %s: %s", packet_path, exc)

        settings_defaults = _load_settings_defaults()
        preferences = _load_preferences()

        payload = {
            "schema": "ciel-gui-panel/v2",
            "control": {
                "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
                "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
                "mode": bridge.get("recommended_control", {}).get("mode", "guided"),
                "recommended_action": bridge.get("health_manifest", {}).get(
                    "recommended_action", "guided interaction"
                ),
                "eeg_state": packet.get("eeg_state", {}),
                "live_vitals": packet.get("live_vitals", {}),
                "orchestration_layer": packet.get("orchestration_layer", {}),
            },
            "communication": {
                "session": session_data,
                "transcript_preview": transcript[:512] if transcript else "",
                "communication_layer": packet.get("communication_layer", {}),
                "memory_store": packet.get("memory_store", {}),
            },
            "settings": settings_defaults,
            "preferences": preferences,
            "support": {
                "health_manifest": bridge.get("health_manifest", {}),
                "recommended_control": bridge.get("recommended_control", {}),
            },
        }
        return jsonify(payload)

    @app.route("/api/models")
    def api_models() -> Response:
        """Return installed GGUF models."""
        try:
            from ..gguf_manager import GGUFManager

            mgr = GGUFManager()
            return jsonify(
                {
                    "schema": "ciel-gui-models/v1",
                    "models_dir": str(mgr.models_dir),
                    "models": mgr.list_models(),
                    "default_installed": mgr.is_installed(),
                }
            )
        except Exception:
            return jsonify({"error": "model manager unavailable", "models": []}), 500

    @app.route("/api/models/ensure", methods=["POST"])
    def api_models_ensure() -> Response:
        """Trigger download of the default model if not yet installed."""
        try:
            from ..gguf_manager import GGUFManager

            mgr = GGUFManager()
            if mgr.is_installed():
                path = mgr.model_path()
                return jsonify({"status": "already_installed", "path": str(path)})
            # Kick off the download in-process.
            # In production a task queue (Celery / background thread) is preferred.
            path = mgr.ensure_model()
            return jsonify({"status": "installed", "path": str(path)})
        except Exception:
            return (
                jsonify({"status": "error", "error": "model installation failed"}),
                500,
            )



    @app.route("/api/control/options")
    def api_control_options() -> Response:
        return jsonify({
            "schema": "ciel-gui-control-options/v1",
            "modes": ["safe", "guided", "standard", "diagnostic"],
            "orchestration_levels": ["conservative", "balanced", "aggressive"],
            "memory_policies": ["session-first", "hybrid", "persistent"],
        })

    @app.route("/api/preferences", methods=["GET", "POST"])
    def api_preferences() -> Response:
        if request.method == "GET":
            return jsonify(_load_preferences())

        payload = request.get_json(silent=True) or {}
        saved = _persist_preferences(payload)
        return jsonify({"status": "saved", "preferences": saved})

    @app.errorhandler(404)
    def not_found(_err) -> tuple[Response, int]:
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(_err) -> tuple[Response, int]:
        return jsonify({"error": "internal server error"}), 500
