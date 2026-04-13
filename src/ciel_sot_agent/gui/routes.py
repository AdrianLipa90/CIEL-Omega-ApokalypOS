"""Flask route handlers for the CIEL Quiet Orbital Control GUI."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from flask import Flask, Response, current_app, jsonify, render_template, request

_LOG = logging.getLogger(__name__)

RUNTIME_SETTINGS_PATH = Path("integration") / "sapiens" / "gui_runtime_settings.json"


def _root() -> Path:
    return Path(current_app.config.get("CIEL_ROOT", Path.cwd()))


def _load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        _LOG.warning("Could not read JSON at %s: %s", path, exc)
        return {}


def _load_orbital_bridge_report() -> dict[str, Any]:
    return _load_json_if_exists(_root() / "integration" / "reports" / "orbital_bridge" / "orbital_bridge_report.json")


def _load_manifest() -> dict[str, Any]:
    return _load_json_if_exists(_root() / "integration" / "sapiens" / "panel_manifest.json")


def _default_runtime_settings() -> dict[str, Any]:
    return {
        "schema": "ciel-gui-runtime-settings/v1",
        "preferences": {
            "language": "pl-PL",
            "theme": "quiet-dark",
            "auto_refresh_seconds": 15,
            "show_live_vitals": True,
            "show_eeg_overlay": True,
        },
        "control": {
            "mode": "guided",
            "energy_budget": "warm",
            "safe_guard": True,
            "writeback_gate": False,
        },
        "model": {
            "selected": None,
            "temperature": 0.2,
            "top_p": 0.9,
            "max_tokens": 1024,
        },
    }


def _load_runtime_settings() -> dict[str, Any]:
    root = _root()
    path = root / RUNTIME_SETTINGS_PATH
    current = _load_json_if_exists(path)
    base = _default_runtime_settings()
    if not current:
        return base
    for key in ("preferences", "control", "model"):
        if isinstance(current.get(key), dict):
            base[key].update(current[key])
    base["schema"] = current.get("schema", base["schema"])
    return base


def _save_runtime_settings(payload: dict[str, Any]) -> Path:
    root = _root()
    path = root / RUNTIME_SETTINGS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def register_routes(app: Flask) -> None:
    @app.route("/")
    def index() -> str:
        bridge = _load_orbital_bridge_report()
        manifest = _load_manifest()
        runtime = _load_runtime_settings()
        context = {
            "system_mode": bridge.get("recommended_control", {}).get("mode", runtime["control"]["mode"]),
            "backend_status": "online" if bridge else "offline",
            "manifest_version": manifest.get("schema", "—"),
            "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
            "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
            "selected_model": runtime.get("model", {}).get("selected") or "none",
        }
        return render_template("index.html", **context)

    @app.route("/api/status")
    def api_status() -> Response:
        bridge = _load_orbital_bridge_report()
        manifest = _load_manifest()
        runtime = _load_runtime_settings()
        payload = {
            "schema": "ciel-gui-status/v1",
            "system_mode": bridge.get("recommended_control", {}).get("mode", runtime["control"]["mode"]),
            "writeback_gate": runtime.get("control", {}).get("writeback_gate", False),
            "backend_status": "online" if bridge else "offline",
            "manifest_version": manifest.get("schema", ""),
            "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
            "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
            "closure_penalty": bridge.get("health_manifest", {}).get("closure_penalty", 0.0),
            "energy_budget": runtime.get("control", {}).get("energy_budget", "warm"),
            "selected_model": runtime.get("model", {}).get("selected"),
        }
        return jsonify(payload)

    @app.route("/api/panel")
    def api_panel() -> Response:
        root = _root()
        bridge = _load_orbital_bridge_report()
        runtime = _load_runtime_settings()
        session_data = _load_json_if_exists(root / "integration" / "reports" / "sapiens_client" / "session.json")
        transcript = (root / "integration" / "reports" / "sapiens_client" / "transcript.md").read_text(encoding="utf-8")[:512] if (root / "integration" / "reports" / "sapiens_client" / "transcript.md").exists() else ""

        payload = {
            "schema": "ciel-gui-panel/v2",
            "control": {
                "coherence_index": bridge.get("state_manifest", {}).get("coherence_index", 0.0),
                "system_health": bridge.get("health_manifest", {}).get("system_health", 0.0),
                "mode": bridge.get("recommended_control", {}).get("mode", runtime["control"]["mode"]),
                "recommended_action": bridge.get("health_manifest", {}).get("recommended_action", "guided interaction"),
                "options": {
                    "modes": ["safe", "guided", "standard", "diagnostic"],
                    "energy_budgets": ["cool", "warm", "performance"],
                },
            },
            "communication": {
                "session": session_data,
                "transcript_preview": transcript,
            },
            "settings": runtime,
            "support": {
                "health_manifest": bridge.get("health_manifest", {}),
                "recommended_control": bridge.get("recommended_control", {}),
            },
        }
        return jsonify(payload)

    @app.route("/api/control/options")
    def api_control_options() -> Response:
        bridge = _load_orbital_bridge_report()
        runtime = _load_runtime_settings()
        return jsonify(
            {
                "schema": "ciel-gui-control-options/v1",
                "available_modes": ["safe", "guided", "standard", "diagnostic"],
                "energy_budgets": ["cool", "warm", "performance"],
                "recommended_mode": bridge.get("recommended_control", {}).get("mode", "guided"),
                "current": runtime.get("control", {}),
            }
        )

    @app.route("/api/settings", methods=["GET", "POST"])
    def api_settings() -> Response:
        if request.method == "GET":
            return jsonify(_load_runtime_settings())

        payload = request.get_json(silent=True) or {}
        current = _load_runtime_settings()
        for key in ("preferences", "control", "model"):
            if isinstance(payload.get(key), dict):
                current[key].update(payload[key])
        path = _save_runtime_settings(current)
        return jsonify({"status": "saved", "path": str(path), "settings": current})

    @app.route("/api/preferences", methods=["GET", "POST"])
    def api_preferences() -> Response:
        current = _load_runtime_settings()
        if request.method == "GET":
            return jsonify({"schema": "ciel-gui-preferences/v1", "preferences": current.get("preferences", {})})

        payload = request.get_json(silent=True) or {}
        prefs = payload.get("preferences", {}) if isinstance(payload, dict) else {}
        if isinstance(prefs, dict):
            current["preferences"].update(prefs)
        path = _save_runtime_settings(current)
        return jsonify({"status": "saved", "path": str(path), "preferences": current["preferences"]})

    @app.route("/api/models")
    def api_models() -> Response:
        try:
            from ..gguf_manager import GGUFManager

            mgr = GGUFManager()
            selected = _load_runtime_settings().get("model", {}).get("selected")
            return jsonify(
                {
                    "schema": "ciel-gui-models/v1",
                    "models_dir": str(mgr.models_dir),
                    "models": mgr.list_models(),
                    "default_installed": mgr.is_installed(),
                    "selected_model": selected,
                }
            )
        except Exception:
            return jsonify({"error": "model manager unavailable", "models": []}), 500

    @app.route("/api/models/select", methods=["POST"])
    def api_models_select() -> Response:
        payload = request.get_json(silent=True) or {}
        model_name = payload.get("name")
        settings = _load_runtime_settings()
        settings["model"]["selected"] = model_name
        path = _save_runtime_settings(settings)
        return jsonify({"status": "selected", "selected": model_name, "path": str(path)})

    @app.route("/api/models/ensure", methods=["POST"])
    def api_models_ensure() -> Response:
        try:
            from ..gguf_manager import GGUFManager

            mgr = GGUFManager()
            if mgr.is_installed():
                path = mgr.model_path()
                return jsonify({"status": "already_installed", "path": str(path)})
            path = mgr.ensure_model()
            return jsonify({"status": "installed", "path": str(path)})
        except Exception:
            return jsonify({"status": "error", "error": "model installation failed"}), 500

    @app.errorhandler(404)
    def not_found(_err) -> tuple[Response, int]:
        return jsonify({"error": "not found"}), 404

    @app.errorhandler(500)
    def server_error(_err) -> tuple[Response, int]:
        return jsonify({"error": "internal server error"}), 500
