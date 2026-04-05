"""GGUF model manager — download and locate small quantised models on first startup.

The manager is intentionally lightweight: it uses only Python stdlib so that the
core package does not require heavy ML dependencies at install time.  The actual
model runner (llama.cpp, ctransformers, etc.) is left to the calling layer.

Usage:
    from ciel_sot_agent.gguf_manager import GGUFManager, download_default_model

    mgr = GGUFManager()
    path = mgr.ensure_model()   # downloads if absent, returns local Path
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# ---------------------------------------------------------------------------
# Canonical default small model
# TinyLlama 1.1B Chat — Q4_K_M quantisation, ~670 MB, Apache-2.0 license.
# Hosted on Hugging Face; this URL is the direct blob link used by the hub.
# ---------------------------------------------------------------------------
_DEFAULT_MODEL = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
_DEFAULT_URL = (
    "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    "/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
)
_DEFAULT_SIZE_BYTES = 669_278_208  # approximate; used for progress reporting only
_DEFAULT_SHA256: str | None = None  # set to hex digest string to enable checksum check


@dataclass
class ModelSpec:
    """Specification for a GGUF model."""

    name: str
    url: str
    expected_size: int = 0
    sha256: str | None = None
    description: str = ""
    tags: list[str] = field(default_factory=list)


# Registry of known small models suitable for first-start install.
KNOWN_MODELS: dict[str, ModelSpec] = {
    "tinyllama-1.1b-chat-q4": ModelSpec(
        name=_DEFAULT_MODEL,
        url=_DEFAULT_URL,
        expected_size=_DEFAULT_SIZE_BYTES,
        sha256=_DEFAULT_SHA256,
        description="TinyLlama 1.1B Chat — Q4_K_M quantisation (~670 MB)",
        tags=["small", "chat", "q4", "default"],
    ),
    "phi-2-q4": ModelSpec(
        name="phi-2.Q4_K_M.gguf",
        url=(
            "https://huggingface.co/TheBloke/phi-2-GGUF"
            "/resolve/main/phi-2.Q4_K_M.gguf"
        ),
        expected_size=1_672_847_360,
        description="Microsoft Phi-2 — Q4_K_M quantisation (~1.6 GB)",
        tags=["small", "chat", "q4"],
    ),
    "qwen2.5-0.5b-q4": ModelSpec(
        name="qwen2.5-0.5b-instruct-q4_k_m.gguf",
        url=(
            "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF"
            "/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"
        ),
        expected_size=397_508_608,
        description="Qwen 2.5 0.5B Instruct — Q4_K_M quantisation (~397 MB)",
        tags=["small", "chat", "q4", "qwen"],
    ),
    "qwen2.5-1.5b-q4": ModelSpec(
        name="qwen2.5-1.5b-instruct-q4_k_m.gguf",
        url=(
            "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF"
            "/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
        ),
        expected_size=986_447_872,
        description="Qwen 2.5 1.5B Instruct — Q4_K_M quantisation (~986 MB)",
        tags=["small", "chat", "q4", "qwen"],
    ),
}


def _default_models_dir() -> Path:
    """Return the user-local directory for CIEL GGUF models."""
    env = os.environ.get("CIEL_MODELS_DIR")
    if env:
        return Path(env).expanduser().resolve()
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / "ciel" / "models"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


class GGUFManager:
    """Manages GGUF model files for the CIEL SOT Agent GUI.

    Parameters
    ----------
    models_dir:
        Directory where GGUF files are stored.  Defaults to
        ``~/.local/share/ciel/models`` (or ``$CIEL_MODELS_DIR``).
    default_model_key:
        Key into ``KNOWN_MODELS`` selecting the default model to install when
        none is present.
    progress_callback:
        Optional callable called during download with ``(bytes_done, total)``
        arguments.  ``total`` is 0 when the server does not advertise
        ``Content-Length``.
    """

    def __init__(
        self,
        models_dir: Path | str | None = None,
        default_model_key: str = "tinyllama-1.1b-chat-q4",
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> None:
        self.models_dir = Path(models_dir) if models_dir else _default_models_dir()
        self.default_model_key = default_model_key
        self.progress_callback = progress_callback
        self._manifest_path = self.models_dir / "manifest.json"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_models(self) -> list[dict]:
        """Return metadata for every *.gguf file currently in models_dir."""
        if not self.models_dir.exists():
            return []
        entries = []
        for p in sorted(self.models_dir.glob("*.gguf")):
            entries.append(
                {
                    "name": p.name,
                    "path": str(p),
                    "size_bytes": p.stat().st_size,
                }
            )
        return entries

    def is_installed(self, model_key: str | None = None) -> bool:
        """Return True if the given (or default) model file exists."""
        path = self.model_path(model_key)
        return path is not None and path.exists()

    def model_path(self, model_key: str | None = None) -> Path | None:
        """Return the local path for *model_key*, or None if not installed."""
        key = model_key or self.default_model_key
        spec = KNOWN_MODELS.get(key)
        if spec is None:
            return None
        return self.models_dir / spec.name

    def ensure_model(self, model_key: str | None = None) -> Path:
        """Return the path to the model, downloading it if necessary.

        Raises
        ------
        ValueError
            If *model_key* is not in ``KNOWN_MODELS``.
        RuntimeError
            If the downloaded file fails a SHA-256 checksum.
        """
        key = model_key or self.default_model_key
        spec = KNOWN_MODELS.get(key)
        if spec is None:
            raise ValueError(f"Unknown model key: {key!r}. Known: {list(KNOWN_MODELS)}")

        dest = self.models_dir / spec.name
        if dest.exists():
            return dest

        self._download(spec, dest)
        return dest

    def save_manifest(self) -> None:
        """Write a JSON manifest of installed models to the models directory."""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        data = {"schema": "ciel-gguf-manifest/v1", "models": self.list_models()}
        self._manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def load_manifest(self) -> dict:
        """Load the last-written manifest, or return an empty structure."""
        if not self._manifest_path.exists():
            return {"schema": "ciel-gguf-manifest/v1", "models": []}
        return json.loads(self._manifest_path.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _download(self, spec: ModelSpec, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(".part")
        try:
            with urllib.request.urlopen(spec.url, timeout=60) as resp:  # noqa: S310
                total = int(resp.headers.get("Content-Length", 0))
                done = 0
                with tmp.open("wb") as fh:
                    while True:
                        chunk = resp.read(65536)
                        if not chunk:
                            break
                        fh.write(chunk)
                        done += len(chunk)
                        if self.progress_callback:
                            self.progress_callback(done, total)
        except Exception:
            if tmp.exists():
                tmp.unlink()
            raise

        if spec.sha256:
            digest = _sha256_file(tmp)
            if digest != spec.sha256:
                tmp.unlink()
                raise RuntimeError(
                    f"SHA-256 mismatch for {spec.name}: "
                    f"expected {spec.sha256}, got {digest}"
                )

        tmp.rename(dest)
        self.save_manifest()


# ---------------------------------------------------------------------------
# Module-level convenience helpers
# ---------------------------------------------------------------------------


def get_model_path(model_key: str | None = None, models_dir: Path | str | None = None) -> Path | None:
    """Return the local path for a model if it exists, else None."""
    mgr = GGUFManager(models_dir=models_dir)
    path = mgr.model_path(model_key)
    return path if (path and path.exists()) else None


def download_default_model(
    models_dir: Path | str | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> Path:
    """Download the default small model and return its local path."""
    mgr = GGUFManager(models_dir=models_dir, progress_callback=progress_callback)
    return mgr.ensure_model()
