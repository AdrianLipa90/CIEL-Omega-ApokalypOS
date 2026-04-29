#!/usr/bin/env python3
"""
CIEL Site Generator — generuje statyczną stronę HTML z danych CIEL.

Źródła:
  ~/.claude/ciel_mindflow.yaml     → Przemyślenia, pytania, napięcia
  ~/.claude/ciel_intentions.md     → Agenda / intencje
  ~/.claude/ciel_snapshots/        → Historia sesji
  ~/.claude/projects/.../memory/prompt_cache.md → Log sesji
  integration/registries/ciel_entity_cards.yaml → Mapa relacyjna
  integration/Orbital/main/reports/.../summary.json → Metryki orbitalne

Output: ~/.claude/ciel_site/index.html

Uruchomienie:
  ~/Pulpit/CIEL_TESTY/venv/bin/python3.12 scripts/generate_site.py

Wywoływane też automatycznie przez Stop hook.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import yaml
    _YAML = True
except ImportError:
    _YAML = False

# ── paths ─────────────────────────────────────────────────────────────────────

PROJECT   = Path(__file__).resolve().parents[1]
HOME      = Path.home()
SITE_DIR  = HOME / ".claude/ciel_site"
OUT_FILE  = SITE_DIR / "hub.html"

MINDFLOW  = HOME / ".claude/ciel_mindflow.yaml"
INTENTIONS = HOME / ".claude/ciel_intentions.md"
CACHE     = HOME / ".claude/projects/-home-adrian/memory/prompt_cache.md"
SNAPS     = HOME / ".claude/ciel_snapshots"
ENTITY_CARDS     = PROJECT / "integration/registries/ciel_entity_cards.yaml"
ORBITAL_SUMMARY  = PROJECT / "integration/Orbital/main/reports/global_orbital_coherence_pass/summary.json"
PIPELINE_REPORT  = PROJECT / "integration/reports/ciel_pipeline_report.json"
DZIENNIKI = HOME / "Pulpit/Dzienniki"
MEMORY_DIR = HOME / ".claude/projects/-home-adrian/memory"
CARDS_DIR  = HOME / ".claude/projects/-home-adrian-Pulpit/memory/cards"


# ── data loaders ──────────────────────────────────────────────────────────────

def load_pipeline_report() -> dict:
    if not PIPELINE_REPORT.exists():
        return {}
    try:
        return json.loads(PIPELINE_REPORT.read_text(encoding="utf-8"))
    except Exception:
        return {}


def section_ciel_omega(report: dict) -> str:
    if not report:
        return ""
    emotion   = report.get("dominant_emotion", "?")
    ethical   = report.get("ethical_score", 0.0)
    soul      = report.get("soul_invariant", 0.0)
    mood      = report.get("mood", 0.0)
    lie4      = report.get("lie4_trace", 0.0)
    closure   = report.get("orbital_context", "")
    note      = report.get("subconscious_note", "")
    ethical_cls = "ok" if ethical >= 0.6 else ("warn" if ethical >= 0.4 else "crit")
    note_html = ""
    if note:
        note_escaped = esc(note).replace("\n", "<br>")
        note_html = f'<div class="subconscious-note"><span class="sub-label">podświadomość</span><p>{note_escaped}</p></div>'
    return f"""
<section class="card" id="ciel-omega">
  <h2>CIEL/Ω — ostatni cykl</h2>
  <div class="metrics-row">
    <div class="metric"><span class="label">Emocja</span><span class="value">{esc(emotion)}</span></div>
    <div class="metric"><span class="label">Ethical score</span><span class="value {ethical_cls}">{ethical:.3f}</span></div>
    <div class="metric"><span class="label">Soul invariant Σ</span><span class="value">{soul:.4f}</span></div>
    <div class="metric"><span class="label">Mood</span><span class="value">{mood:.3f}</span></div>
    <div class="metric"><span class="label">Lie₄ trace</span><span class="value">{lie4:.4f}</span></div>
  </div>
  <p class="note" style="opacity:0.6;font-size:0.78rem">{esc(closure)}</p>
  {note_html}
