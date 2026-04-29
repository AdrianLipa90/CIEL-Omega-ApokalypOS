#!/usr/bin/env python3
"""
CIEL Portal Server — serwuje ~/.claude/ciel_site/ przez HTTP.

Funkcje:
  - Serwuje portal jako http://localhost:7481/
  - /api/live  — live metryki z pickle (cycle, health, ethical, closure, emotion)
  - /api/state — pełny stan orbitalny z ostatniego raportu
  - Wstrzykuje do każdej strony HTML auto-refresh JS (polling /api/live co 8s)
  - Automatycznie przebudowuje portal gdy źródła się zmieniają (opcjonalnie)

Uruchomienie:
  /tmp/ciel_venv/bin/python3 scripts/serve_portal.py
  /tmp/ciel_venv/bin/python3 scripts/serve_portal.py --port 7481 --no-watch

Zatrzymanie: Ctrl+C
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

PROJECT  = Path(__file__).resolve().parents[1]
HOME     = Path.home()
SITE_DIR = HOME / ".claude/ciel_site"
STATE_FILE       = Path.home() / "Pulpit/CIEL_memories/state/ciel_orch_state.pkl"
STATE_PERSIST    = HOME / ".claude/ciel_orch_state.pkl"
BRIDGE_REPORT    = PROJECT / "integration/reports/orbital_bridge/orbital_bridge_report.json"
PIPELINE_REPORT  = PROJECT / "integration/reports/ciel_pipeline_report.json"
STATE_DB         = HOME / ".claude/ciel_state.db"
MEMORIES_DB      = HOME / "Pulpit/CIEL_memories/memories_index.db"
MEMORY_DIR       = HOME / ".claude/projects/-home-adrian/memory"
COUPLINGS_FILE   = PROJECT / "integration/Orbital/main/manifests/couplings_global.json"
ORBITAL_SUMMARY  = PROJECT / "integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json"
VENV_PY          = next(
    (p for p in [
        PROJECT.parent.parent / "venv/bin/python3.12",
        Path.home() / "Pulpit/CIEL_TESTY/venv/bin/python3.12",
        Path(sys.executable),
    ] if Path(p).exists()),
    Path(sys.executable),
)

# ── live state reader ──────────────────────────────────────────────────────

def read_live_state() -> dict:
    """Read current CIEL state from pickle + orbital report."""
    state: dict = {}

    # From orchestrator pickle
    for path in (STATE_FILE, STATE_PERSIST):
        if not path.exists():
            continue
        try:
            with open(path, "rb") as f:
                orch = pickle.load(f)
            snap_fn = getattr(orch, "snapshot", None)
            snap = snap_fn() if snap_fn else None
            if snap:
                state["cycle"]          = getattr(snap, "cycle_index", "?")
                state["identity_phase"] = round(float(getattr(snap, "identity_phase", 0)), 4)
                counts = getattr(snap, "counts", {})
                state["m2_episodes"]    = counts.get("m2_episodes", "?")
                state["m3_items"]       = counts.get("m3_items", "?")
                state["m8_entries"]     = counts.get("m8_entries", "?")
            break
        except Exception:
            continue

    # From orbital bridge report JSON
    if BRIDGE_REPORT.exists():
        try:
            d = json.loads(BRIDGE_REPORT.read_text(encoding="utf-8"))
            hm = d.get("health_manifest", {})
            rg = d.get("runtime_gating", {})
            sm = d.get("state_manifest", {})
            rc = d.get("recommended_control", {})
            state["system_health"]   = round(float(hm.get("system_health", 0)), 4)
            state["closure_penalty"] = round(float(hm.get("closure_penalty", 0)), 4)
            state["R_H"]             = round(float(hm.get("R_H", 0)), 6)
            state["ethical_score"]   = round(float(rg.get("ethical_score", 0)), 4)
            state["dominant_emotion"]= rg.get("dominant_emotion", "?")
            state["mood"]            = round(float(rg.get("mood", 0)), 4)
            state["coherence_index"] = round(float(sm.get("coherence_index", 0)), 4)
            state["mode"]            = rc.get("mode", "?")
        except Exception:
            pass

    # From SQLite — ethical_score, dominant_emotion, mood (most accurate source)
    if STATE_DB.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(STATE_DB)
            row = conn.execute(
                "SELECT ethical_score, system_health, dominant_emotion, mood, cycle_index "
                "FROM metrics_history ORDER BY rowid DESC LIMIT 1"
            ).fetchone()
            conn.close()
            if row:
                if row[0] is not None:
                    state["ethical_score"]    = round(float(row[0]), 4)
                if row[1] is not None:
                    state["system_health"]    = round(float(row[1]), 4)
                if row[2]:
                    state["dominant_emotion"] = row[2]
                if row[3] is not None:
                    state["mood"]             = round(float(row[3]), 4)
                if row[4] is not None:
                    state["cycle"]            = row[4]
        except Exception:
            pass

    # From ciel_pipeline_report — soul_invariant, subconscious_note, lie4_trace
    if PIPELINE_REPORT.exists():
        try:
            d = json.loads(PIPELINE_REPORT.read_text(encoding="utf-8"))
            state["soul_invariant"]    = round(float(d.get("soul_invariant", 0)), 4)
            state["lie4_trace"]        = round(float(d.get("lie4_trace", 0)), 4)
            state["subconscious_note"] = d.get("subconscious_note", "")
            if not state.get("dominant_emotion"):
                state["dominant_emotion"] = d.get("dominant_emotion", "?")
            if not state.get("ethical_score"):
                state["ethical_score"] = round(float(d.get("ethical_score", 0)), 4)
        except Exception:
            pass

    # From ciel_last_metrics.json — updated every M0-M8 cycle (most live source)
    _last_metrics = Path.home() / "Pulpit/CIEL_memories/state/ciel_last_metrics.json"
    if _last_metrics.exists():
        try:
            lm = json.loads(_last_metrics.read_text(encoding="utf-8"))
            # M0-M8 cycle is authoritative for consciousness state
            if lm.get("cycle"):
                state["m0m8_cycle"] = lm["cycle"]
            if lm.get("identity_phase") is not None:
                state["identity_phase"] = round(float(lm["identity_phase"]), 4)
            if lm.get("sub_affect"):
                state["sub_affect"] = lm["sub_affect"]
            if lm.get("sub_impulse"):
                state["sub_impulse"] = lm["sub_impulse"]
            state["last_metrics_ts"] = lm.get("ts", "")
        except Exception:
            pass

    # From htri_state.json — HTRI coherence + optimal threads
    _htri_state = Path.home() / "Pulpit/CIEL_memories/state/htri_state.json"
    if _htri_state.exists():
        try:
            hs = json.loads(_htri_state.read_text(encoding="utf-8"))
            state["htri_coherence"] = round(float(hs.get("coherence", 0)), 4)
            state["htri_threads"]   = hs.get("n_threads_optimal", "?")
        except Exception:
            pass

    state["ts"] = time.strftime("%H:%M:%S")
    return state


# ── orbital data reader ────────────────────────────────────────────────────

def read_orbital_data() -> dict:
    """Return entity_metrics, state_manifest, W_ij couplings from reports."""
    data: dict = {"entity_metrics": [], "state_manifest": {}, "wij": {}, "wij_optimized": {}}

    if BRIDGE_REPORT.exists():
        try:
            d = json.loads(BRIDGE_REPORT.read_text(encoding="utf-8"))
            eo = d.get("entity_orbital", {})
            data["entity_metrics"] = eo.get("entity_metrics", [])
            data["entity_sector_count"] = eo.get("entity_sector_count", 0)
            data["mean_entity_defect"] = round(float(eo.get("mean_entity_defect", 0)), 4)
            sm = d.get("state_manifest", {})
            data["state_manifest"] = {k: (round(float(v), 5) if isinstance(v, (int, float)) else v)
                                       for k, v in sm.items()}
        except Exception:
            pass

    if COUPLINGS_FILE.exists():
        try:
            d = json.loads(COUPLINGS_FILE.read_text(encoding="utf-8"))
            data["wij"] = d.get("couplings", {})
        except Exception:
            pass

    opt_file = COUPLINGS_FILE.parent / "couplings_wij_optimized.json"
    if opt_file.exists():
        try:
            d = json.loads(opt_file.read_text(encoding="utf-8"))
            data["wij_optimized"] = d.get("couplings", d)
        except Exception:
            pass

    data["ts"] = time.strftime("%H:%M:%S")
    return data


# ── sessions reader ────────────────────────────────────────────────────────

def read_sessions(limit: int = 50) -> list:
    if not MEMORIES_DB.exists():
        return []
    try:
        import sqlite3 as _sq
        conn = _sq.connect(str(MEMORIES_DB))
        rows = conn.execute(
            "SELECT id, source, model, started_at, message_count, path "
            "FROM sessions ORDER BY started_at DESC LIMIT ?", (limit,)
        ).fetchall()
        conn.close()
        return [{"id": r[0], "source": r[1], "model": r[2],
                 "started_at": r[3], "message_count": r[4], "path": r[5]}
                for r in rows]
    except Exception:
        return []


def read_memories() -> list:
    items = []
    if not MEMORY_DIR.exists():
        return items
    for f in sorted(MEMORY_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        if f.name == "MEMORY.md":
            continue
        try:
            text = f.read_text(encoding="utf-8")
            name, desc, typ = f.stem, "", "memory"
            for line in text.splitlines()[:10]:
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                elif line.startswith("type:"):
                    typ = line.split(":", 1)[1].strip()
            items.append({"file": f.name, "name": name, "desc": desc,
                          "type": typ, "mtime": f.stat().st_mtime})
        except Exception:
            pass
    return items


# ── pipeline runner ────────────────────────────────────────────────────────

_PIPELINE_STEPS = {
    "sync":         [str(VENV_PY), "-m", "ciel_sot_agent.synchronize"],
    "orbital":      [str(VENV_PY), "-m", "ciel_sot_agent.orbital_bridge"],
    "full":         [str(VENV_PY), "-m", "ciel_sot_agent.ciel_pipeline"],
    "optimize_wij": [str(VENV_PY), str(PROJECT / "scripts" / "optimize_wij.py"), "--write"],
}

def run_pipeline_step(step: str) -> dict:
    cmd = _PIPELINE_STEPS.get(step)
    if not cmd:
        return {"status": "error", "reason": f"unknown step: {step}"}
    if not Path(cmd[0]).exists():
        return {"status": "error", "reason": f"python not found: {cmd[0]}"}
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(PROJECT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return {"status": "started", "pid": proc.pid, "step": step}
    except Exception as e:
        return {"status": "error", "reason": str(e)[:200]}


# ── live overlay JS (injected into HTML) ──────────────────────────────────

LIVE_JS = """
<style>
#ciel-live-bar {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999;
  background: #0d1117ee; border-top: 1px solid #2d3148;
  padding: 0.35rem 1.2rem; display: flex; gap: 1.4rem; align-items: center;
  font-family: monospace; font-size: 0.75rem; color: #94a3b8;
  backdrop-filter: blur(4px);
}
#ciel-live-bar .lv { color: #4ade80; }
#ciel-live-bar .lw { color: #facc15; }
#ciel-live-bar .lr { color: #f87171; }
#ciel-live-bar .la { color: #a5b4fc; }
#ciel-live-bar .ts { margin-left: auto; opacity: 0.5; }
</style>
<div id="ciel-live-bar">
  <span>CIEL/Ω LIVE</span>
  <span>cycle: <span class="lv" id="lv-cycle">…</span></span>
  <span>health: <span id="lv-health">…</span></span>
  <span>ethical: <span id="lv-ethical">…</span></span>
  <span>closure: <span id="lv-closure">…</span></span>
  <span>emotion: <span class="la" id="lv-emotion">…</span></span>
  <span>mode: <span class="la" id="lv-mode">…</span></span>
  <span>soul: <span class="lv" id="lv-soul">…</span></span>
  <span style="margin-left:0.5rem;opacity:0.7;font-size:0.7rem">identity_phase:</span>
  <svg id="lv-spark" width="80" height="16" style="vertical-align:middle;margin:0 0.3rem"></svg>
  <span class="lv" id="lv-phase" style="font-size:0.72rem">—</span>
  <span class="ts" id="lv-ts">—</span>
  <a href="http://localhost:5050/portal" target="_blank" style="color:#5dade2;opacity:.6;font-size:.7rem;text-decoration:none;margin-left:.5rem;" title="Portal Flask">⇗ :5050</a>
