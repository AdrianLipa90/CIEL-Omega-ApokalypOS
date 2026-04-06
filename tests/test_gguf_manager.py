"""Tests for the CIEL GGUF model manager.

These tests do NOT perform real network downloads.  They verify:
- GGUFManager API contracts
- model_path / is_installed logic
- list_models with real filesystem
- manifest read/write round-trip
- ensure_model download path is exercised via monkeypatching
- ModelSpec and KNOWN_MODELS registry
- Module-level helpers (get_model_path, download_default_model)
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.ciel_sot_agent.gguf_manager.manager import (
    KNOWN_MODELS,
    GGUFManager,
    ModelSpec,
    _default_models_dir,
    download_default_model,
    get_model_path,
)


# ---------------------------------------------------------------------------
# KNOWN_MODELS registry
# ---------------------------------------------------------------------------

class TestKnownModels:
    def test_registry_not_empty(self):
        assert len(KNOWN_MODELS) >= 1

    def test_default_key_present(self):
        assert "tinyllama-1.1b-chat-q4" in KNOWN_MODELS

    def test_each_spec_has_name_and_url(self):
        for key, spec in KNOWN_MODELS.items():
            assert spec.name, f"ModelSpec {key!r} has empty name"
            assert spec.url.startswith("https://"), f"ModelSpec {key!r} has unexpected URL"

    def test_spec_tags_are_list(self):
        for spec in KNOWN_MODELS.values():
            assert isinstance(spec.tags, list)


# ---------------------------------------------------------------------------
# ModelSpec dataclass
# ---------------------------------------------------------------------------

class TestModelSpec:
    def test_create_minimal(self):
        spec = ModelSpec(name="test.gguf", url="https://example.com/test.gguf")
        assert spec.name == "test.gguf"
        assert spec.sha256 is None
        assert spec.tags == []

    def test_create_full(self):
        spec = ModelSpec(
            name="m.gguf",
            url="https://example.com/m.gguf",
            expected_size=1000,
            sha256="abc123",
            description="test model",
            tags=["small", "q4"],
        )
        assert spec.expected_size == 1000
        assert spec.sha256 == "abc123"
        assert "small" in spec.tags


# ---------------------------------------------------------------------------
# GGUFManager — path and existence checks
# ---------------------------------------------------------------------------

class TestGGUFManagerPaths:
    def test_models_dir_uses_custom_path(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        assert mgr.models_dir == tmp_path

    def test_model_path_returns_expected_name(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        path = mgr.model_path("tinyllama-1.1b-chat-q4")
        assert path is not None
        assert path.name == KNOWN_MODELS["tinyllama-1.1b-chat-q4"].name

    def test_model_path_unknown_key_returns_none(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        assert mgr.model_path("nonexistent-model-xyz") is None

    def test_is_installed_false_when_file_missing(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        assert mgr.is_installed() is False

    def test_is_installed_true_when_file_present(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        spec = KNOWN_MODELS[mgr.default_model_key]
        (tmp_path / spec.name).write_bytes(b"fake")
        assert mgr.is_installed() is True


# ---------------------------------------------------------------------------
# GGUFManager — list_models
# ---------------------------------------------------------------------------

class TestGGUFManagerListModels:
    def test_list_empty_when_dir_missing(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path / "nonexistent")
        assert mgr.list_models() == []

    def test_list_returns_gguf_files(self, tmp_path):
        (tmp_path / "model_a.gguf").write_bytes(b"x" * 100)
        (tmp_path / "model_b.gguf").write_bytes(b"x" * 200)
        (tmp_path / "other.txt").write_text("not a model")
        mgr = GGUFManager(models_dir=tmp_path)
        entries = mgr.list_models()
        names = {e["name"] for e in entries}
        assert "model_a.gguf" in names
        assert "model_b.gguf" in names
        assert "other.txt" not in names

    def test_list_includes_size_and_path(self, tmp_path):
        (tmp_path / "m.gguf").write_bytes(b"x" * 512)
        mgr = GGUFManager(models_dir=tmp_path)
        entries = mgr.list_models()
        assert entries[0]["size_bytes"] == 512
        assert "path" in entries[0]


# ---------------------------------------------------------------------------
# GGUFManager — manifest
# ---------------------------------------------------------------------------

class TestGGUFManagerManifest:
    def test_load_manifest_empty_when_missing(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        manifest = mgr.load_manifest()
        assert manifest["schema"] == "ciel-gguf-manifest/v1"
        assert manifest["models"] == []

    def test_save_and_load_manifest_round_trip(self, tmp_path):
        (tmp_path / "m.gguf").write_bytes(b"data")
        mgr = GGUFManager(models_dir=tmp_path)
        mgr.save_manifest()
        loaded = mgr.load_manifest()
        assert loaded["schema"] == "ciel-gguf-manifest/v1"
        names = [e["name"] for e in loaded["models"]]
        assert "m.gguf" in names

    def test_manifest_path_is_inside_models_dir(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        assert mgr._manifest_path.parent == tmp_path


# ---------------------------------------------------------------------------
# GGUFManager — ensure_model (mocked download)
# ---------------------------------------------------------------------------

class TestGGUFManagerEnsureModel:
    def test_ensure_returns_existing_file(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        spec = KNOWN_MODELS[mgr.default_model_key]
        dest = tmp_path / spec.name
        dest.write_bytes(b"fake model data")
        result = mgr.ensure_model()
        assert result == dest

    def test_ensure_raises_for_unknown_key(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        with pytest.raises(ValueError, match="Unknown model key"):
            mgr.ensure_model("totally-unknown-key-xyz")

    def test_ensure_calls_download_when_missing(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        spec = KNOWN_MODELS[mgr.default_model_key]

        # Simulate a successful download by writing the file in _download
        def fake_download(s, dest):
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b"fake gguf")

        with patch.object(mgr, "_download", side_effect=fake_download) as mock_dl:
            path = mgr.ensure_model()
            mock_dl.assert_called_once()
            assert path.exists()
            assert path.name == spec.name

    def test_progress_callback_receives_calls(self, tmp_path):
        calls = []

        def cb(done, total):
            calls.append((done, total))

        mgr = GGUFManager(models_dir=tmp_path, progress_callback=cb)
        spec = KNOWN_MODELS[mgr.default_model_key]

        def fake_download(s, dest):
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Simulate calling progress callback
            if mgr.progress_callback:
                mgr.progress_callback(1024, 2048)
            dest.write_bytes(b"fake")

        with patch.object(mgr, "_download", side_effect=fake_download):
            mgr.ensure_model()

        assert len(calls) >= 1

    def test_partial_file_cleaned_on_download_error(self, tmp_path):
        mgr = GGUFManager(models_dir=tmp_path)
        spec = KNOWN_MODELS[mgr.default_model_key]
        dest = tmp_path / spec.name

        def failing_download(s, d):
            d.parent.mkdir(parents=True, exist_ok=True)
            tmp = d.with_suffix(".part")
            tmp.write_bytes(b"partial")
            raise IOError("network error")

        with patch.object(mgr, "_download", side_effect=failing_download):
            with pytest.raises(IOError):
                mgr.ensure_model()

        assert not dest.exists()


# ---------------------------------------------------------------------------
# GGUFManager — SHA-256 verification (via _download directly)
# ---------------------------------------------------------------------------

class TestSHA256Verification:
    def test_sha256_mismatch_raises_and_removes_file(self, tmp_path):
        """_download should raise RuntimeError if SHA-256 doesn't match."""
        mgr = GGUFManager(models_dir=tmp_path)
        spec = ModelSpec(
            name="test.gguf",
            url="https://example.com/test.gguf",
            sha256="0" * 64,  # Wrong digest
        )
        dest = tmp_path / "test.gguf"
        tmp_part = dest.with_suffix(".part")

        # Fake HTTP response
        fake_response = MagicMock()
        fake_response.__enter__ = lambda s: s
        fake_response.__exit__ = MagicMock(return_value=False)
        fake_response.headers = {"Content-Length": "5"}
        fake_response.read.side_effect = [b"hello", b""]

        with patch("urllib.request.urlopen", return_value=fake_response):
            with pytest.raises(RuntimeError, match="SHA-256 mismatch"):
                mgr._download(spec, dest)

        assert not dest.exists()
        assert not tmp_part.exists()


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