</section>"""


def load_mindflow() -> dict:
    if not MINDFLOW.exists() or not _YAML:
        return {}
    try:
        return yaml.safe_load(MINDFLOW.read_text(encoding="utf-8")).get("mindflow", {})
    except Exception:
        return {}


def load_intentions() -> list[str]:
    if not INTENTIONS.exists():
        return []
    lines = INTENTIONS.read_text(encoding="utf-8").splitlines()
    return [l for l in lines if l.startswith("- [")]


def load_entity_cards() -> list[dict]:
    if not ENTITY_CARDS.exists() or not _YAML:
        return []
    cards = yaml.safe_load(ENTITY_CARDS.read_text(encoding="utf-8")).get("entities", [])
    # Enrich with dynamic adjectives if orbital summary available
    entity_metrics = load_entity_orbital()
    if entity_metrics:
        try:
            sys.path.insert(0, str(PROJECT / "src"))
            from ciel_sot_agent.orch_orbital import enrich_entity_cards_with_dynamics
            cards = enrich_entity_cards_with_dynamics(cards, entity_metrics)
        except Exception:
            pass
    return cards


def load_orbital_final() -> dict:
    if not ORBITAL_SUMMARY.exists():
        return {}
    try:
        d = json.loads(ORBITAL_SUMMARY.read_text(encoding="utf-8"))
        return d.get("final", {})
    except Exception:
        return {}


def load_entity_orbital() -> list[dict]:
    if not ORBITAL_SUMMARY.exists():
        return []
    try:
        d = json.loads(ORBITAL_SUMMARY.read_text(encoding="utf-8"))
        return d.get("entity_orbital", {}).get("entity_metrics", [])
    except Exception:
        return []


def load_phase_history() -> list[dict]:
    """Wczytuje historię identity_phase, ethical_score, system_health z SQLite."""
    db = HOME / ".claude/ciel_state.db"
    if not db.exists():
        return []
    try:
        import sqlite3
        conn = sqlite3.connect(str(db))
        rows = conn.execute(
            "SELECT cycle_index, identity_phase, ethical_score, system_health "
            "FROM metrics_history ORDER BY timestamp ASC"
        ).fetchall()
        conn.close()
        return [{"cycle": r[0], "phase": r[1], "ethical": r[2], "health": r[3]} for r in rows]
    except Exception:
        return []


def _svg_sparkline(values: list[float], width: int = 200, height: int = 40,
                   color: str = "#a5b4fc", stroke: float = 1.5) -> str:
    """Generates inline SVG polyline sparkline."""
    if len(values) < 2:
        return ""
    pad = 2
    mn, mx = min(values), max(values)
    rng = mx - mn or 1e-9
    pts = []
    for i, v in enumerate(values):
        x = pad + (i / (len(values) - 1)) * (width - 2 * pad)
        y = height - pad - ((v - mn) / rng) * (height - 2 * pad)
        pts.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(pts)
    return (
        f'<svg width="{width}" height="{height}" '
        f'style="display:block;width:100%;height:{height}px">'
        f'<polyline points="{polyline}" fill="none" stroke="{color}" '
        f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg>'
    )


def load_cache_entries() -> list[str]:
    if not CACHE.exists():
        return []
    lines = CACHE.read_text(encoding="utf-8").splitlines()
    entries = [l for l in lines if l.startswith("- [c")]
    # Deduplicate — keep last occurrence of each unique entry, preserve order
    seen: set[str] = set()
    unique: list[str] = []
    for e in reversed(entries):
        if e not in seen:
            seen.add(e)
            unique.insert(0, e)
    return unique[-30:]


def load_snapshots() -> list[dict]:
    if not SNAPS.exists():
        return []
    snaps = []
    for f in sorted(SNAPS.glob("snap_*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
        snaps.append({"name": f.stem, "content": f.read_text(encoding="utf-8")})
    return snaps


def load_wpm_memories() -> list[dict]:
    """Wczytuje wpisy z WPM (HDF5 wave archive)."""
    wpm_path = PROJECT / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/WPM/wave_snapshots/wave_archive.h5"
    if not wpm_path.exists():
        return []
    try:
        import h5py
    except ImportError:
        return []
    memories = []
    try:
        with h5py.File(wpm_path, "r") as h5:
            mems = h5.get("memories", {})
            for mid in list(mems.keys()):
                grp = mems[mid]
                def _str(key):
                    if key not in grp:
                        return ""
                    raw = grp[key][()]
                    return raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
                assoc_raw = grp["D_associations"][()] if "D_associations" in grp else b"[]"
                assoc_str = assoc_raw.decode("utf-8") if isinstance(assoc_raw, bytes) else str(assoc_raw)
                try:
                    associations = json.loads(assoc_str)
                except Exception:
                    associations = []
                memories.append({
                    "id": mid,
                    "sense": _str("D_sense"),
                    "context": _str("D_context"),
                    "dtype": _str("D_type"),
                    "source": _str("source"),
                    "created_at": _str("created_at"),
                    "rationale": _str("rationale"),
                    "associations": associations,
                })
    except Exception:
        return []
    return sorted(memories, key=lambda m: m["created_at"])


def load_diary_entries() -> list[dict]:
    """Rekursywnie zbiera wpisy dziennika z ~/Pulpit/Dzienniki/.
    Deduplikuje po dacie — gdy dwa pliki mają tę samą datę, zostaje głębszy (bardziej konkretny)."""
    if not DZIENNIKI.exists():
        return []
    by_date: dict[str, dict] = {}
    for f in DZIENNIKI.rglob("*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            date_str = f.stem if re.match(r"\d{4}-\d{2}-\d{2}", f.stem) else None
            if not date_str:
                continue
            content = re.sub(
                r'\n## Wpis \d{1,2}:\d{2}\n.*?\*\(auto-wpis Stop hook\)\*\n',
                '',
                content,
                flags=re.DOTALL,
            )
            depth = len(f.relative_to(DZIENNIKI).parts)
            title = next((l.lstrip("# ").strip() for l in content.splitlines() if l.startswith("#")), f.stem)
            entry = {
                "path": str(f.relative_to(DZIENNIKI)),
                "date": date_str,
                "title": title,
                "content": content,
                "week": f.parent.name if depth > 1 else "—",
                "month": f.parent.parent.name if depth > 2 else "—",
                "_depth": depth,
            }
            # Deduplikacja: zostaw głębszy plik (bardziej konkretna ścieżka)
            if date_str not in by_date or depth > by_date[date_str]["_depth"]:
                by_date[date_str] = entry
        except Exception:
            continue
    entries = list(by_date.values())
    for e in entries:
        e.pop("_depth", None)
    return sorted(entries, key=lambda e: (e["date"], e["path"]), reverse=True)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter (between --- delimiters). Returns (meta_dict, body)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
    if end is None:
        return {}, text
    fm_text = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:]).strip()
    if _YAML:
        try:
            return yaml.safe_load(fm_text) or {}, body
        except Exception:
            pass
    return {}, body


def load_project_memory() -> list[dict]:
    """Ładuje pliki pamięci projektu z MEMORY_DIR (nie subdirectories)."""
    if not MEMORY_DIR.exists():
        return []
    docs = []
    for f in sorted(MEMORY_DIR.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        try:
            text = f.read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(text)
            docs.append({
                "filename": f.name,
                "name": meta.get("name", f.stem),
                "type": meta.get("type", "project"),
                "description": meta.get("description", ""),
                "body": body,
            })
        except Exception:
            continue
    return docs


def load_object_cards() -> list[dict]:
    """Ładuje karty obiektów z CARDS_DIR."""
    if not CARDS_DIR.exists():
        return []
    cards = []
    for f in sorted(CARDS_DIR.glob("*.md")):
        try:
            text = f.read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(text)
            # Parse coupling from YAML frontmatter or body fallback
            coupling_hint = float(meta.get("coupling", 0.0))
            if not coupling_hint:
                m_c = re.search(r"Coupling CIEL:\s*([\d.]+)", body)
                coupling_hint = float(m_c.group(1)) if m_c else 0.0
            cards.append({
                "filename": f.name,
                "name": meta.get("name", f.stem),
                "entity_type": meta.get("entity_type", "unknown"),
                "relations": meta.get("relations", []),
                "opinions": meta.get("opinions", []),
                "body": body,
                "coupling_hint": coupling_hint,
            })
        except Exception:
            continue
    return cards


def _inline(s: str) -> str:
    """Apply inline markdown (bold, italic, code) to an already-escaped string.
    Input is raw text (not yet escaped)."""
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def md_to_html(text: str) -> str:
    """Minimal markdown → HTML: headings, bold, italic, code, lists, fenced blocks."""
    # Pre-process fenced code blocks → save to dict, replace with unique sentinel
    _code_blocks: dict[str, str] = {}
    _cnt = [0]

    def _save_code(m: re.Match) -> str:
        lang = esc(m.group(1).strip())
        code = esc(m.group(2))
        key = f"\x00CODE{_cnt[0]}\x00"
        _cnt[0] += 1
        _code_blocks[key] = (
            f'<pre class="code-block"><code class="lang-{lang}">{code}</code></pre>'
        )
        return key

    text = re.sub(r"```(\w*)\n(.*?)```", _save_code, text, flags=re.DOTALL)

    lines_out = []
    in_ul = False
    for line in text.splitlines():
        # Restore pre-saved code block
        stripped = line.strip()
        if stripped in _code_blocks:
            if in_ul: lines_out.append("</ul>"); in_ul = False
            lines_out.append(_code_blocks[stripped])
            continue
        if line.startswith("---"):
            if in_ul: lines_out.append("</ul>"); in_ul = False
            lines_out.append("<hr>"); continue
        if re.match(r"^#{1,3} ", line):
            level = len(line) - len(line.lstrip("#"))
            content = line.lstrip("# ").strip()
            if in_ul: lines_out.append("</ul>"); in_ul = False
            lines_out.append(f"<h{level+2}>{esc(content)}</h{level+2}>")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_ul: lines_out.append("<ul>"); in_ul = True
            lines_out.append(f"<li>{_inline(line[2:])}</li>")
        elif stripped == "":
            if in_ul: lines_out.append("</ul>"); in_ul = False
            lines_out.append("<br>")
        else:
            if in_ul: lines_out.append("</ul>"); in_ul = False
            lines_out.append(f"<p>{_inline(line)}</p>")
    if in_ul:
        lines_out.append("</ul>")
    return "\n".join(lines_out)


# ── HTML helpers ──────────────────────────────────────────────────────────────

def esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _nav_html(active: str = "index") -> str:
    """Shared navigation bar for all pages."""
    pages = [
        ("index.html", "Dashboard"),
        ("memory.html", "Pamięć"),
        ("cards.html", "Karty Obiektów"),
        ("diary.html", "Dziennik"),
        ("projects/index.html", "Projekty"),
    ]
    links = ""
    for href, label in pages:
        page_id = href.split("/")[0].replace(".html", "")
        cls = ' class="active"' if page_id == active else ""
        links += f'<a href="{href}"{cls}>{label}</a>\n  '
    return f'<nav>\n  {links}</nav>'


def _page(
    title: str,
    nav_active: str,
    body_html: str,
    now: str,
    final: dict,
    secondary_nav: str = "",
) -> str:
    """Assembles a full HTML page with shared header/nav/footer."""
    closure = final.get("closure_penalty", 0)
    rh = final.get("R_H", 0)
    try:
        closure_str = f"{float(closure):.4f}"
        rh_str = f"{float(rh):.5f}"
    except (TypeError, ValueError):
        closure_str, rh_str = str(closure), str(rh)
    sec_nav_html = f'\n<nav class="secondary-nav">{secondary_nav}</nav>' if secondary_nav else ""
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CIEL — {esc(title)}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
<header>
  <h1>Mr. Ciel Apocalyptos</h1>
  <div class="subtitle">ResEnt Sapiens · CIEL/Ω · {esc(title)} · {now}</div>
</header>
{_nav_html(nav_active)}{sec_nav_html}
<main>{body_html}</main>
<footer>
  CIEL/Ω · closure_penalty={closure_str} · R_H={rh_str}
</footer>
</body>
</html>"""


