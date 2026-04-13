"""Tests for the Flask-based CIEL Quiet Orbital Control GUI.

These tests use Flask's built-in test client and do not require a running
server.  They verify:
- App factory creates a valid Flask app
- All registered routes return expected HTTP status codes
- API endpoints return correct JSON schemas
- The index route renders HTML containing key UI elements
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# Skip entire module if Flask is not installed (shouldn't happen in dev,
# but guards against minimal install environments).
pytest.importorskip("flask")

from src.ciel_sot_agent.gui.app import create_app  # noqa: E402


@pytest.fixture()
def app():
    """Create a test Flask application instance."""
    root = Path(__file__).resolve().parents[1]
    app = create_app(root=root, debug=False)
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(app):
    """Return a Flask test client."""
    return app.test_client()


# -------------------------------------------------------------------
# Index / HTML routes
# -------------------------------------------------------------------

class TestIndexRoute:
    def test_index_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert b"text/html" in resp.content_type.encode() or b"html" in resp.data.lower()

    def test_index_contains_ciel_brand(self, client):
        resp = client.get("/")
        assert b"CIEL" in resp.data

    def test_index_contains_nav_sections(self, client):
        resp = client.get("/")
        data = resp.data
        # Navigation rail items should be present
        assert b"Control" in data
        assert b"Settings" in data
        assert b"Support" in data

    def test_index_contains_quiet_orbital_identity(self, client):
        resp = client.get("/")
        # Identity phrase must appear somewhere in the HTML
        assert b"Orbital" in resp.data or b"orbital" in resp.data


# -------------------------------------------------------------------
# /api/status
# -------------------------------------------------------------------

class TestApiStatus:
    def test_status_returns_200(self, client):
        resp = client.get("/api/status")
        assert resp.status_code == 200

    def test_status_returns_json(self, client):
        resp = client.get("/api/status")
        assert resp.is_json

    def test_status_schema(self, client):
        resp = client.get("/api/status")
        data = resp.get_json()
        assert data["schema"] == "ciel-gui-status/v1"

    def test_status_has_required_fields(self, client):
        resp = client.get("/api/status")
        data = resp.get_json()
        required = {
            "system_mode", "writeback_gate", "backend_status",
            "manifest_version", "coherence_index", "system_health",
            "closure_penalty", "energy_budget",
        }
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_status_coherence_is_float(self, client):
        resp = client.get("/api/status")
        data = resp.get_json()
        assert isinstance(data["coherence_index"], (int, float))

    def test_status_health_is_float(self, client):
        resp = client.get("/api/status")
        data = resp.get_json()
        assert isinstance(data["system_health"], (int, float))


# -------------------------------------------------------------------
# /api/panel
# -------------------------------------------------------------------

class TestApiPanel:
    def test_panel_returns_200(self, client):
        resp = client.get("/api/panel")
        assert resp.status_code == 200

    def test_panel_returns_json(self, client):
        resp = client.get("/api/panel")
        assert resp.is_json

    def test_panel_schema(self, client):
        resp = client.get("/api/panel")
        data = resp.get_json()
        assert data["schema"] == "ciel-gui-panel/v2"

    def test_panel_has_control_section(self, client):
        resp = client.get("/api/panel")
        data = resp.get_json()
        assert "control" in data
        assert "coherence_index" in data["control"]
        assert "system_health" in data["control"]
        assert "mode" in data["control"]

    def test_panel_has_communication_section(self, client):
        resp = client.get("/api/panel")
        data = resp.get_json()
        assert "communication" in data

    def test_panel_has_support_section(self, client):
        resp = client.get("/api/panel")
        data = resp.get_json()
        assert "support" in data


# -------------------------------------------------------------------
# /api/models
# -------------------------------------------------------------------

class TestApiModels:
    def test_models_returns_200_or_500(self, client):
        # 200 is expected; 500 only if GGUF manager itself fails unexpectedly
        resp = client.get("/api/models")
        assert resp.status_code in (200, 500)

    def test_models_returns_json(self, client):
        resp = client.get("/api/models")
        assert resp.is_json

    def test_models_has_schema_on_success(self, client):
        resp = client.get("/api/models")
        if resp.status_code == 200:
            data = resp.get_json()
            assert data["schema"] == "ciel-gui-models/v1"
            assert "models" in data
            assert isinstance(data["models"], list)
            assert "default_installed" in data

    def test_models_ensure_post_method_required(self, client):
        # GET on /api/models/ensure should return 405
        resp = client.get("/api/models/ensure")
        assert resp.status_code == 405


# -------------------------------------------------------------------
# 404 handler
# -------------------------------------------------------------------

class TestErrorHandlers:
    def test_404_returns_json(self, client):
        resp = client.get("/nonexistent-route-xyz")
        assert resp.status_code == 404
        assert resp.is_json
        data = resp.get_json()
        assert "error" in data




# -------------------------------------------------------------------
# /api/settings, /api/preferences, /api/control/options, /api/models/select
# -------------------------------------------------------------------

class TestGuiSettingsAndControl:
    def test_control_options_returns_200(self, client):
        resp = client.get('/api/control/options')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['schema'] == 'ciel-gui-control-options/v1'
        assert 'available_modes' in data

    def test_settings_get_returns_runtime_schema(self, client):
        resp = client.get('/api/settings')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['schema'] == 'ciel-gui-runtime-settings/v1'
        assert 'preferences' in data
        assert 'control' in data
        assert 'model' in data

    def test_settings_post_persists_payload(self, client):
        payload = {'control': {'mode': 'safe'}, 'preferences': {'language': 'pl-PL'}}
        resp = client.post('/api/settings', data=json.dumps(payload), content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'saved'
        assert data['settings']['control']['mode'] == 'safe'

    def test_preferences_roundtrip(self, client):
        payload = {'preferences': {'theme': 'high-contrast'}}
        post = client.post('/api/preferences', data=json.dumps(payload), content_type='application/json')
        assert post.status_code == 200
        get_resp = client.get('/api/preferences')
        assert get_resp.status_code == 200
        data = get_resp.get_json()
        assert data['preferences']['theme'] == 'high-contrast'

    def test_model_select_accepts_name(self, client):
        resp = client.post('/api/models/select', data=json.dumps({'name': 'demo-model.gguf'}), content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'selected'
        assert data['selected'] == 'demo-model.gguf'

# -------------------------------------------------------------------
# App factory
# -------------------------------------------------------------------

class TestAppFactory:
    def test_create_app_with_explicit_root(self, tmp_path):
        app = create_app(root=tmp_path, debug=False)
        assert app is not None
        assert app.config["CIEL_ROOT"] == tmp_path

    def test_create_app_debug_mode(self, tmp_path):
        app = create_app(root=tmp_path, debug=True)
        assert app.config["DEBUG"] is True

    def test_create_app_registers_routes(self, tmp_path):
        app = create_app(root=tmp_path)
        rules = {r.rule for r in app.url_map.iter_rules()}
        assert "/" in rules
        assert "/api/status" in rules
        assert "/api/panel" in rules
        assert "/api/models" in rules
        assert "/api/models/ensure" in rules
        assert "/api/control/options" in rules
        assert "/api/settings" in rules
        assert "/api/preferences" in rules
        assert "/api/models/select" in rules
