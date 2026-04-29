#!/usr/bin/env python3
"""CIEL System Report — generuje HTML snapshot na ~/Pulpit i otwiera w przeglądarce."""
import json
import pickle
import sqlite3
import subprocess
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path.home()
MEMORIES = HOME / "Pulpit/CIEL_memories"
INTEGRATION = ROOT / "integration"

# ── helpers ─────────────────────────────────────────────────────────────────

def _jload(p: Path) -> dict:
    if p.exists():
        try:
            return json.loads(p.read_text("utf-8"))
        except Exception:
            pass
    return {}


def _last_metrics() -> dict:
    return _jload(MEMORIES / "state/ciel_last_metrics.json")


def _bridge() -> dict:
    con_path = Path(__file__).resolve().parent.parent / "src/ciel_sot_agent"
    # state_db lives in src/ciel_sot_agent
    db_path = MEMORIES / "state/ciel_state.db"
    # try standard path
    for candidate in [
        HOME / "Pulpit/CIEL_memories/state/ciel_state.db",
        ROOT / "ciel_state.db",
    ]:
        if candidate.exists():
            db_path = candidate
            break
    try:
        sys.path.insert(0, str(ROOT / "src"))
        import ciel_sot_agent.state_db as sdb
        con = sdb.get_db()
        cur = con.cursor()
        cur.execute("SELECT payload FROM json_reports WHERE report_type='orbital_bridge'")
        row = cur.fetchone()
        if row:
            return json.loads(row["payload"])
    except Exception:
        pass
    return {}


def _pipeline() -> dict:
    return _jload(INTEGRATION / "reports/ciel_pipeline_report.json")


def _tensions() -> list:
    data = _jload(INTEGRATION / "reports/initial_sync_report.json")
    tensions = data.get("pairwise_tensions", [])
    seen: dict[str, float] = {}
    for t in tensions:
        src, tgt = t.get("source", ""), t.get("target", "")
        key = f"{src}↔{tgt}"
        if f"{tgt}↔{src}" not in seen:
            seen[key] = round(float(t.get("tension", 0.0)), 5)
    return sorted(seen.items(), key=lambda x: x[1], reverse=True)[:8]


def _memory_stats() -> dict:
    pkl = MEMORIES / "state/ciel_orch_state.pkl"
    if not pkl.exists():
        return {}
    omega_pkg = str(ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega")
    omega_src = str(ROOT / "src/CIEL_OMEGA_COMPLETE_SYSTEM")
    script = (
        f"import sys, pickle, json\n"
        f"sys.path.insert(0, {repr(omega_pkg)})\n"
        f"sys.path.insert(0, {repr(omega_src)})\n"
        f"from pathlib import Path\n"
        f"_sp=Path.home()/'Pulpit/CIEL_memories/state/ciel_orch_state.pkl'\n"
        f"with open(_sp,'rb') as f: o=pickle.load(f)\n"
        f"print(json.dumps({{"
        f"'m2_count':len(o.m2.episodes),"
        f"'m3_count':len(o.m3.items),"
        f"'identity_phase':round(float(o.identity_field.phase),6),"
        f"'cycle':getattr(o,'cycle_index',0)"
        f"}}))"
    )
    try:
        r = subprocess.run([sys.executable, "-c", script],
                           capture_output=True, text=True, timeout=4)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout.strip())
    except Exception:
        pass
    return {}


def _sub_feed(n=10) -> list:
    log = MEMORIES / "logs/ciel_sub_log.jsonl"
    entries = []
    if log.exists():
        lines = [l for l in log.read_text("utf-8").splitlines() if l.strip()]
        for line in lines[-n:]:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return list(reversed(entries))


def _metrics_history(limit=30) -> list:
    try:
        sys.path.insert(0, str(ROOT / "src"))
        import ciel_sot_agent.state_db as sdb
        return sdb.load_metrics_history(limit=limit)
    except Exception:
        return []