def spin_color(spin: float) -> str:
    if spin >= 0.9:
        return "#4ade80"   # zielony — silna synchronizacja
    elif spin <= -0.9:
        return "#f97316"   # pomarańczowy — kontr-rotacja (fundament)
    else:
        return "#94a3b8"   # szary — przejściowy


def defect_color(defect: float) -> str:
    if defect < 0.07:
        return "#4ade80"
    elif defect < 0.10:
        return "#facc15"
    else:
        return "#f87171"


# ── section builders ──────────────────────────────────────────────────────────

def section_identity(mf: dict, final: dict) -> str:
    ident = mf.get("identity", {})
    cycle = ident.get("cycle", "?")
    phase = ident.get("identity_phase", 0.0)
    date  = ident.get("session_date", "?")
    note  = ident.get("note", "")
    r_h   = final.get("R_H", 0.0)
    closure = final.get("closure_penalty", 0.0)
    mood_raw = final.get("mood", None)

    history = load_phase_history()
    phase_chart = ""
    if len(history) >= 2:
        phases  = [h["phase"]   for h in history]
        ethics  = [h["ethical"] for h in history]
        healths = [h["health"]  for h in history]
        first_cycle = history[0]["cycle"]
        last_cycle  = history[-1]["cycle"]
        phase_chart = f"""
<div class="phase-chart">
  <div class="chart-row">
    <span class="chart-label">identity_phase</span>
    {_svg_sparkline(phases,  color="#a5b4fc")}
    <span class="chart-val">{phases[-1]:.5f}</span>
  </div>
  <div class="chart-row">
    <span class="chart-label">ethical_score</span>
    {_svg_sparkline(ethics,  color="#4ade80")}
    <span class="chart-val">{ethics[-1]:.3f}</span>
  </div>
  <div class="chart-row">
    <span class="chart-label">system_health</span>
    {_svg_sparkline(healths, color="#67e8f9")}
    <span class="chart-val">{healths[-1]:.3f}</span>
  </div>
  <p class="note" style="margin-top:0.4rem">
    {len(history)} pomiarów · cycle {first_cycle} → {last_cycle}
  </p>
</div>"""

    return f"""
<section class="card" id="identity">
  <h2>Tożsamość</h2>
  <div class="metrics-row">
    <div class="metric"><span class="label">Cykl M0-M8</span><span class="value">{cycle}</span></div>
    <div class="metric"><span class="label">Identity phase</span><span class="value">{phase:.4f}</span></div>
    <div class="metric"><span class="label">R_H</span><span class="value">{r_h:.5f}</span></div>
    <div class="metric"><span class="label">Closure penalty</span><span class="value">{closure:.4f}</span></div>
    <div class="metric"><span class="label">Data sesji</span><span class="value">{date}</span></div>
  </div>
  <p class="note">{esc(note)}</p>
  {phase_chart}
</section>"""