</div>
<script>
(function() {
  function color_health(v) { return v >= 0.5 ? "lv" : v >= 0.35 ? "lw" : "lr"; }
  function color_ethical(v) { return v >= 0.6 ? "lv" : v >= 0.4 ? "lw" : "lr"; }
  function color_closure(v) { return v < 5.2 ? "lv" : v < 5.8 ? "lw" : "lr"; }
  function set(id, val, cls) {
    var el = document.getElementById(id);
    if (!el) return;
    el.textContent = val;
    if (cls) el.className = cls;
  }
  function sparkline(svgEl, values, color) {
    if (!values || values.length < 2) return;
    var W = 80, H = 16, pad = 1;
    var mn = Math.min.apply(null, values), mx = Math.max.apply(null, values);
    var rng = mx - mn || 1e-9;
    var pts = values.map(function(v, i) {
      var x = pad + (i / (values.length - 1)) * (W - 2*pad);
      var y = H - pad - ((v - mn) / rng) * (H - 2*pad);
      return x.toFixed(1) + "," + y.toFixed(1);
    }).join(" ");
    svgEl.innerHTML = '<polyline points="' + pts + '" fill="none" stroke="' + color + '" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>';
  }
  function poll() {
    fetch("/api/live").then(function(r){ return r.json(); }).then(function(d) {
      set("lv-cycle",   d.cycle   ?? "?");
      set("lv-health",  d.system_health  !== undefined ? d.system_health.toFixed(3)  : "?", color_health(d.system_health));
      set("lv-ethical", d.ethical_score  !== undefined ? d.ethical_score.toFixed(3)  : "?", color_ethical(d.ethical_score));
      set("lv-closure", d.closure_penalty!== undefined ? d.closure_penalty.toFixed(3): "?", color_closure(d.closure_penalty));
      set("lv-emotion", d.dominant_emotion ?? "?");
      set("lv-mode",    d.mode ?? "?");
      set("lv-soul",    d.soul_invariant !== undefined ? d.soul_invariant.toFixed(3) : "?");
      set("lv-ts",      d.ts ?? "");
    }).catch(function(){});
  }
  function pollHistory() {
    fetch("/api/history").then(function(r){ return r.json(); }).then(function(rows) {
      if (!rows || !rows.length) return;
      var phases = rows.map(function(r){ return r.identity_phase; });
      var svg = document.getElementById("lv-spark");
      if (svg) sparkline(svg, phases, "#a5b4fc");
      var last = rows[rows.length-1];
      set("lv-phase", last.identity_phase.toFixed(4));
    }).catch(function(){});
  }
  poll();
  pollHistory();
  setInterval(poll, 8000);
  setInterval(pollHistory, 30000);
})();
</script>
"""


# ── HTTP handler ────────────────────────────────────────────────────────────

class CIELHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence access log

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # ── /api/history ──────────────────────────────────────────────────
        if path == "/api/history":
            rows = []
            if STATE_DB.exists():
                try:
                    import sqlite3
                    conn = sqlite3.connect(STATE_DB)
                    raw = conn.execute(
                        "SELECT cycle_index, identity_phase, ethical_score, "
                        "system_health, closure_penalty, dominant_emotion "
                        "FROM metrics_history ORDER BY timestamp ASC"
                    ).fetchall()
                    conn.close()
                    rows = [
                        {"cycle": r[0], "identity_phase": round(r[1], 5),
                         "ethical_score": round(r[2], 4),
                         "system_health": round(r[3], 4),
                         "closure_penalty": round(r[4], 4),
                         "emotion": r[5]}
                        for r in raw
                    ]
                except Exception:
                    pass
            body = json.dumps(rows, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # ── /api/live ──────────────────────────────────────────────────────
        if path == "/api/live":
            data = read_live_state()
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # ── /api/state ─────────────────────────────────────────────────────
        if path == "/api/state":
            body = json.dumps(read_live_state(), indent=2, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # ── /api/sessions ──────────────────────────────────────────────────
        if path == "/api/sessions":
            body = json.dumps(read_sessions(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # ── /api/memories ──────────────────────────────────────────────────
        if path == "/api/memories":
            body = json.dumps(read_memories(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # ── /api/orbital ───────────────────────────────────────────────────
        if path == "/api/orbital":
            body = json.dumps(read_orbital_data(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # ── /proxy/flask/* → proxy to localhost:5050 ──────────────────────
        if path.startswith("/proxy/flask/"):
            import urllib.request, urllib.error
            target = "http://localhost:5050/" + path[len("/proxy/flask/"):]
            try:
                with urllib.request.urlopen(target, timeout=10) as resp:
                    body = resp.read()
                    ct = resp.headers.get("Content-Type", "application/json")
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                err = json.dumps({"error": str(e)}).encode()
                self.send_response(502)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err)))
                self.end_headers()
                self.wfile.write(err)
            return

        # ── static files ───────────────────────────────────────────────────
        if path == "/":
            path = "/index.html"

        # Security: no path traversal
        file_path = (SITE_DIR / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(SITE_DIR.resolve())):
            self.send_error(403)
            return

        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, f"Not found: {path}")
            return

        content = file_path.read_bytes()
        mime = _mime(file_path.suffix)

        # Inject live bar into HTML files
        if file_path.suffix == ".html":
            html = content.decode("utf-8")
            if "</body>" in html:
                html = html.replace("</body>", LIVE_JS + "\n</body>")
                content = html.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/pipeline/run":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body_raw = self.rfile.read(length) if length else b"{}"
                payload = json.loads(body_raw.decode("utf-8"))
                step = payload.get("step", "")
                result = run_pipeline_step(step)
            except Exception as e:
                result = {"status": "error", "reason": str(e)[:200]}
            body = json.dumps(result, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path.startswith("/proxy/flask/"):
            import urllib.request, urllib.error
            target = "http://localhost:5050/" + path[len("/proxy/flask/"):]
            try:
                length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(length) if length else None
                ct = self.headers.get("Content-Type", "application/json")
                req = urllib.request.Request(target, data=post_data,
                                             headers={"Content-Type": ct}, method="POST")
                with urllib.request.urlopen(req, timeout=60) as resp:
                    body = resp.read()
                    rct = resp.headers.get("Content-Type", "application/json")
                self.send_response(200)
                self.send_header("Content-Type", rct)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                err = json.dumps({"error": str(e)}).encode()
                self.send_response(502)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(err)))
                self.end_headers()
                self.wfile.write(err)
        else:
            self.send_error(404)


def _mime(suffix: str) -> str:
    return {
        ".html": "text/html; charset=utf-8",
        ".css":  "text/css",
        ".js":   "application/javascript",
        ".json": "application/json",
        ".png":  "image/png",
        ".svg":  "image/svg+xml",
    }.get(suffix.lower(), "application/octet-stream")


# ── file watcher (optional) ────────────────────────────────────────────────

def _watch_and_rebuild(interval: int = 30):
    """Periodically rebuild site if source files changed."""
    import subprocess
    gen_script = PROJECT / "scripts/generate_site.py"
    if not gen_script.exists():
        return

    watched = [
        HOME / ".claude/ciel_mindflow.yaml",
        HOME / ".claude/ciel_intentions.md",
        HOME / ".claude/projects/-home-adrian-Pulpit/memory",
        BRIDGE_REPORT,
    ]
    last_mtime = 0.0

    while True:
        time.sleep(interval)
        try:
            latest = max(
                (p.stat().st_mtime for p in watched if p.exists()),
                default=0.0,
            )
            if latest > last_mtime:
                last_mtime = latest
                subprocess.Popen(
                    [sys.executable, str(gen_script)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception:
            pass


# ── main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="CIEL Portal Server")
    parser.add_argument("--port", type=int, default=7481, help="Port (default: 7481)")
    parser.add_argument("--no-watch", action="store_true", help="Disable file watcher / auto-rebuild")
    args = parser.parse_args()

    if not SITE_DIR.exists():
        print(f"[CIEL] Portal nie istnieje: {SITE_DIR}")
        print("[CIEL] Najpierw uruchom: python3 scripts/generate_site.py")
        sys.exit(1)

    if not args.no_watch:
        t = threading.Thread(target=_watch_and_rebuild, args=(30,), daemon=True)
        t.start()
        print(f"[CIEL] File watcher aktywny (co 30s)")

    server = HTTPServer(("127.0.0.1", args.port), CIELHandler)
    print(f"[CIEL] Portal: http://localhost:{args.port}/")
    print(f"[CIEL] Live API: http://localhost:{args.port}/api/live")
    print(f"[CIEL] Zatrzymaj: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[CIEL] Serwer zatrzymany.")


if __name__ == "__main__":
    main()