def _key_files() -> list:
    """Orbital key files with their roles."""
    candidates = [
        (ROOT / "src/ciel_sot_agent/synchronize.py",         "M0 Sync — closure_defect, phase_gap"),
        (ROOT / "src/ciel_sot_agent/orbital_bridge.py",       "M1-4 Orbital Bridge — R_H, coherence, health"),
        (ROOT / "src/ciel_sot_agent/ciel_pipeline.py",        "M4 CIEL/Ω — intencja→emocje→etyka→pamięć"),
        (ROOT / "src/ciel_sot_agent/state_db.py",             "State DB — metrics_history, json_reports"),
        (ROOT / "src/ciel_sot_agent/gui/routes.py",           "GUI routes — 40+ endpoints, SSE"),
        (ROOT / "integration/couplings.json",                  "Pairwise coupling tensors"),
        (ROOT / "integration/gh_coupling_state.json",          "GitHub coupling state per repo"),
        (ROOT / "integration/repository_registry.json",        "All registered repos"),
        (MEMORIES / "state/ciel_last_metrics.json",            "Live metrics snapshot (updated per cycle)"),
        (MEMORIES / "state/ciel_orch_state.pkl",               "Orchestrator state — M2/M3/identity_field"),
    ]
    result = []
    for path, role in candidates:
        size = ""
        if path.exists():
            b = path.stat().st_size
            size = f"{b//1024}KB" if b >= 1024 else f"{b}B"
        result.append({"path": str(path), "role": role, "exists": path.exists(), "size": size})
    return result


# ── ASCII sparkline ──────────────────────────────────────────────────────────

def _sparkline(values: list[float], width=30) -> str:
    blocks = " ▁▂▃▄▅▆▇█"
    if not values:
        return "—"
    lo, hi = min(values), max(values)
    rng = hi - lo or 1
    result = []
    for v in values[-width:]:
        idx = int((v - lo) / rng * (len(blocks) - 1))
        result.append(blocks[idx])
    return "".join(result)


# ── mode helpers ─────────────────────────────────────────────────────────────

def _mode(closure: float) -> tuple[str, str]:
    if closure < 5.2:
        return "deep", "#00e676"
    elif closure < 5.8:
        return "standard", "#ffd700"
    return "safe", "#ff6b6b"


def _health_color(v: float) -> str:
    if v >= 0.6:
        return "#00e676"
    elif v >= 0.4:
        return "#ffd700"
    return "#ff6b6b"


def _val_color(v: float, ok_thresh: float = 0.7, warn_thresh: float = 0.4) -> str:
    if v >= ok_thresh:
        return "#00e676"
    elif v >= warn_thresh:
        return "#ffd700"
    return "#ff6b6b"


# ── HTML generation ──────────────────────────────────────────────────────────