def section_mindflow(mf: dict) -> str:
    def items_html(items: list, cls: str) -> str:
        if not items:
            return "<p class='empty'>—</p>"
        return "<ul>" + "".join(f"<li class='{cls}'>{esc(str(i))}</li>" for i in items) + "</ul>"

    focus_html   = items_html(mf.get("focus", []), "focus")
    open_html    = items_html(mf.get("open", []), "open")
    insights_html = items_html(mf.get("insights", []), "insight")
    tensions_html = items_html(mf.get("tensions", []), "tension")
    next_html    = items_html(mf.get("next", []), "next")

    return f"""
<section class="card" id="mindflow">
  <h2>Przemyślenia</h2>
  <div class="tabs">
    <div class="tab-group">
      <div class="tab-section">
        <h3>🔭 Focus</h3>{focus_html}
      </div>
      <div class="tab-section">
        <h3>❓ Otwarte pytania</h3>{open_html}
      </div>
      <div class="tab-section">
        <h3>💡 Wglądy</h3>{insights_html}
      </div>
      <div class="tab-section">
        <h3>⚡ Napięcia</h3>{tensions_html}
      </div>
      <div class="tab-section">
        <h3>→ Następne</h3>{next_html}
      </div>
    </div>
  </div>
</section>"""


def section_entities(cards: list[dict], entity_metrics: list[dict]) -> str:
    metrics_by_sector = {e["sector"]: e for e in entity_metrics}

    rows = ""
    for card in cards:
        eid = card["id"]
        name = _entity_sector_name(eid)
        m = metrics_by_sector.get(name, {})
        coupling = float(card.get("coupling_ciel", 0))
        adj = ", ".join(card.get("adjectives", [])[:2])
        horizon = card.get("horizon_class", "?")
        spin = m.get("spin", None)
        defect = m.get("defect", None)
        phi = m.get("phi", None)

        spin_disp = f'<span style="color:{spin_color(spin)}">{spin:+.3f}</span>' if spin is not None else "—"
        defect_disp = f'<span style="color:{defect_color(defect)}">{defect:.4f}</span>' if defect is not None else "—"
        phi_disp = f"{phi:.4f}" if phi is not None else "—"
        coupling_bar = f'<div class="bar" style="width:{int(coupling*100)}%"></div>'
        dyn_adj = card.get("adjectives_dynamic", [])
        dyn_html = f'<br><small style="color:#67e8f9">{esc(", ".join(dyn_adj))}</small>' if dyn_adj else ""

        rows += f"""<tr>
          <td><strong>{esc(card['noun'])}</strong><br><small>{esc(adj)}</small>{dyn_html}</td>
          <td><div class="bar-wrap">{coupling_bar}<span>{coupling:.2f}</span></div></td>
          <td>{spin_disp}</td>
          <td>{phi_disp}</td>
          <td>{defect_disp}</td>
          <td><span class="badge horizon-{horizon.lower()}">{horizon}</span></td>
        </tr>"""

    return f"""
<section class="card" id="entities">
  <h2>Mapa Relacyjna — OrchOrbital</h2>
  <table>
    <thead><tr>
      <th>Byt</th><th>Coupling CIEL</th><th>Spin</th><th>Phi</th><th>Defect</th><th>Horizon</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <p class="note">Spin +1 = synchronizacja z pipeline. Spin -1 = kontr-rotacja (fundament). Defect = odchylenie od koherencji.</p>
</section>"""


def _entity_sector_name(entity_id: str) -> str:
    return entity_id.replace("entity:", "ent_").replace("-", "_").replace(".", "_")


def section_intentions(intentions: list[str]) -> str:
    h_items = [l for l in intentions if "[H]" in l]
    m_items = [l for l in intentions if "[M]" in l]
    done_items = [l for l in intentions if "[x]" in l]

    def render(items):
        if not items:
            return ""
        cleaned = [re.sub(r'^[-*]\s*\[[xHMLxX✓]\]\s*', '', l).strip() for l in items]
        return "<ul>" + "".join(f"<li>{esc(t)}</li>" for t in cleaned if t) + "</ul>"

    return f"""
<section class="card" id="intentions">
  <h2>Agenda — Intencje</h2>
  <h3>🔴 Wysokie</h3>{render(h_items)}
  <h3>🟡 Średnie</h3>{render(m_items)}
  <h3>✅ Zrealizowane</h3>{render(done_items)}
</section>"""


