#!/usr/bin/env python3
"""Load CIEL secrets from the local secrets directory into environment variables."""
from __future__ import annotations

import os
from pathlib import Path

SECRET_CANDIDATES = [
    Path.home() / "Pulpit/CIEL_memories/secrets/cielapi",
    Path.home() / ".config/ciel/api_key",
]


def load_anthropic_api_key() -> str:
    """Load the Anthropic API key from the first readable secret file."""
    existing = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if existing:
        return existing

    for path in SECRET_CANDIDATES:
        try:
            if path.is_file():
                value = path.read_text(encoding="utf-8").strip()
                if value:
                    os.environ["ANTHROPIC_API_KEY"] = value
                    os.environ.setdefault("CIEL_ANTHROPIC_API_KEY_SOURCE", str(path))
                    return value
        except OSError:
            continue
    return ""