class TestModuleHelpers:
    def test_get_model_path_returns_none_when_missing(self, tmp_path):
        result = get_model_path(models_dir=tmp_path)
        assert result is None

    def test_get_model_path_returns_path_when_present(self, tmp_path):
        spec = KNOWN_MODELS["tinyllama-1.1b-chat-q4"]
        (tmp_path / spec.name).write_bytes(b"fake")
        result = get_model_path("tinyllama-1.1b-chat-q4", models_dir=tmp_path)
        assert result is not None
        assert result.name == spec.name

    def test_download_default_model_calls_ensure(self, tmp_path):
        with patch.object(GGUFManager, "ensure_model") as mock_ensure:
            mock_ensure.return_value = tmp_path / "model.gguf"
            result = download_default_model(models_dir=tmp_path)
            mock_ensure.assert_called_once()

    def test_default_models_dir_env_var(self, monkeypatch, tmp_path):
        monkeypatch.setenv("CIEL_MODELS_DIR", str(tmp_path))
        result = _default_models_dir()
        assert result == tmp_path.resolve()

    def test_default_models_dir_xdg(self, monkeypatch, tmp_path):
        monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
        monkeypatch.delenv("CIEL_MODELS_DIR", raising=False)
        result = _default_models_dir()
        assert result == tmp_path / "ciel" / "models"