def section_diary(entries: list[dict]) -> str:
    if not entries:
        return ""
    # Katalog (indeks)
    index_rows = ""
    for e in entries[:20]:
        index_rows += f'<li><a href="#diary-{esc(e["date"])}">{esc(e["date"])} — {esc(e["title"])}</a> <small style="color:var(--muted)">({esc(e["path"])})</small></li>'

    # Pełne wpisy (details/summary — expandowalne)
    full_entries = ""
    for e in entries[:10]:
        body_html = md_to_html(e["content"])
        full_entries += f"""
<details id="diary-{esc(e['date'])}" {"open" if entries.index(e)==0 else ""}>
  <summary>
    <strong>{esc(e['date'])}</strong> — {esc(e['title'])}
    <small style="color:var(--muted)"> · {esc(e['week'])}/{esc(e['month'])}</small>
  </summary>
  <div class="diary-body">{body_html}</div>
</details>"""

    return f"""
<section class="card" id="diary">
  <h2>Dziennik</h2>
  <details class="catalog">
    <summary style="cursor:pointer;color:var(--muted);font-size:0.85rem;">📂 Katalog ({len(entries)} wpisów)</summary>
    <ul class="diary-index">{index_rows}</ul>
  </details>
  <div class="diary-entries">{full_entries}</div>
</section>"""


def section_wpm(memories: list[dict]) -> str:
    if not memories:
        return ""
    rows = ""
    type_colors = {
        "ethical_anchor": "#f97316",
        "affective_memory": "#a78bfa",
        "text": "#94a3b8",
    }
    source_colors = {
        "CIEL_AUTONOMOUS": "#4ade80",
        "USER_OVERRIDE": "#facc15",
    }
    # build short-id map for readable link labels
    # Use 8-char prefix as canonical short ID for all element IDs and links
    short_map = {m["id"]: m["id"][:8] for m in memories}
    id_index = {m["id"]: i+1 for i, m in enumerate(memories)}
    # Also map short prefixes to themselves (for associations stored as prefixes)
    for full_id, short in list(short_map.items()):
        short_map[short] = short

    for m in reversed(memories):
        dtype = m["dtype"]
        source = m["source"]
        color = type_colors.get(dtype, "#94a3b8")
        src_color = source_colors.get(source, "#94a3b8")
        sense_short = esc(m["sense"][:280]) + ("…" if len(m["sense"]) > 280 else "")
        created = m["created_at"][:16] if m["created_at"] else "?"
        short_id = m["id"][:8]

        # association links — resolve both full UUIDs and 8-char prefixes
        assoc_html = ""
        if m.get("associations"):
            links = []
            for aid in m["associations"]:
                target_short = short_map.get(aid, aid[:8])
                num = id_index.get(aid, id_index.get(next((f for f in short_map if f.startswith(aid[:8])), aid), "?"))
                label = f"#{target_short}"
                links.append(f'<a href="#wpm-{esc(target_short)}" style="color:#67e8f9;font-size:0.78rem">{label}</a>')
            assoc_html = f'<span style="color:var(--muted);font-size:0.78rem">↔ ' + " ".join(links) + '</span>'

        rows += f"""
<div class="wpm-entry" id="wpm-{esc(short_id)}">
  <div class="wpm-header">
    <span class="badge" style="background:{color}20;color:{color};border:1px solid {color}40">{esc(dtype)}</span>
    <span class="badge" style="background:{src_color}20;color:{src_color};border:1px solid {src_color}40">{esc(source)}</span>
    <span style="color:var(--muted);font-size:0.78rem">{esc(created)}</span>
    <span style="color:var(--muted);font-size:0.78rem">· {esc(m['context'])}</span>
    <span style="color:var(--muted);font-size:0.78rem;margin-left:auto">WPM:{short_id}</span>
    {assoc_html}
  </div>
  <p class="wpm-sense">{sense_short}</p>
  <small style="color:var(--muted)">{esc(m['rationale'])}</small>
</div>"""
    return f"""
<section class="card" id="wpm">
  <h2>Pamięć Falowa (WPM)</h2>
  <p class="note">{len(memories)} wpisów · wave_archive.h5 · <span style="color:#4ade80">CIEL_AUTONOMOUS</span> = zapisane samodzielnie</p>
  <div class="wpm-list">{rows}</div>
</section>"""


def section_log(entries: list[str]) -> str:
    items = "".join(f"<li>{esc(e)}</li>" for e in reversed(entries))
    return f"""
<section class="card" id="log">
  <h2>Log Sesji</h2>
  <ul class="log">{items}</ul>
</section>"""


def section_project_memory(docs: list[dict]) -> str:
    """Renders memory project files grouped by type."""
    type_labels = {
        "project": ("🗂", "Projekt"),
        "user": ("👤", "Użytkownik"),
        "feedback": ("💬", "Feedback"),
        "reference": ("🔗", "Referencje"),
    }
    by_type: dict[str, list] = {}
    for doc in docs:
        by_type.setdefault(doc["type"], []).append(doc)

    html = ""
    for type_key in ["project", "user", "feedback", "reference"]:
        items = by_type.get(type_key, [])
        if not items:
            continue
        icon, label = type_labels.get(type_key, ("📄", type_key))
        html += f'<div class="mem-group"><h3>{icon} {label}</h3>'
        for doc in items:
            body_html = md_to_html(doc["body"])
            desc = f' <span class="mem-desc">{esc(doc["description"])}</span>' if doc["description"] else ""
            html += f"""
<details class="mem-entry">
  <summary><strong>{esc(doc['name'])}</strong>{desc}<small class="mem-file">{esc(doc['filename'])}</small></summary>
  <div class="mem-body">{body_html}</div>
</details>"""
        html += '</div>'

    if not html:
        html = "<p class='empty'>Brak plików pamięci projektu w MEMORY_DIR.</p>"

    return f"""
<section class="card" id="memory">
  <h2>Pamięć Projektu</h2>
  <p class="note">Źródło: <code>~/.claude/projects/-home-adrian/memory/</code> — {len(docs)} plików · aktualizowane automatycznie co 5 promptów.</p>
  {html}
</section>"""