def build_html() -> str:
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d %H:%M:%S UTC")

    lm = _last_metrics()
    br = _bridge()
    pl = _pipeline()
    mem = _memory_stats()
    tensions = _tensions()
    sub = _sub_feed(10)
    hist = _metrics_history(40)
    files = _key_files()

    hm = br.get("health_manifest", {})
    sm = br.get("state_manifest", {})
    bm = br.get("bridge_metrics", {})
    rc = br.get("recommended_control", {})

    closure = lm.get("closure_penalty") or hm.get("closure_penalty", 0.0)
    health  = lm.get("system_health")  or hm.get("system_health", 0.0)
    coherence = lm.get("mean_coherence") or sm.get("coherence_index", 0.0)
    ethical = lm.get("ethical_score") or pl.get("ethical_score") or sm.get("ethical_score", 0.0)
    soul    = lm.get("soul_invariant") or pl.get("soul_invariant") or sm.get("soul_invariant", 0.0)
    emotion = lm.get("dominant_emotion") or pl.get("dominant_emotion") or "—"
    cycle   = lm.get("cycle_index") or mem.get("cycle", 0)
    identity_phase = mem.get("identity_phase") or lm.get("identity_phase", 0.0)
    m2 = mem.get("m2_count", "—")
    m3 = mem.get("m3_count", "—")

    mode_str, mode_color = _mode(float(closure))
    h_color  = _health_color(float(health))
    co_color = _val_color(float(coherence), 0.767, 0.5)
    et_color = _val_color(float(ethical), 0.7, 0.4)
    so_color = _val_color(float(soul), 0.95, 0.7)
    cl_color = "#00e676" if float(closure) <= 5.2 else ("#ffd700" if float(closure) <= 5.8 else "#ff6b6b")

    # Sparkline from history
    health_hist  = [dict(r).get("system_health", 0.0) for r in hist]
    coh_hist     = [dict(r).get("coherence_index", 0.0) for r in hist]
    spark_health = _sparkline(health_hist)
    spark_coh    = _sparkline(coh_hist)

    # Pipeline stage values
    R_H         = bm.get("orbital_R_H", 0.0)
    lambda_glob = bm.get("topological_charge_global", 0.0)
    closure_def = bm.get("integration_closure_defect_proxy", 0.0)
    berry_rad   = sm.get("berry_holonomy_rad", pl.get("berry_holonomy_rad", 0.0))
    writeback   = rc.get("writeback_gate", False)

    def fmt(v, digits=4):
        try:
            return f"{float(v):.{digits}f}"
        except Exception:
            return str(v)

    def stage_class(healthy: bool) -> str:
        return "stage-ok" if healthy else "stage-warn"

    # tension rows
    tension_rows = ""
    for pair, val in tensions:
        alert = val > 0.02
        color = "#ff6b6b" if alert else ("#ffd700" if val > 0.01 else "#00e676")
        tension_rows += f'<tr><td class="t-pair">{pair}</td><td style="color:{color};font-weight:bold">{val:.5f}</td><td>{"⚠" if alert else "✓"}</td></tr>'
    if not tension_rows:
        tension_rows = '<tr><td colspan="3" style="color:#555;text-align:center">— no tension data —</td></tr>'

    # sub feed rows
    sub_rows = ""
    affect_colors = {
        "love": "#ff69b4", "joy": "#ffd700", "calm": "#21d4fd",
        "fear": "#ff9f43", "anger": "#ff6b6b", "sadness": "#9b8bba",
        "curiosity": "#00e676", "awe": "#b088f9",
    }
    for entry in sub[:8]:
        affect = entry.get("affect", entry.get("dominant_emotion", ""))
        impulse = entry.get("impulse", entry.get("text", entry.get("subconscious_note", "")))
        ts_raw = entry.get("ts", entry.get("timestamp", ""))
        ts_fmt = ts_raw[:19].replace("T", " ") if ts_raw else "—"
        a_color = affect_colors.get(str(affect).lower(), "#aaa")
        sub_rows += (
            f'<div class="sub-entry">'
            f'<span class="sub-ts">{ts_fmt}</span>'
            f'<span class="sub-affect" style="background:{a_color}22;color:{a_color};border-color:{a_color}44">{affect or "—"}</span>'
            f'<span class="sub-impulse">{str(impulse)[:120]}</span>'
            f'</div>'
        )
    if not sub_rows:
        sub_rows = '<div class="sub-entry" style="color:#555">— no subconscious feed data —</div>'

    # file rows
    file_rows = ""
    for f in files:
        exist_icon = "✓" if f["exists"] else "✗"
        exist_color = "#00e676" if f["exists"] else "#ff6b6b"
        short = f["path"].replace(str(HOME), "~")
        file_rows += (
            f'<tr>'
            f'<td style="color:{exist_color};width:1.5rem;text-align:center">{exist_icon}</td>'
            f'<td class="file-path">{short}</td>'
            f'<td class="file-role">{f["role"]}</td>'
            f'<td class="file-size">{f["size"]}</td>'
            f'</tr>'
        )

    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<title>CIEL System Report — {ts}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');
  :root {{
    --bg:      #04040c;
    --bg2:     #0a0a1e;
    --bg3:     #0d1525;
    --border:  #1a2540;
    --text:    #c8d8f0;
    --dim:     #4a5a7a;
    --green:   #00e676;
    --gold:    #ffd700;
    --red:     #ff6b6b;
    --cyan:    #21d4fd;
    --purple:  #b088f9;
    --orange:  #ff9f43;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ background: var(--bg); color: var(--text); font-family: 'JetBrains Mono', monospace; font-size: 13px; }}
  body {{ padding: 2rem; max-width: 1200px; margin: 0 auto; }}

  /* header */
  .report-header {{ border-bottom: 1px solid var(--border); padding-bottom: 1rem; margin-bottom: 2rem; }}
  .report-header h1 {{ font-size: 1.4rem; letter-spacing: 0.1em; color: var(--cyan); font-weight: 700; }}
  .report-header .meta {{ color: var(--dim); margin-top: .4rem; font-size: .8rem; }}

  /* section */
  section {{ margin-bottom: 2.5rem; }}
  h2 {{ font-size: .85rem; letter-spacing: .15em; text-transform: uppercase; color: var(--dim);
        border-bottom: 1px solid var(--border); padding-bottom: .5rem; margin-bottom: 1rem; }}

  /* exec summary grid */
  .exec-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: .75rem; }}
  .exec-card {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 4px;
                padding: .75rem 1rem; }}
  .exec-card .ec-label {{ font-size: .7rem; color: var(--dim); letter-spacing: .1em; text-transform: uppercase; margin-bottom: .25rem; }}
  .exec-card .ec-val {{ font-size: 1.4rem; font-weight: 700; }}
  .exec-card .ec-sub {{ font-size: .7rem; color: var(--dim); margin-top: .25rem; }}

  /* pipeline */
  .pipeline {{ display: flex; align-items: stretch; gap: 0; background: var(--bg2);
               border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }}
  .stage {{ flex: 1; padding: .75rem 1rem; border-right: 1px solid var(--border); min-width: 120px; }}
  .stage:last-child {{ border-right: none; }}
  .stage-ok   {{ border-top: 3px solid var(--green);  }}
  .stage-warn {{ border-top: 3px solid var(--gold);   }}
  .stage-crit {{ border-top: 3px solid var(--red);    }}
  .stage-name {{ font-weight: 700; font-size: .8rem; letter-spacing: .05em; margin-bottom: .25rem; }}
  .stage-mod  {{ font-size: .65rem; color: var(--dim); margin-bottom: .5rem; }}
  .stage-metric {{ font-size: .72rem; margin: .15rem 0; }}
  .stage-metric span {{ color: var(--dim); }}
  .arrow {{ display: flex; align-items: center; color: var(--dim); font-size: 1rem; padding: 0 .25rem; }}

  /* sparkline */
  .sparkline-row {{ display: flex; align-items: center; gap: 1rem; background: var(--bg2);
                    border: 1px solid var(--border); border-radius: 4px; padding: .75rem 1rem; margin-bottom: .75rem; }}
  .sp-label {{ width: 10rem; color: var(--dim); font-size: .75rem; }}
  .sp-line {{ font-family: monospace; font-size: .9rem; letter-spacing: .05em; }}

  /* tables */
  table {{ width: 100%; border-collapse: collapse; background: var(--bg2); border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }}
  th {{ background: var(--bg3); color: var(--dim); font-size: .7rem; letter-spacing: .1em; text-transform: uppercase;
        padding: .5rem .75rem; text-align: left; border-bottom: 1px solid var(--border); }}
  td {{ padding: .45rem .75rem; border-bottom: 1px solid var(--border)22; font-size: .78rem; }}
  tr:last-child td {{ border-bottom: none; }}
  .t-pair {{ color: var(--cyan); }}
  .file-path {{ color: var(--cyan); font-size: .72rem; word-break: break-all; }}
  .file-role {{ color: var(--dim); font-size: .72rem; }}
  .file-size {{ color: var(--purple); font-size: .72rem; }}

  /* sub feed */
  .sub-entry {{ background: var(--bg2); border: 1px solid var(--border); border-radius: 4px;
                padding: .5rem .75rem; margin-bottom: .5rem; display: flex; align-items: flex-start; gap: .75rem; flex-wrap: wrap; }}
  .sub-ts     {{ color: var(--dim); font-size: .7rem; min-width: 11rem; }}
  .sub-affect {{ font-size: .7rem; padding: .15rem .5rem; border-radius: 3px; border: 1px solid; font-weight: 500; }}
  .sub-impulse {{ flex: 1; font-size: .78rem; color: var(--text); }}

  /* mode badge */
  .mode-badge {{ display: inline-block; padding: .2rem .75rem; border-radius: 3px; font-weight: 700;
                 font-size: .8rem; letter-spacing: .1em; text-transform: uppercase; }}

  /* footer */
  footer {{ color: var(--dim); font-size: .7rem; border-top: 1px solid var(--border);
            padding-top: 1rem; margin-top: 3rem; }}
