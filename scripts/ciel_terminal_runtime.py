#!/usr/bin/env python3
"""Persistent CIEL terminal launcher with File-Library provenance attestation.

The launcher activates only when:
- the repository cli.py is byte-identical to the verified File-Library ZIP member;
- the live NOEMA<->AUX surface is ACTIVE and all three 36D float64 buffers are valid.

No alternate terminal implementation is silently substituted.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import struct
import sys
from pathlib import Path

REQUIRED_CLI_SHA256 = "64679c7d2ddf9304f17c5833d7400bb3a1c24b7eb265e95213aaff8bd4da7b8e"
REQUIRED_ARCHIVE_SHA256 = "fef25a4cb20380483fec5b3e84ad8a2d1465e6a53ecf6dfd9ec42ec67d82e9ef"
N = 36
VECTOR_BYTES = N * 8


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_vector(path: Path) -> dict:
    raw = path.read_bytes()
    if len(raw) != VECTOR_BYTES:
        raise RuntimeError(f"BAD_VECTOR_SIZE:{path}:{len(raw)}")
    values = struct.unpack("<36d", raw)
    if not all(math.isfinite(x) for x in values):
        raise RuntimeError(f"NONFINITE_VECTOR:{path}")
    return {"path": str(path), "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def verify_tether(root: Path) -> dict:
    status_path = root / "ciel_binding_status"
    if not status_path.is_file() or status_path.read_text(encoding="utf-8").strip() != "ACTIVE":
        raise RuntimeError("TETHER_NOT_ACTIVE")
    vectors = {name: verify_vector(root / name) for name in ("phi", "aux_phi", "aux_feedback_phi")}
    for required in (root / "session" / "startpoint.json", root / "session" / "system_message.txt"):
        if not required.is_file():
            raise RuntimeError(f"MISSING_SESSION_FILE:{required}")
    return {"status": "ACTIVE", "root": str(root), "vectors": vectors}


def locate_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def verify_terminal(repo_root: Path) -> dict:
    cli = repo_root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega" / "ciel" / "cli.py"
    if not cli.is_file():
        raise RuntimeError(f"CIEL_TERMINAL_MISSING:{cli}")
    digest = sha256_file(cli)
    if digest != REQUIRED_CLI_SHA256:
        raise RuntimeError(f"CIEL_TERMINAL_SHA_MISMATCH:{digest}")
    return {
        "status": "VERIFIED_LIBRARY_MEMBER_MATCH",
        "path": str(cli),
        "sha256": digest,
        "archive_sha256": REQUIRED_ARCHIVE_SHA256,
    }


def load_cli(repo_root: Path):
    cli_path = repo_root / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM" / "ciel_omega" / "ciel" / "cli.py"
    omega_root = cli_path.parents[1]
    if str(omega_root) not in sys.path:
        sys.path.insert(0, str(omega_root))
    spec = importlib.util.spec_from_file_location("_noema_verified_ciel_cli", cli_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("CIEL_TERMINAL_IMPORT_SPEC_FAILED")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description="Verified persistent CIEL terminal runtime")
    ap.add_argument("text", nargs="?", default="hello from CIEL")
    ap.add_argument("--root", default="/dev/shm/ciel_noema", help="live NOEMA surface root")
    ap.add_argument("--smoke", action="store_true", help="run CIEL handshake smoke test")
    ap.add_argument("--verify-only", action="store_true", help="attest terminal and tether without invoking CIEL")
    args = ap.parse_args()

    repo = locate_repo_root()
    terminal = verify_terminal(repo)
    tether = verify_tether(Path(args.root))
    receipt = {
        "schema": "noema.ciel-terminal-activation/v1",
        "status": "PASS",
        "terminal": terminal,
        "tether": tether,
        "engine_bypass": False,
        "surface": "CIELClient",
        "persistence": "PERSISTENT_PROJECT_RUNTIME",
    }
    if args.verify_only:
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0

    mod = load_cli(repo)
    if args.smoke:
        mod.smoke_test()
        return 0
    result = mod._run_client(args.text)
    print(json.dumps(result, indent=2, sort_keys=True, default=mod._json_default, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