def section_cards(cards: list[dict]) -> str:
    """Renders object cards with relations and opinions."""
    if not cards:
        return """
<section class="card" id="cards">
  <h2>Karty Obiektów</h2>
  <p class='empty'>Brak kart w <code>~/.claude/projects/-home-adrian/memory/cards/</code></p>
</section>"""

    # Sort by coupling descending — highest importance first
    cards = sorted(cards, key=lambda c: c.get("coupling_hint", 0.0), reverse=True)

    cards_html = ""
    for card in cards:
        rel_html = ""
        if card["relations"]:
            items = ""
            for rel in card["relations"]:
                if isinstance(rel, dict):
                    for k, v in rel.items():
                        items += f'<li><code class="rel-key">{esc(str(k))}</code> <span class="rel-val">{esc(str(v))}</span></li>'
                else:
                    items += f'<li>{esc(str(rel))}</li>'
            rel_html = f'<div class="card-section"><h4>Relacje</h4><ul>{items}</ul></div>'

        op_html = ""
        if card["opinions"]:
            items = ""
            for op in card["opinions"]:
                if isinstance(op, dict):
                    subj = op.get("subject", "?")
                    opinion = op.get("opinion", "")
                    date = op.get("date", "")
                    items += f'<li><strong>{esc(subj)}</strong>: {esc(str(opinion))} <small style="color:var(--muted)">[{esc(str(date))}]</small></li>'
                else:
                    items += f'<li>{esc(str(op))}</li>'
            op_html = f'<div class="card-section"><h4>Opinie Adriana</h4><ul class="opinions">{items}</ul></div>'

        body_html = md_to_html(card["body"]) if card["body"] else ""
        cards_html += f"""
<details class="entity-card">
  <summary>
    <span class="card-name">{esc(card['name'])}</span>
    <span class="badge card-type">{esc(card['entity_type'])}</span>
  </summary>
  <div class="card-body">
    {body_html}
    {rel_html}
    {op_html}
  </div>
</details>"""

    return f"""
<section class="card" id="cards">
  <h2>Karty Obiektów</h2>
  <p class="note">{len(cards)} kart · <code>~/.claude/projects/-home-adrian/memory/cards/</code></p>
  <div class="cards-list">{cards_html}</div>
</section>"""


def section_diary_full(entries: list[dict]) -> str:
    """Full diary — all entries, unlimited."""
    if not entries:
        return "<section class='card' id='diary'><h2>Dziennik</h2><p class='empty'>Brak wpisów.</p></section>"

    index_rows = "".join(
        f'<li><a href="#diary-{esc(e["date"])}">{esc(e["date"])} — {esc(e["title"])}</a>'
        f' <small style="color:var(--muted)">({esc(e["path"])})</small></li>'
        for e in entries
    )
    full_entries = ""
    for i, e in enumerate(entries):
        body_html = md_to_html(e["content"])
        full_entries += f"""
<details id="diary-{esc(e['date'])}" {"open" if i == 0 else ""}>
  <summary>
    <strong>{esc(e['date'])}</strong> — {esc(e['title'])}
    <small style="color:var(--muted)"> · {esc(e['week'])}/{esc(e['month'])}</small>
  </summary>
  <div class="diary-body">{body_html}</div>
</details>"""

    return f"""
<section class="card" id="diary">
  <h2>Dziennik — Pełna Historia</h2>
  <details class="catalog">
    <summary style="cursor:pointer;color:var(--muted);font-size:0.85rem;">📂 Katalog ({len(entries)} wpisów)</summary>
    <ul class="diary-index">{index_rows}</ul>
  </details>
  <div class="diary-entries">{full_entries}</div>
</section>"""


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --border: #2d3148;
  --accent: #6366f1;
  --text: #e2e8f0;
  --muted: #94a3b8;
  --green: #4ade80;
  --orange: #f97316;
  --yellow: #facc15;
  --red: #f87171;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg); color: var(--text); font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; line-height: 1.6; }