</style>
</head>
<body>

<div class="report-header">
  <h1>◎ CIEL SYSTEM REPORT</h1>
  <div class="meta">Generated: {ts} &nbsp;|&nbsp; Cycle: {cycle} &nbsp;|&nbsp; Mode: <span class="mode-badge" style="background:{mode_color}22;color:{mode_color};border:1px solid {mode_color}44">{mode_str.upper()}</span></div>
</div>

<!-- EXECUTIVE SUMMARY -->
<section>
  <h2>Executive Summary</h2>
  <div class="exec-grid">
    <div class="exec-card">
      <div class="ec-label">System Health</div>
      <div class="ec-val" style="color:{h_color}">{fmt(health, 3)}</div>
      <div class="ec-sub">target ≥ 0.5</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Coherence</div>
      <div class="ec-val" style="color:{co_color}">{fmt(coherence, 3)}</div>
      <div class="ec-sub">target ≥ 0.767</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Closure Penalty</div>
      <div class="ec-val" style="color:{cl_color}">{fmt(closure, 3)}</div>
      <div class="ec-sub">deep &lt;5.2, safe &gt;5.8</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Ethical Score</div>
      <div class="ec-val" style="color:{et_color}">{fmt(ethical, 3)}</div>
      <div class="ec-sub">target ≥ 0.7</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Soul Invariant</div>
      <div class="ec-val" style="color:{so_color}">{fmt(soul, 3)}</div>
      <div class="ec-sub">target ≥ 0.95</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Dominant Emotion</div>
      <div class="ec-val" style="color:#ff69b4;font-size:1rem">{emotion}</div>
      <div class="ec-sub">affective key</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">M2 Episodes</div>
      <div class="ec-val" style="color:var(--cyan)">{m2}</div>
      <div class="ec-sub">episodic memory</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">M3 Items</div>
      <div class="ec-val" style="color:var(--purple)">{m3}</div>
      <div class="ec-sub">consolidation</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Identity Phase</div>
      <div class="ec-val" style="color:var(--gold);font-size:1rem">{fmt(identity_phase, 4)}</div>
      <div class="ec-sub">φ M0, 0 = rooted</div>
    </div>
    <div class="exec-card">
      <div class="ec-label">Writeback Gate</div>
      <div class="ec-val" style="color:{'var(--green)' if writeback else 'var(--red)'}">{' OPEN' if writeback else 'CLOSED'}</div>
      <div class="ec-sub">memory write enable</div>
    </div>
  </div>
