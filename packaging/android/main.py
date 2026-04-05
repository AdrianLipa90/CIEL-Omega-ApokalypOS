"""CIEL Orbital Control — Android entry point (Kivy).

This module provides a lightweight Kivy-based Android companion for the CIEL
SOT Agent.  It connects to a running ciel-sot-gui Flask server (on the same
local network or localhost via ADB forward) and displays the key observables
in a native Android UI following the Quiet Orbital Control identity.

Build with Buildozer (see packaging/android/buildozer.spec):
    cd packaging/android
    buildozer android debug deploy run
"""

from __future__ import annotations

import json
import threading
from typing import Any

try:
    import kivy  # noqa: F401
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.lang import Builder
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.screenmanager import Screen, ScreenManager
except ImportError as exc:
    raise ImportError(
        "Kivy is required for the Android build.  "
        "Install it with: pip install kivy"
    ) from exc

try:
    import urllib.request
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False

# ---------------------------------------------------------------------------
# KV layout definition
# ---------------------------------------------------------------------------
KV = """
#:import get_color_from_hex kivy.utils.get_color_from_hex

<CIELColors@Widget>:
    # Quiet Orbital Control canonical palette (Kivy rgba 0-1)
    col_bg:           get_color_from_hex('#0e0f18ff')
    col_panel:        get_color_from_hex('#13151fff')
    col_surface:      get_color_from_hex('#1a1d2bff')
    col_cyan:         get_color_from_hex('#4fc3c3ff')
    col_amber:        get_color_from_hex('#e8b554ff')
    col_text:         get_color_from_hex('#c8ccd8ff')
    col_text_muted:   get_color_from_hex('#7a7e94ff')

ScreenManager:
    ControlScreen:
        name: 'control'
    SettingsScreen:
        name: 'settings'

<ControlScreen>:
    name: 'control'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: get_color_from_hex('#0e0f18ff')
            Rectangle:
                pos: self.pos
                size: self.size

        # Top bar
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            padding: '12dp', '8dp'
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#0b0d16ff')
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: 'CIEL'
                bold: True
                font_size: '14sp'
                color: get_color_from_hex('#c8ccd8ff')
                size_hint_x: None
                width: '60dp'
            Label:
                id: lbl_mode
                text: 'MODE: —'
                font_size: '11sp'
                color: get_color_from_hex('#7a7e94ff')
            Label:
                id: lbl_status
                text: 'BACKEND: —'
                font_size: '11sp'
                color: get_color_from_hex('#7a7e94ff')

        # Main content
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: '16dp'
                spacing: '12dp'

                # Coherence metric card
                BoxLayout:
                    size_hint_y: None
                    height: '90dp'
                    orientation: 'vertical'
                    padding: '14dp', '10dp'
                    spacing: '6dp'
                    canvas.before:
                        Color:
                            rgba: get_color_from_hex('#1a1d2bff')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8]
                    Label:
                        text: 'COHERENCE INDEX'
                        font_size: '9sp'
                        color: get_color_from_hex('#454962ff')
                        halign: 'left'
                        text_size: self.size
                    Label:
                        id: lbl_coherence
                        text: '—'
                        font_size: '28sp'
                        bold: True
                        color: get_color_from_hex('#7c6fbdff')
                        halign: 'left'
                        text_size: self.size

                # System Health metric card
                BoxLayout:
                    size_hint_y: None
                    height: '90dp'
                    orientation: 'vertical'
                    padding: '14dp', '10dp'
                    spacing: '6dp'
                    canvas.before:
                        Color:
                            rgba: get_color_from_hex('#1a1d2bff')
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [8]
                    Label:
                        text: 'SYSTEM HEALTH'
                        font_size: '9sp'
                        color: get_color_from_hex('#454962ff')
                        halign: 'left'
                        text_size: self.size
                    Label:
                        id: lbl_health
                        text: '—'
                        font_size: '28sp'
                        bold: True
                        color: get_color_from_hex('#4fc3c3ff')
                        halign: 'left'
                        text_size: self.size

                # Refresh button
                Button:
                    text: 'Refresh'
                    size_hint_y: None
                    height: '44dp'
                    on_press: app.refresh_status()
                    background_color: get_color_from_hex('#1c1f30ff')
                    color: get_color_from_hex('#4fc3c3ff')

<SettingsScreen>:
    name: 'settings'
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: get_color_from_hex('#0e0f18ff')
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'Settings'
            font_size: '20sp'
            color: get_color_from_hex('#c8ccd8ff')
        Label:
            text: 'Server URL: http://127.0.0.1:5050'
            font_size: '12sp'
            color: get_color_from_hex('#7a7e94ff')
"""


# ---------------------------------------------------------------------------
# Screen classes
# ---------------------------------------------------------------------------

class ControlScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

class CIELOrbitalApp(App):
    """CIEL Quiet Orbital Control — Kivy Android application."""

    SERVER_URL = "http://127.0.0.1:5050"

    def build(self):
        return Builder.load_string(KV)

    def on_start(self):
        self.refresh_status()
        # Schedule periodic refresh every 15 s (energy-aware)
        Clock.schedule_interval(lambda _dt: self.refresh_status(), 15)

    def refresh_status(self):
        """Fetch /api/status in a background thread."""
        if not _HAS_URLLIB:
            return
        threading.Thread(target=self._fetch_status, daemon=True).start()

    def _fetch_status(self):
        try:
            url = f"{self.SERVER_URL}/api/status"
            with urllib.request.urlopen(url, timeout=5) as resp:  # noqa: S310
                data: dict[str, Any] = json.loads(resp.read().decode())
            Clock.schedule_once(lambda _dt: self._apply_status(data))
        except Exception:
            pass

    def _apply_status(self, data: dict[str, Any]) -> None:
        sm: ScreenManager = self.root
        screen: ControlScreen = sm.get_screen("control")
        screen.ids.lbl_mode.text = f"MODE: {data.get('system_mode', '—')}"
        screen.ids.lbl_status.text = f"BACKEND: {data.get('backend_status', '—')}"

        ci = data.get("coherence_index")
        if ci is not None:
            screen.ids.lbl_coherence.text = f"{ci:.2f}"

        sh = data.get("system_health")
        if sh is not None:
            screen.ids.lbl_health.text = f"{sh:.2f}"


def main() -> None:
    CIELOrbitalApp().run()


if __name__ == "__main__":
    main()