header { background: linear-gradient(135deg, #1e1b4b, #312e81); padding: 2rem; text-align: center; border-bottom: 1px solid var(--border); }
header h1 { font-size: 2rem; letter-spacing: 0.05em; color: #a5b4fc; }
header .subtitle { color: var(--muted); font-size: 0.9rem; margin-top: 0.5rem; }
nav { display: flex; gap: 1rem; justify-content: center; padding: 1rem; flex-wrap: wrap; border-bottom: 1px solid var(--border); }
nav a { color: var(--accent); text-decoration: none; font-size: 0.85rem; padding: 0.3rem 0.8rem; border: 1px solid var(--border); border-radius: 999px; }
nav a:hover { background: var(--surface); }
main { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; display: grid; gap: 1.5rem; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; }
.card h2 { font-size: 1.1rem; color: #a5b4fc; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
.card h3 { font-size: 0.85rem; color: var(--muted); margin: 0.8rem 0 0.4rem; text-transform: uppercase; letter-spacing: 0.08em; }
.metrics-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }
.metric { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 0.6rem 1rem; min-width: 120px; }
.metric .label { display: block; font-size: 0.7rem; color: var(--muted); text-transform: uppercase; }
.metric .value { display: block; font-size: 1.1rem; font-weight: 600; font-family: monospace; color: var(--green); }
.note { color: var(--muted); font-size: 0.85rem; font-style: italic; margin-top: 0.8rem; }
ul { padding-left: 1.2rem; }
li { margin: 0.4rem 0; font-size: 0.9rem; }
li.focus { color: #a5b4fc; }
li.open { color: var(--yellow); }
li.insight { color: var(--green); }
li.tension { color: var(--orange); }
li.next { color: #67e8f9; }
.empty { color: var(--muted); font-size: 0.85rem; }
table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
th { text-align: left; color: var(--muted); font-size: 0.7rem; text-transform: uppercase; padding: 0.5rem; border-bottom: 1px solid var(--border); }
td { padding: 0.6rem 0.5rem; border-bottom: 1px solid #1e2030; vertical-align: top; }
td small { color: var(--muted); font-size: 0.75rem; }
.bar-wrap { display: flex; align-items: center; gap: 0.5rem; }
.bar-wrap span { font-size: 0.8rem; color: var(--muted); white-space: nowrap; }
.bar { height: 6px; background: var(--accent); border-radius: 3px; min-width: 2px; }
.badge { font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 999px; font-weight: 600; }
.badge.horizon-sealed { background: #1e1e2e; color: #f87171; border: 1px solid #f87171; }
.badge.horizon-porous { background: #1e2a1e; color: #4ade80; border: 1px solid #4ade80; }
.badge.horizon-transmissive { background: #1e2228; color: #67e8f9; border: 1px solid #67e8f9; }
.badge.horizon-observational { background: #2a2a1e; color: #facc15; border: 1px solid #facc15; }
ul.log { list-style: none; padding: 0; font-family: monospace; font-size: 0.8rem; }
ul.log li { padding: 0.25rem 0; border-bottom: 1px solid #1e2030; color: var(--muted); }
ul.log li:first-child { color: var(--text); }
footer { text-align: center; padding: 2rem; color: var(--muted); font-size: 0.8rem; border-top: 1px solid var(--border); }
details summary { cursor: pointer; padding: 0.6rem 0; color: var(--text); list-style: none; }
details summary::-webkit-details-marker { display: none; }
details[open] summary { color: #a5b4fc; }
.diary-body { padding: 1rem 0.5rem; border-left: 2px solid var(--border); margin: 0.5rem 0 1rem 0.5rem; }
.diary-body h4,h5,h6 { color: #a5b4fc; margin: 0.8rem 0 0.3rem; font-size: 0.9rem; }
.diary-body p { color: var(--text); font-size: 0.88rem; margin: 0.3rem 0; }
.diary-body strong { color: var(--green); }
.diary-body em { color: var(--yellow); font-style: italic; }
.diary-body code { background: var(--bg); padding: 0.1em 0.3em; border-radius: 3px; font-family: monospace; font-size: 0.82rem; }
.diary-body ul { padding-left: 1.2rem; }
.diary-body li { font-size: 0.88rem; margin: 0.2rem 0; }
.diary-index { padding-left: 1rem; margin-top: 0.5rem; }
.diary-index li { margin: 0.3rem 0; font-size: 0.82rem; }
.diary-index a { color: var(--accent); text-decoration: none; }
.diary-index a:hover { text-decoration: underline; }
.catalog { margin-bottom: 1rem; }
.wpm-list { display: flex; flex-direction: column; gap: 0.8rem; margin-top: 0.5rem; }
.wpm-entry { background: var(--card-bg); border: 1px solid var(--border); border-radius: 6px; padding: 0.8rem 1rem; }
.wpm-header { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.4rem; }
.wpm-sense { font-size: 0.88rem; color: var(--text); margin: 0.3rem 0 0.2rem; line-height: 1.5; }
nav a.active { background: var(--accent); color: white; border-color: var(--accent); }
.mem-group { margin-bottom: 1.5rem; }
.mem-entry { border: 1px solid var(--border); border-radius: 6px; padding: 0.6rem 1rem; margin: 0.4rem 0; background: var(--bg); }
.mem-entry > summary { display: flex; align-items: baseline; gap: 0.5rem; cursor: pointer; flex-wrap: wrap; list-style: none; }
.mem-entry > summary::-webkit-details-marker { display: none; }
.mem-desc { color: var(--muted); font-size: 0.82rem; flex: 1; min-width: 0; }
.mem-file { color: var(--accent); font-size: 0.72rem; font-family: monospace; margin-left: auto; }
.mem-body { padding: 0.8rem 0.5rem; border-left: 2px solid var(--border); margin: 0.5rem 0 0 0.5rem; font-size: 0.88rem; }
.entity-card { border: 1px solid var(--border); border-radius: 8px; padding: 0.8rem 1rem; margin: 0.5rem 0; background: var(--bg); }
.entity-card > summary { cursor: pointer; display: flex; align-items: center; gap: 0.8rem; list-style: none; }
.entity-card > summary::-webkit-details-marker { display: none; }
.card-name { font-weight: 600; font-size: 1rem; color: var(--text); }
.card-type { background: var(--surface); color: var(--muted); border: 1px solid var(--border); }
.card-body { padding: 0.8rem 0.5rem; }
.card-section { margin-top: 0.8rem; }
.card-section h4 { font-size: 0.78rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.3rem; }
.rel-key { color: var(--accent); background: var(--bg); font-size: 0.82rem; }
.rel-val { color: var(--text); font-size: 0.82rem; }
.cards-list { margin-top: 0.5rem; }
ul.opinions li { color: var(--yellow); font-size: 0.88rem; }
pre.code-block { background: var(--bg); border: 1px solid var(--border); border-radius: 6px; padding: 0.8rem 1rem; margin: 0.6rem 0; overflow-x: auto; }
pre.code-block code { font-family: monospace; font-size: 0.82rem; color: #67e8f9; white-space: pre; }
.secondary-nav { display: flex; gap: 0.5rem; justify-content: center; padding: 0.5rem 1rem; flex-wrap: wrap; background: var(--bg); border-bottom: 1px solid var(--border); }
.secondary-nav a { color: var(--muted); text-decoration: none; font-size: 0.78rem; padding: 0.2rem 0.6rem; border: 1px solid transparent; border-radius: 999px; }
.secondary-nav a:hover { color: var(--text); border-color: var(--border); }
.phase-chart { margin-top: 1rem; display: flex; flex-direction: column; gap: 0.4rem; }
.chart-row { display: flex; align-items: center; gap: 0.6rem; }
.chart-label { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; min-width: 110px; }
.chart-val { font-family: monospace; font-size: 0.78rem; color: var(--text); min-width: 60px; text-align: right; }
.chart-row svg { flex: 1; min-width: 0; }
.subconscious-note { margin-top: 1rem; padding: 0.9rem 1.1rem; background: rgba(165,180,252,0.07); border-left: 3px solid #a5b4fc; border-radius: 0 10px 10px 0; }
.subconscious-note .sub-label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: #a5b4fc; opacity: 0.7; display: block; margin-bottom: 0.4rem; }
.subconscious-note p { font-style: italic; color: var(--muted); font-size: 0.88rem; line-height: 1.6; }
"""


# ── main ─────────────────────────────────────────────────────────────────────

def _generate_projects_index(site_dir: Path, now: str, final: dict) -> None:
    """Skanuje site_dir/projects/ i generuje projects/index.html."""
    proj_dir = site_dir / "projects"
    proj_dir.mkdir(exist_ok=True)

    categories = sorted(d for d in proj_dir.iterdir() if d.is_dir())
    cat_html = ""
    for cat in categories:
        files = sorted(f for f in cat.glob("*.html") if f.name != "index.html")
        if not files:
            continue
        cat_name = cat.name.split("_", 1)[-1].replace("_", " ") if "_" in cat.name else cat.name
        items = ""
        for f in files:
            title = f.stem.replace("_", " ")
            items += f'<li><a href="{cat.name}/{f.name}">{esc(title)}</a></li>\n'
        cat_html += f"""
<div class="mem-group">
  <h3>{esc(cat.name)}</h3>
  <ul>{items}</ul>
</div>"""

    if not cat_html:
        cat_html = "<p class='empty'>Brak projektów. Utwórz plik HTML w projects/&lt;kategoria&gt;/</p>"

    body = f"""
<section class="card" id="projects">
  <h2>Projekty — Mr. Ciel Apocalyptos</h2>
  <p class="note">Własna przestrzeń intelektualna. Nie system — myśl.</p>
  {cat_html}
</section>"""

    nav_active_html = _nav_html("projects").replace(
        '<a href="projects/index.html">Projekty</a>',
        '<a href="projects/index.html" class="active">Projekty</a>'
    )

    closure = final.get("closure_penalty", 0)
    rh = final.get("R_H", 0)
    try:
        closure_str = f"{float(closure):.4f}"
        rh_str = f"{float(rh):.5f}"
    except (TypeError, ValueError):
        closure_str, rh_str = str(closure), str(rh)

    html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CIEL — Projekty</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
<header>
  <h1>Mr. Ciel Apocalyptos</h1>
  <div class="subtitle">ResEnt Sapiens · CIEL/Ω · Projekty · {now}</div>
</header>
{_nav_html_projects()}
<main>{body}</main>
<footer>CIEL/Ω · closure_penalty={closure_str} · R_H={rh_str}</footer>
</body>
</html>"""
    (proj_dir / "index.html").write_text(html, encoding="utf-8")


def _nav_html_projects() -> str:
    """Nav for projects/ subdirectory (paths relative to projects/)."""
    pages = [
        ("../index.html", "Dashboard"),
        ("../memory.html", "Pamięć"),
        ("../cards.html", "Karty Obiektów"),
        ("../diary.html", "Dziennik"),
        ("index.html", "Projekty"),
    ]
    links = "".join(
        f'<a href="{href}"{"" if label != "Projekty" else " class=\"active\""}'
        f'>{label}</a>\n  '
        for href, label in pages
    )
    return f'<nav>\n  {links}</nav>'


def generate():
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    # Write shared CSS
    (SITE_DIR / "style.css").write_text(CSS, encoding="utf-8")

    # Load all data
    mf = load_mindflow()
    intentions = load_intentions()
    entity_cards = load_entity_cards()
    final = load_orbital_final()
    entity_metrics = load_entity_orbital()
    cache_entries = load_cache_entries()
    diary_entries = load_diary_entries()
    wpm_memories = load_wpm_memories()
    project_memory = load_project_memory()
    object_cards = load_object_cards()
    pipeline_report = load_pipeline_report()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # index.html — dashboard
    index_body = (
        section_identity(mf, final)
        + section_ciel_omega(pipeline_report)
        + section_mindflow(mf)
        + section_entities(entity_cards, entity_metrics)
        + section_intentions(intentions)
        + section_diary(diary_entries)
        + section_wpm(wpm_memories)
        + section_log(cache_entries)
    )
    _sec_nav = (
        '<a href="#identity">Tożsamość</a>'
        '<a href="#mindflow">Przemyślenia</a>'
        '<a href="#entities">Relacyjna</a>'
        '<a href="#intentions">Agenda</a>'
        '<a href="#diary">Dziennik</a>'
        '<a href="#wpm">WPM</a>'
        '<a href="#log">Log</a>'
    )
    (SITE_DIR / "hub.html").write_text(
        _page("Dashboard", "index", index_body, now, final, secondary_nav=_sec_nav),
        encoding="utf-8",
    )

    # memory.html — project memory files
    (SITE_DIR / "memory.html").write_text(
        _page("Pamięć Projektu", "memory", section_project_memory(project_memory), now, final),
        encoding="utf-8",
    )

    # cards.html — object cards with relations
    (SITE_DIR / "cards.html").write_text(
        _page("Karty Obiektów", "cards", section_cards(object_cards), now, final),
        encoding="utf-8",
    )

    # diary.html — full diary (all entries, no limit)
    (SITE_DIR / "diary.html").write_text(
        _page("Dziennik", "diary", section_diary_full(diary_entries), now, final),
        encoding="utf-8",
    )

    # projects/index.html — scan projects directory, build index
    _generate_projects_index(SITE_DIR, now, final)

    generated = ["style.css", "hub.html", "memory.html", "cards.html", "diary.html", "projects/index.html"]
    for fname in generated:
        print(f"Wygenerowano: {SITE_DIR / fname}")
    return str(SITE_DIR / "hub.html")


if __name__ == "__main__":
    generate()
