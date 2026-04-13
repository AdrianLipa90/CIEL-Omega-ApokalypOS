"""Flask application factory and entry-point for the CIEL Quiet Orbital Control GUI.

The GUI is intentionally a *consumer* of prepared state — it reads manifests,
reports, and session files written by backend modules rather than performing
heavy computation itself.  This follows the "GUI consumes state; GUI does not
impersonate runtime" principle from the CIEL GUI Identity Brief.

Entry-point usage:
    ciel-sot-gui [--host HOST] [--port PORT] [--debug]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from typing import Any

from .routes import register_routes


def create_app(root: str | Path | None = None, debug: bool = False) -> Any:
    """Create and configure the Flask application.

    Parameters
    ----------
    root:
        Repository / project root.  When *None* the working directory is used.
    debug:
        Enable Flask debug mode (development only).
    """
    try:
        from flask import Flask
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Flask is required to run the CIEL GUI.  "
            "Install it with: pip install 'ciel-sot-agent[gui]'"
        ) from exc

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
        static_url_path="/static",
    )
    app.config["DEBUG"] = debug
    app.config["CIEL_ROOT"] = Path(root) if root else Path.cwd()

    register_routes(app)
    return app


def main(argv: list[str] | None = None) -> None:
    """CLI entry-point: ``ciel-sot-gui``."""
    parser = argparse.ArgumentParser(
        prog="ciel-sot-gui",
        description="Launch the CIEL Quiet Orbital Control web interface.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", default=5050, type=int, help="Bind port (default: 5050)")
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    parser.add_argument("--root", default=None, help="Project root directory")

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    app = create_app(root=args.root, debug=args.debug)
    app.run(host=args.host, port=args.port, debug=args.debug)
