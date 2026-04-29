#!/usr/bin/env python3
"""
CIEL/Ω System Launcher

Uruchamia cały system CIEL:
  1. Sprawdza i instaluje zależności GUI
  2. Uruchamia CIEL pipeline (synchronize → orbital_bridge) w tle
  3. Otwiera GUI NiceGUI z ikoną Logo1.png w przeglądarce

Użycie:
    python scripts/ciel_launch.py
    python scripts/ciel_launch.py --no-pipeline   # tylko GUI
    python scripts/ciel_launch.py --port 9090
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

# ── Ścieżki ──────────────────────────────────────────────────────────────────

PROJECT_DIR   = Path(__file__).resolve().parent.parent
DEMO_DIR      = PROJECT_DIR / "src" / "ciel-omega-demo-main"
VENV_PY       = Path("/tmp/ciel_venv/bin/python3")
REQUIREMENTS  = DEMO_DIR / "requirements.txt"
APP_ENTRY     = DEMO_DIR / "ciel_omega_app.py"
LOGO_PATH     = DEMO_DIR / "main" / "Logo1.png"
DESKTOP_FILE  = Path.home() / "Pulpit" / "CIEL_Omega.desktop"


# ── Instalacja zależności GUI ─────────────────────────────────────────────────

def ensure_gui_deps() -> None:
    print("[CIEL] Sprawdzam zależności GUI...")
    try:
        import nicegui  # noqa: F401
        import psutil   # noqa: F401
        print("[CIEL] Zależności OK.")
    except ImportError:
        print("[CIEL] Instaluję zależności z requirements.txt...")
        subprocess.run(
            [str(VENV_PY), "-m", "pip", "install", "-r", str(REQUIREMENTS), "-q"],
            check=True,
        )
        print("[CIEL] Zależności zainstalowane.")


# ── CIEL pipeline w tle ───────────────────────────────────────────────────────

def start_pipeline() -> list[subprocess.Popen]:
    procs = []
    print("[CIEL] Uruchamiam pipeline (synchronize → orbital_bridge)...")

    try:
        p1 = subprocess.Popen(
            [str(VENV_PY), "-m", "ciel_sot_agent.synchronize"],
            cwd=str(PROJECT_DIR / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        procs.append(p1)
        time.sleep(1.5)
        print("[CIEL]   ✓ synchronize (PID {})".format(p1.pid))
    except Exception as e:
        print(f"[CIEL]   ⚠ synchronize: {e}")

    try:
        p2 = subprocess.Popen(
            [str(VENV_PY), "-m", "ciel_sot_agent.orbital_bridge"],
            cwd=str(PROJECT_DIR / "src" / "CIEL_OMEGA_COMPLETE_SYSTEM"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        procs.append(p2)
        time.sleep(1.0)
        print("[CIEL]   ✓ orbital_bridge (PID {})".format(p2.pid))
    except Exception as e:
        print(f"[CIEL]   ⚠ orbital_bridge: {e}")

    return procs


# ── .desktop launcher na Pulpicie ────────────────────────────────────────────

def create_desktop_file(port: int) -> None:
    """Tworzy ikonę .desktop na Pulpicie (Linux freedesktop standard)."""
    content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=CIEL/Ω
Comment=CIEL Omega — Live Digital Intelligence Engine
Exec={VENV_PY} {APP_ENTRY}
Icon={LOGO_PATH}
Terminal=false
Categories=Science;Education;
StartupWMClass=CIEL
"""
    DESKTOP_FILE.write_text(content, encoding="utf-8")
    DESKTOP_FILE.chmod(0o755)
    print(f"[CIEL] Ikona na Pulpicie: {DESKTOP_FILE}")


# ── Główny launcher ───────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="CIEL/Ω System Launcher")
    parser.add_argument("--port",        type=int, default=8080,  help="Port GUI (domyślnie 8080)")
    parser.add_argument("--no-pipeline", action="store_true",     help="Nie uruchamiaj pipeline")
    parser.add_argument("--no-browser",  action="store_true",     help="Nie otwieraj przeglądarki")
    args = parser.parse_args()

    print("=" * 60)
    print("  CIEL/Ω SYSTEM LAUNCHER")
    print(f"  Projekt: {PROJECT_DIR}")
    print(f"  Port:    {args.port}")
    print("=" * 60)

    # 1. Zależności
    ensure_gui_deps()

    # 2. Desktop icon
    create_desktop_file(args.port)

    # 3. Pipeline w tle
    pipeline_procs = []
    if not args.no_pipeline:
        pipeline_procs = start_pipeline()

    # 4. Otwórz przeglądarkę po 2s
    if not args.no_browser:
        url = f"http://127.0.0.1:{args.port}"
        print(f"[CIEL] GUI: {url}")

        def _open_browser():
            time.sleep(2.5)
            webbrowser.open(url)

        import threading
        threading.Thread(target=_open_browser, daemon=True).start()

    # 5. Uruchom GUI (blokujące)
    print("[CIEL] Startuje GUI...")
    env = {
        "CIEL_HOST": "127.0.0.1",
        "CIEL_PORT": str(args.port),
        **__import__("os").environ,
    }

    try:
        result = subprocess.run(
            [str(VENV_PY), str(APP_ENTRY)],
            cwd=str(DEMO_DIR),
            env=env,
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\n[CIEL] Zamykam system...")
        for p in pipeline_procs:
            p.terminate()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