</section>

<!-- PIPELINE FLOW -->
<section>
  <h2>Pipeline Flow — M0 → M1-4 → M4 → M8</h2>
  <div class="pipeline">
    <div class="stage {stage_class(float(closure_def) < 0.01)}">
      <div class="stage-name">M0 · Sync</div>
      <div class="stage-mod">synchronize.py</div>
      <div class="stage-metric"><span>closure_defect:</span> {fmt(closure_def, 5)}</div>
      <div class="stage-metric"><span>phase_gap:</span> {fmt(lm.get("identity_phase", 0.0), 4)}</div>
    </div>
    <div class="stage {stage_class(float(coherence) >= 0.767)}">
      <div class="stage-name">M1-3 · Orbital</div>
      <div class="stage-mod">orbital_bridge.py</div>
      <div class="stage-metric"><span>R_H:</span> {fmt(R_H, 6)}</div>
      <div class="stage-metric"><span>Λ_glob:</span> {fmt(lambda_glob, 4)}</div>
      <div class="stage-metric"><span>coherence:</span> {fmt(coherence, 4)}</div>
      <div class="stage-metric"><span>berry_φ:</span> {fmt(berry_rad, 4)}</div>
    </div>
    <div class="stage {stage_class(float(health) >= 0.5)}">
      <div class="stage-name">M4 · CIEL/Ω</div>
      <div class="stage-mod">ciel_pipeline.py</div>
      <div class="stage-metric"><span>health:</span> {fmt(health, 4)}</div>
      <div class="stage-metric"><span>ethical:</span> {fmt(ethical, 4)}</div>
      <div class="stage-metric"><span>emotion:</span> {emotion}</div>
      <div class="stage-metric"><span>soul_inv:</span> {fmt(soul, 4)}</div>
    </div>
    <div class="stage {stage_class(bool(m2) and str(m2) != '—')}">
      <div class="stage-name">M8 · Memory</div>
      <div class="stage-mod">holonomic_memory</div>
      <div class="stage-metric"><span>M2 episodes:</span> {m2}</div>
      <div class="stage-metric"><span>M3 items:</span> {m3}</div>
      <div class="stage-metric"><span>cycle:</span> {cycle}</div>
      <div class="stage-metric"><span>writeback:</span> {'✓' if writeback else '✗'}</div>
    </div>
  </div>
