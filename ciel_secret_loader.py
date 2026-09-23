"""Compatibility import for scripts that are imported as modules from repository root.

Direct script execution still resolves ``scripts/ciel_secret_loader.py`` from the
scripts directory. Test/module imports resolve this shim and reuse the same loader
implementation without duplicating secret-handling logic.
"""
from scripts.ciel_secret_loader import load_anthropic_api_key

__all__ = ["load_anthropic_api_key"]
