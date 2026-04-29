"""GGUF model manager for CIEL SOT Agent."""

from .manager import GGUFManager, ModelSpec, download_default_model, get_model_path

__all__ = ["GGUFManager", "ModelSpec", "download_default_model", "get_model_path"]