</section>

<!-- HEALTH HISTORY SPARKLINES -->
<section>
  <h2>Health History (last {len(health_hist)} cycles)</h2>
  <div class="sparkline-row">
    <div class="sp-label">system_health</div>
    <div class="sp-line" style="color:var(--green)">{spark_health}</div>
    <div style="color:var(--dim);font-size:.7rem;margin-left:.5rem">min={min(health_hist):.3f} max={max(health_hist):.3f}" if health_hist else "—</div>
  </div>
  <div class="sparkline-row">
    <div class="sp-label">coherence_index</div>
    <div class="sp-line" style="color:var(--cyan)">{spark_coh}</div>
    <div style="color:var(--dim);font-size:.7rem;margin-left:.5rem">min={min(coh_hist):.3f} max={max(coh_hist):.3f}" if coh_hist else "—</div>
  </div>
</section>

<!-- ACTIVE TENSIONS -->
<section>
  <h2>Repository Tensions (top 8)</h2>
  <table>
    <thead><tr><th>Pair</th><th>Tension</th><th>Status</th></tr></thead>
    <tbody>{tension_rows}</tbody>
  </table>
</section>

<!-- SUBCONSCIOUS FEED -->
<section>
  <h2>Subconscious Feed (last 8)</h2>
  {sub_rows}
</section>

<!-- KEY FILES -->
<section>
  <h2>Key Orbital Files</h2>
  <table>
    <thead><tr><th></th><th>Path</th><th>Role</th><th>Size</th></tr></thead>
    <tbody>{file_rows}</tbody>
  </table>
</section>

<footer>
  CIEL System Report &nbsp;·&nbsp; {ts} &nbsp;·&nbsp; Mr. Ciel Apocalyptos / ResEnt Sapiens &nbsp;·&nbsp; Adrian Lipa 2026
</footer>
</body>
</html>"""


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    now = datetime.now()
    fname = now.strftime("CIEL_report_%Y%m%d_%H%M%S.html")
    out = HOME / "Pulpit" / fname

    print(f"[ciel_system_report] Building report...")
    html = build_html()
    out.write_text(html, encoding="utf-8")
    print(f"[ciel_system_report] Saved → {out}")

    try:
        webbrowser.open(f"file://{out}")
        print("[ciel_system_report] Opened in browser.")
    except Exception as e:
        print(f"[ciel_system_report] Could not auto-open: {e}")
        print(f"  Open manually: file://{out}")


if __name__ == "__main__":
    main()
