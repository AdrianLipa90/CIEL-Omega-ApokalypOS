"""Flask route handlers for the CIEL Quiet Orbital Control GUI.

Routes
------
GET  /               — Main dashboard (HTML)
GET  /api/status     — System status JSON (top status bar data)
GET  /api/panel      — Full panel state JSON
GET  /api/models     — Installed GGUF models JSON
POST /api/models/ensure  — Ensure the default model is installed (async-safe)
"""

from __future__ import annotations

import json
import traceback
from pathlib import Path

from flask import Flask, Response, current_app, jsonify, render_template


def _root() -> Path:
    return Path(current_app.config.get("CIEL_ROOT", Path.cwd()))


def _load_orbital_bridge_report() -> dict:
    """Load the latest orbital bridge report if available."""
    root = _root()
    report_path = root / "integration" / "reports" / "orbital_bridge" / "orbital_bridge_report.json"
    if report_path.exists():
        try:
            return json.loads(report_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _load_manifest() -> dict:
    """Load panel manifest if available."""
    root = _root()
    manifest_path = root / "integration" / "sapiens" / "panel_manifest.json"
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


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
        session_data: dict = {}
        if session_path.exists():
            try:
                session_data = json.loads(session_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        transcript_path = root / "integration" / "reports" / "sapiens_client" / "transcript.md"
        transcript = ""
        if transcript_path.exists():
            try:
                transcript = transcript_path.read_text(encoding="utf-8")[:4096]
            except Exception:
                pass

        payload = {
            "schema": "ciel-gui-panel/v1",
            "control": {
                "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
                "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
                "mode": bridge.get("recommended_control", {}).get("mode", "guided"),
                "recommended_action": bridge.get("health_manifest", {}).get(
                    "recommended_action", "guided interaction"
                ),
            },
            "communication": {
                "session": session_data,
                "transcript_preview": transcript[:512] if transcript else "",
            },
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
        except Exception as exc:
            return jsonify({"error": str(exc), "models": []}), 500

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
        except Exception as exc:
            return (
                jsonify({"status": "error", "error": str(exc), "traceback": traceback.format_exc()}),
                500,
            )

    @app.errorhandler(404)
    def not_found(_err) -> tuple[Response, int]:
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(_err) -> tuple[Response, int]:
        return jsonify({"error": "internal server error"}), 500
