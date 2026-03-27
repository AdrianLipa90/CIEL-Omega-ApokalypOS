"""CIEL/Ω Quantum Consciousness Suite

Copyright (c) 2025 Adrian Lipa / Intention Lab
Licensed under the CIEL Research Non-Commercial License v1.1.

Minimal data loader for local / remote binary or numeric data.

Source: ext3.SimpleLoader
"""

from __future__ import annotations

from typing import Any, Dict

import numpy as np


class SimpleLoader:
    """Fetch and parse binary data (local files or HTTP URLs)."""

    dtype_map = {8: np.uint8, 16: np.int16, 32: np.int32, -32: np.float32}

    @staticmethod
    def fetch(url_or_path: str) -> bytes:
        if url_or_path.startswith("http"):
            import requests
            return requests.get(url_or_path, stream=True).content
        with open(url_or_path, "rb") as f:
            return f.read()

    @staticmethod
    def parse_header(data: bytes) -> Dict[str, Any]:
        """Parse a FITS-like header from raw bytes."""
        header, pos = b"", 0
        while b"END" not in header and pos < len(data):
            header += data[pos : pos + 2880]
            pos += 2880
        hdr: Dict[str, Any] = {}
        for i in range(0, len(header), 80):
            card = header[i : i + 80].decode("ascii", errors="ignore").strip()
            if card.startswith("END"):
                break
            if "=" in card:
                k, rest = card.split("=", 1)
                k = k.strip()
                v: Any = rest.split("/")[0].strip().strip("'")
                try:
                    v = float(v) if "." in str(v) else int(v)
                except (ValueError, TypeError):
                    pass
                hdr[k] = v
        return hdr


__all__ = ["SimpleLoader"]
