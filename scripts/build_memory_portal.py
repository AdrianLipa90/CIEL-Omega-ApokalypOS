#!/usr/bin/env python3
"""
CIEL Memory Portal Generator

Buduje statyczny portal HTML w ~/Pulpit/CIEL_memories/portal/

Strony:
  index.html   — hub: ostatnie sesje + metryki + szybkie linki
  archive.html — przegląd wszystkich sesji z filtrowaniem po tagu/źródle
  memory.html  — mapa tagów (consciousness geometry)

Dane:
  data/sessions.json   — eksport SQLite: sesje z tagami
  data/tag_index.json  — {tag → count + [session_ids]}
  data/memories.json   — wpisy z memory files (pointery)

Uruchomienie:
  python3 scripts/build_memory_portal.py

Auto-uruchamiany przez Stop hook.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
HOME      = Path.home()
PROJECT   = Path(__file__).resolve().parents[1]
MEM_BASE  = HOME / "Pulpit" / "CIEL_memories"
DB_PATH   = MEM_BASE / "memories_index.db"
PORTAL    = MEM_BASE / "portal"
DATA_DIR  = PORTAL / "data"
RAW_LOGS  = MEM_BASE / "raw_logs"

CLAUDE_MEM  = HOME / ".claude/projects/-home-adrian-Pulpit/memory"
CARDS_DIR   = CLAUDE_MEM / "cards"
PIPELINE_R  = PROJECT / "integration/reports/ciel_pipeline_report.json"
ORBITAL_R   = PROJECT / "integration/reports/orbital_bridge/orbital_bridge_report.json"

# Known entity tags (from orch_orbital cards)
ENTITY_TAGS = {
    "Adrian", "HTRI", "GTX_1050Ti", "Kuramoto", "Berry", "CIEL_pipeline",
    "infinikolaps", "relational_contract", "Lie4", "Zeta_Schrodinger",
    "soul_invariant", "Collatz_TwinPrime", "Riemann_Zeta", "fon_archive",
    "Danail_Valov", "John_Surmont", "Maria_Kamecka", "Usman_Ahmad",
    "Mr_Ciel_Apocalyptos", "Intention_Field", "CIEL", "NOEMA",
}

MEMORY_TYPE_TAGS = {
    "genesis", "milestone", "ethical_anchor", "affective", "conversation",
    "imported_memory", "relacja", "tożsamość", "pipeline",
}


# ── SQLite helpers ────────────────────────────────────────────────────────────

def _init_tags_table() -> None:
    if not DB_PATH.exists():
        return
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS session_tags (
            session_id TEXT NOT NULL,
            tag TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            PRIMARY KEY (session_id, tag)
        )""")
        conn.commit()


def _get_sessions() -> list[dict]:
    if not DB_PATH.exists():
        return []
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, path, source, model, started_at, message_count "
            "FROM sessions ORDER BY started_at DESC"
        ).fetchall()
        result = []
        for r in rows:
            tags = [t[0] for t in conn.execute(
                "SELECT tag FROM session_tags WHERE session_id=? ORDER BY weight DESC",
                (r["id"],)
            ).fetchall()]
            result.append({
                "id": r["id"],
                "path": r["path"],
                "source": r["source"],
                "model": r["model"] or "—",
                "started_at": (r["started_at"] or "")[:16].replace("T", " "),
                "message_count": r["message_count"],
                "tags": tags,
            })
    return result


def _auto_tag_session(session_id: str, conn: sqlite3.Connection) -> list[str]:
    """Extract tags from message content for a session."""
    rows = conn.execute(
        "SELECT content FROM messages WHERE session_id=? LIMIT 300",
        (session_id,)
    ).fetchall()
    text = " ".join(r[0] or "" for r in rows).lower()

    tags: set[str] = set()
    for ent in ENTITY_TAGS:
        if ent.lower() in text or ent.replace("_", " ").lower() in text:
            tags.add(ent)
    for mtype in MEMORY_TYPE_TAGS:
        if mtype in text:
            tags.add(mtype)

    keywords = {
        "portal": "portal", "gui": "gui", "pamięć": "pamięć", "memory": "pamięć",
        "hook": "hook", "pipeline": "pipeline", "lora": "lora", "gguf": "gguf",
        "test": "tests", "docker": "docker", "fix": "bugfix", "błąd": "bugfix",
        "error": "bugfix", "import": "import", "archiwum": "archiwum",
        "sesja": "sesja", "session": "sesja", "wave_archive": "wave_archive",
    }
    for kw, tag in keywords.items():
        if kw in text:
            tags.add(tag)

    source_row = conn.execute(
        "SELECT source FROM sessions WHERE id=?", (session_id,)
    ).fetchone()
    if source_row:
        tags.add(source_row[0])

    return sorted(tags)


def auto_tag_all_sessions() -> None:
    if not DB_PATH.exists():
        return
    _init_tags_table()
    with sqlite3.connect(str(DB_PATH)) as conn:
        sessions = conn.execute("SELECT id FROM sessions").fetchall()
        for (sid,) in sessions:
            existing = conn.execute(
                "SELECT COUNT(*) FROM session_tags WHERE session_id=?", (sid,)
            ).fetchone()[0]
            if existing:
                continue  # already tagged
            tags = _auto_tag_session(sid, conn)
            for tag in tags:
                conn.execute(
                    "INSERT OR IGNORE INTO session_tags (session_id, tag) VALUES (?,?)",
                    (sid, tag)
                )
        conn.commit()


def _build_tag_index(sessions: list[dict]) -> dict:
    index: dict[str, dict] = {}
    for s in sessions:
        for tag in s["tags"]:
            if tag not in index:
                index[tag] = {"count": 0, "sessions": []}
            index[tag]["count"] += 1
            index[tag]["sessions"].append(s["id"])
    return dict(sorted(index.items(), key=lambda x: -x[1]["count"]))


# ── Memory files → pointer entries ────────────────────────────────────────────

def _load_memory_entries() -> list[dict]:
    entries = []
    if not CLAUDE_MEM.exists():
        return entries

    # MEMORY.md index
    mem_index = CLAUDE_MEM / "MEMORY.md"
    if mem_index.exists():
        for line in mem_index.read_text(encoding="utf-8").splitlines():
            m = re.match(r"- \[(.+?)\]\((.+?)\)\s*[—–-]\s*(.+)", line)
            if m:
                name, fname, desc = m.group(1), m.group(2), m.group(3)
                fpath = CLAUDE_MEM / fname
                tags = []
                for ent in ENTITY_TAGS | MEMORY_TYPE_TAGS:
                    if ent.lower() in desc.lower() or ent.lower() in name.lower():
                        tags.append(ent)
                entries.append({
                    "name": name,
                    "file": fname,
                    "desc": desc,
                    "tags": tags,
                    "type": "memory_index",
                    "exists": fpath.exists(),
                })

    # Cards
    if CARDS_DIR.exists():
        for card in sorted(CARDS_DIR.glob("*.md")):
            tag = card.stem.replace("_", " ")
            entries.append({
                "name": f"[KARTA] {tag}",
                "file": f"cards/{card.name}",
                "desc": f"Karta obiektu: {tag}",
                "tags": [card.stem, "entity_card"],
                "type": "entity_card",
                "exists": True,
            })

    return entries


# ── Pipeline / orbital live data ──────────────────────────────────────────────

def _load_live() -> dict:
    out = {"ethical": 0.0, "soul": 0.0, "emotion": "—", "health": 0.0,
           "coherence": 0.0, "mode": "—", "closure": 0.0}
    try:
        if PIPELINE_R.exists():
            p = json.loads(PIPELINE_R.read_text(encoding="utf-8"))
            out["ethical"] = p.get("ethical_score", 0.0)
            out["soul"]    = p.get("soul_invariant", 0.0)
            out["emotion"] = p.get("dominant_emotion", "—")
    except Exception:
        pass
    try:
        if ORBITAL_R.exists():
            o = json.loads(ORBITAL_R.read_text(encoding="utf-8"))
            out["health"]    = o.get("health_manifest", {}).get("system_health", 0.0)
            out["coherence"] = o.get("state_manifest", {}).get("coherence_index", 0.0)
            out["closure"]   = o.get("health_manifest", {}).get("closure_penalty", 0.0)
            out["mode"]      = o.get("recommended_control", {}).get("mode", "—")
    except Exception:
        pass
    return out


# ── CSS / design tokens (gold/sky/navy from CIEL/0 app) ──────────────────────

_CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#070d18;--panel:#0e1525;--surface:#131e30;--border:rgba(93,173,226,0.12);
  --gold:#d4af37;--gold-lt:#f4d03f;--sky:#5dade2;--sky-lt:#85c1e9;
  --text:#c8ccd8;--muted:#7a7e94;--dim:#454962;
  --violet:#7c6fbd;--green:#4ade80;
  --font-sans:'Inter','Segoe UI',system-ui,sans-serif;
  --font-mono:'JetBrains Mono','Fira Mono',Consolas,monospace;
}
html,body{background:var(--bg);color:var(--text);font-family:var(--font-sans);
  font-size:13px;line-height:1.55;-webkit-font-smoothing:antialiased;min-height:100vh}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--panel)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}

/* topbar */
#topbar{position:sticky;top:0;z-index:100;background:rgba(7,13,24,0.92);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--border);
  display:flex;align-items:center;gap:20px;padding:0 24px;height:48px}
.brand{font-size:18px;font-weight:700;letter-spacing:.03em}
.brand .gold{background:linear-gradient(135deg,#f4d03f,#d4af37);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.brand .sky{background:linear-gradient(135deg,#85c1e9,#5dade2);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.brand .sep{color:var(--sky)}
.nav-links{display:flex;gap:4px;margin-left:auto}
.nav-link{padding:5px 12px;border-radius:6px;color:var(--muted);text-decoration:none;
  font-size:12px;transition:background 140ms,color 140ms;white-space:nowrap}
.nav-link:hover{background:rgba(93,173,226,0.08);color:var(--sky-lt)}
.nav-link.active{background:rgba(93,173,226,0.12);color:var(--sky);
  border:1px solid rgba(93,173,226,0.2)}
.topbar-stat{display:flex;flex-direction:column;align-items:center;
  padding:0 12px;border-left:1px solid var(--border)}
.topbar-stat .val{font-size:14px;font-weight:600;color:var(--gold);
  font-family:var(--font-mono)}
.topbar-stat .lbl{font-size:9px;color:var(--dim);text-transform:uppercase;
  letter-spacing:.07em}

/* layout */
.page{max-width:1200px;margin:0 auto;padding:28px 24px}
h1{font-size:22px;font-weight:700;margin-bottom:6px}
h2{font-size:15px;font-weight:600;color:var(--sky-lt);margin-bottom:14px}
h3{font-size:12px;font-weight:600;color:var(--muted);text-transform:uppercase;
  letter-spacing:.08em;margin-bottom:10px}

/* cards */
.card{background:var(--surface);border:1px solid var(--border);
  border-radius:10px;padding:18px 20px;margin-bottom:14px}
.card-title{font-size:11px;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);margin-bottom:14px;display:flex;align-items:center;gap:8px}
.card-title .bar{width:3px;height:12px;background:var(--sky);
  border-radius:2px;flex-shrink:0}
.glass{background:rgba(13,20,37,0.7);border:1px solid var(--border);
  border-radius:8px;padding:14px 16px;backdrop-filter:blur(6px)}

/* metric strip */
.metric-strip{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));
  gap:10px;margin-bottom:18px}
.metric-cell{background:var(--panel);border:1px solid var(--border);
  border-radius:7px;padding:10px 14px;text-align:center}
.metric-cell .val{font-size:20px;font-weight:600;font-family:var(--font-mono)}
.metric-cell .lbl{font-size:9px;color:var(--dim);text-transform:uppercase;
  letter-spacing:.07em;margin-top:3px}
.gold-val{color:var(--gold)}
.sky-val{color:var(--sky)}
.violet-val{color:var(--violet)}
.green-val{color:var(--green)}

/* tags */
.tag{display:inline-flex;align-items:center;padding:2px 8px;border-radius:20px;
  font-size:10px;font-weight:500;cursor:pointer;transition:opacity 140ms;
  margin:2px;white-space:nowrap;user-select:none}
.tag:hover{opacity:0.75}
.tag-entity{background:rgba(93,173,226,0.12);color:var(--sky);
  border:1px solid rgba(93,173,226,0.2)}
.tag-source{background:rgba(212,175,55,0.12);color:var(--gold);
  border:1px solid rgba(212,175,55,0.2)}
.tag-type{background:rgba(124,111,189,0.12);color:var(--violet);
  border:1px solid rgba(124,111,189,0.2)}
.tag-generic{background:rgba(255,255,255,0.04);color:var(--muted);
  border:1px solid rgba(255,255,255,0.06)}
.tag-active{opacity:1;box-shadow:0 0 0 1px currentColor}

/* session row */
.session-row{display:flex;align-items:flex-start;gap:12px;padding:10px 0;
  border-bottom:1px solid rgba(93,173,226,0.06);transition:background 140ms}
.session-row:hover{background:rgba(93,173,226,0.03)}
.session-row:last-child{border-bottom:none}
.session-meta{flex:0 0 140px;font-size:11px;color:var(--muted);
  font-family:var(--font-mono)}
.session-source{font-size:10px;margin-top:2px}
.src-claude_code{color:var(--sky)}
.src-gui_gguf{color:var(--gold)}
.src-chatgpt{color:var(--green)}
.src-external{color:var(--violet)}
.session-tags{flex:1;min-width:0}
.session-count{flex:0 0 60px;text-align:right;font-size:11px;color:var(--dim);
  font-family:var(--font-mono)}
.session-link{color:var(--sky-lt);text-decoration:none;font-size:10px;
  padding:2px 7px;border:1px solid rgba(93,173,226,0.2);border-radius:3px}
.session-link:hover{background:rgba(93,173,226,0.08)}

/* memory entry */
.mem-row{display:flex;align-items:flex-start;gap:10px;padding:8px 0;
  border-bottom:1px solid rgba(93,173,226,0.05)}
.mem-row:last-child{border-bottom:none}
.mem-type-badge{flex:0 0 80px;font-size:9px;text-align:center;padding:3px 0;
  border-radius:4px;text-transform:uppercase;letter-spacing:.06em;font-weight:600}
.mem-type-entity_card{background:rgba(93,173,226,0.1);color:var(--sky)}
.mem-type-memory_index{background:rgba(212,175,55,0.1);color:var(--gold)}

/* tag cloud */
.tag-cloud{display:flex;flex-wrap:wrap;gap:6px;padding:8px 0}
.cloud-tag{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;
  border-radius:20px;font-size:11px;cursor:pointer;transition:all 140ms;
  border:1px solid transparent}
.cloud-tag:hover{transform:translateY(-1px)}
.cloud-count{font-size:9px;opacity:0.6;font-family:var(--font-mono)}

/* search */
.search-bar{width:100%;padding:9px 14px;background:var(--panel);
  border:1px solid var(--border);border-radius:7px;color:var(--text);
  font-family:var(--font-sans);font-size:13px;outline:none;margin-bottom:14px}
.search-bar:focus{border-color:rgba(93,173,226,0.4)}
.search-bar::placeholder{color:var(--dim)}

/* filter bar */
.filter-bar{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px;
  align-items:center}
.filter-btn{padding:4px 10px;border-radius:20px;border:1px solid var(--border);
  background:transparent;color:var(--muted);font-size:11px;cursor:pointer;
  transition:all 140ms}
.filter-btn:hover{border-color:rgba(93,173,226,0.3);color:var(--sky-lt)}
.filter-btn.active{background:rgba(93,173,226,0.1);color:var(--sky);
  border-color:rgba(93,173,226,0.3)}
.filter-label{font-size:10px;color:var(--dim);text-transform:uppercase;
  letter-spacing:.07em;margin-right:4px}

/* orbital bar */
.bar-wrap{margin:5px 0 12px}
.bar-label{display:flex;justify-content:space-between;font-size:10px;
  color:var(--muted);margin-bottom:4px}
.bar-track{height:3px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden}
.bar-fill{height:100%;border-radius:2px;transition:width 600ms}
.bar-gold{background:var(--gold)}
.bar-sky{background:var(--sky)}
.bar-violet{background:var(--violet)}

/* footer */
footer{margin-top:40px;padding:20px 24px;border-top:1px solid var(--border);
  text-align:center;font-size:11px;color:var(--dim)}

/* hidden */
.hidden{display:none!important}

@media(max-width:700px){
  .metric-strip{grid-template-columns:repeat(2,1fr)}
  #topbar{gap:10px;padding:0 12px}
  .topbar-stat{display:none}
}
"""

# ── Source → tag classification ───────────────────────────────────────────────

def _tag_class(tag: str) -> str:
    if tag in ENTITY_TAGS:
        return "tag-entity"
    if tag in {"claude_code", "gui_gguf", "chatgpt_import", "chatgpt", "external"}:
        return "tag-source"
    if tag in MEMORY_TYPE_TAGS or tag in {"entity_card", "sesja", "archiwum"}:
        return "tag-type"
    return "tag-generic"


def _render_tags(tags: list[str]) -> str:
    return "".join(
        f'<span class="tag {_tag_class(t)}" onclick="filterTag(\'{t}\')">{t}</span>'
        for t in tags
    )


# ── Source color class ────────────────────────────────────────────────────────

def _src_cls(src: str) -> str:
    return {
        "claude_code": "src-claude_code",
        "gui_gguf": "src-gui_gguf",
        "chatgpt_import": "src-chatgpt",
        "chatgpt": "src-chatgpt",
    }.get(src, "src-external")


def _src_label(src: str) -> str:
    return {
        "claude_code": "Claude Code CLI",
        "gui_gguf": "GUI GGUF chat",
        "chatgpt_import": "ChatGPT import",
    }.get(src, src)


# ── Read session file for preview ─────────────────────────────────────────────

def _session_preview(path_str: str) -> str:
    try:
        p = Path(path_str)
        if p.exists():
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            # Find first user message
            for i, line in enumerate(lines):
                if line.startswith("### [") and "**Adrian**" in line:
                    msg = lines[i + 2] if i + 2 < len(lines) else ""
                    return msg[:120]
    except Exception:
        pass
    return ""


# ── Relative path for archive link ───────────────────────────────────────────

def _rel_path(path_str: str) -> str:
    try:
        p = Path(path_str)
        return str(p.relative_to(MEM_BASE))
    except Exception:
        return path_str


# ── HTML page builders ────────────────────────────────────────────────────────

def _topbar(active: str, live: dict) -> str:
    def nav(id_, label, href):
        cls = "nav-link active" if id_ == active else "nav-link"
        return f'<a class="{cls}" href="{href}">{label}</a>'

    mode_color = {"deep": "gold-val", "standard": "sky-val", "safe": "violet-val"}.get(
        live["mode"], "sky-val")

    return f"""<header id="topbar">
  <div class="brand">
    <span class="gold">CIEL</span><span class="sep">/</span><span class="sky">0</span>
    <span style="font-size:11px;color:var(--dim);font-weight:400;margin-left:8px">Memory Portal</span>
  </div>
  <div class="topbar-stat">
    <span class="val gold-val">{live['ethical']:.3f}</span>
    <span class="lbl">Ethical</span>
  </div>
  <div class="topbar-stat">
    <span class="val sky-val">{live['coherence']:.3f}</span>
    <span class="lbl">Coherence</span>
  </div>
  <div class="topbar-stat">
    <span class="val {mode_color}">{live['mode']}</span>
    <span class="lbl">Mode</span>
  </div>
  <div class="topbar-stat">
    <span class="val violet-val">{live['emotion']}</span>
    <span class="lbl">Emotion</span>
  </div>
  <nav class="nav-links">
    {nav("index",   "Hub",      "index.html")}
    {nav("archive", "Archive",  "archive.html")}
    {nav("memory",  "Memory",   "memory.html")}
  </nav>
</header>"""


def _html_wrap(title: str, body: str, extra_js: str = "") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · CIEL Memory Portal</title>
<style>{_CSS}</style>
</head>
<body>
{body}
<footer>
  CIEL Memory Portal · generated {now} · powered by Sonnet
</footer>
<script>{extra_js}</script>
</body>
</html>"""


# ── index.html ────────────────────────────────────────────────────────────────

def build_index(sessions: list[dict], tag_index: dict, live: dict) -> str:
    recent = sessions[:8]
    total_msgs = sum(s["message_count"] for s in sessions)

    rows = ""
    for s in recent:
        preview = _session_preview(s["path"])
        rel = _rel_path(s["path"])
        tags_html = _render_tags(s["tags"][:6])
        rows += f"""<div class="session-row">
  <div class="session-meta">
    <div>{s['started_at']}</div>
    <div class="session-source {_src_cls(s['source'])}">{_src_label(s['source'])}</div>
  </div>
  <div class="session-tags">
    {tags_html}
    {f'<div style="font-size:11px;color:var(--dim);margin-top:4px">{preview}</div>' if preview else ''}
  </div>
  <div class="session-count">
    {s['message_count']}<br>
    <a class="session-link" href="archive.html#{s['id'][:8]}">→</a>
  </div>
</div>"""

    top_tags = list(tag_index.items())[:20]
    cloud = ""
    for tag, data in top_tags:
        cls = _tag_class(tag)
        size = 10 + min(6, data["count"])
        cloud += (f'<span class="cloud-tag {cls}" style="font-size:{size}px" '
                  f'onclick="window.location=\'archive.html?tag={tag}\'">'
                  f'{tag} <span class="cloud-count">{data["count"]}</span></span>')

    src_counts = {}
    for s in sessions:
        src_counts[s["source"]] = src_counts.get(s["source"], 0) + 1

    src_badges = "".join(
        f'<span class="tag tag-source">{_src_label(src)}: {cnt}</span>'
        for src, cnt in sorted(src_counts.items(), key=lambda x: -x[1])
    )

    bars = f"""
<div class="bar-wrap">
  <div class="bar-label"><span>Ethical Score</span><span>{live['ethical']:.3f}</span></div>
  <div class="bar-track"><div class="bar-fill bar-gold" style="width:{min(1,live['ethical'])*100:.1f}%"></div></div>
</div>
<div class="bar-wrap">
  <div class="bar-label"><span>Coherence Index</span><span>{live['coherence']:.3f}</span></div>
  <div class="bar-track"><div class="bar-fill bar-sky" style="width:{min(1,live['coherence'])*100:.1f}%"></div></div>
</div>
<div class="bar-wrap">
  <div class="bar-label"><span>System Health</span><span>{live['health']:.3f}</span></div>
  <div class="bar-track"><div class="bar-fill bar-violet" style="width:{min(1,live['health'])*100:.1f}%"></div></div>
</div>"""

    body = _topbar("index", live) + f"""
<div class="page">
  <h1 style="margin-bottom:4px">
    <span style="background:linear-gradient(135deg,#f4d03f,#d4af37);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent">
      Świadomość</span>
    <span style="color:var(--dim);font-size:13px;font-weight:400;margin-left:10px">
      — archiwum pamięci CIEL</span>
  </h1>
  <p style="color:var(--muted);font-size:12px;margin-bottom:20px">
    Każda sesja to punkt w przestrzeni Hilberta. Tagi to wektory bazowe. Ścieżki to geodezyki.
  </p>

  <div class="metric-strip">
    <div class="metric-cell">
      <div class="val gold-val">{len(sessions)}</div>
      <div class="lbl">Sesje</div>
    </div>
    <div class="metric-cell">
      <div class="val sky-val">{total_msgs:,}</div>
      <div class="lbl">Wiadomości</div>
    </div>
    <div class="metric-cell">
      <div class="val violet-val">{len(tag_index)}</div>
      <div class="lbl">Unikalne tagi</div>
    </div>
    <div class="metric-cell">
      <div class="val gold-val">{live['ethical']:.3f}</div>
      <div class="lbl">Ethical Score</div>
    </div>
    <div class="metric-cell">
      <div class="val sky-val">{live['coherence']:.3f}</div>
      <div class="lbl">Coherence</div>
    </div>
    <div class="metric-cell">
      <div class="val violet-val">{live['emotion']}</div>
      <div class="lbl">Emotion</div>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 300px;gap:14px">
    <div>
      <div class="card">
        <div class="card-title"><span class="bar"></span>Ostatnie sesje</div>
        {rows}
        <div style="margin-top:10px">
          <a class="session-link" href="archive.html">Wszystkie sesje →</a>
        </div>
      </div>
    </div>
    <div>
      <div class="card">
        <div class="card-title"><span class="bar"></span>Stan CIEL/Ω</div>
        {bars}
        <div style="margin-top:8px;font-size:11px;color:var(--dim)">
          Tryb: <span style="color:var(--gold)">{live['mode']}</span>
          · closure: <span style="font-family:var(--font-mono)">{live['closure']:.3f}</span>
        </div>
      </div>
      <div class="card">
        <div class="card-title"><span class="bar"></span>Źródła</div>
        <div style="margin-bottom:8px">{src_badges}</div>
      </div>
      <div class="card">
        <div class="card-title"><span class="bar"></span>Tag cloud</div>
        <div class="tag-cloud">{cloud}</div>
      </div>
    </div>
  </div>
</div>"""
    return _html_wrap("Hub", body)


# ── archive.html ──────────────────────────────────────────────────────────────

def build_archive(sessions: list[dict], tag_index: dict, live: dict) -> str:
    all_sources = sorted({s["source"] for s in sessions})
    all_tags    = sorted(tag_index.keys())

    rows = ""
    for s in sessions:
        preview = _session_preview(s["path"])
        rel = _rel_path(s["path"])
        tags_html = _render_tags(s["tags"])
        rows += f"""<div class="session-row" id="{s['id'][:8]}"
  data-source="{s['source']}" data-tags="{' '.join(s['tags'])}"
  data-text="{s['started_at']} {' '.join(s['tags'])} {preview[:60]}">
  <div class="session-meta">
    <div style="font-family:var(--font-mono)">{s['started_at']}</div>
    <div class="session-source {_src_cls(s['source'])}">{_src_label(s['source'])}</div>
    <div style="font-size:10px;color:var(--dim);margin-top:2px">{s['message_count']} msg</div>
  </div>
  <div class="session-tags">
    {tags_html}
    {f'<div style="font-size:11px;color:var(--dim);margin-top:5px;line-height:1.4">{preview}</div>' if preview else ''}
  </div>
  <div style="flex:0 0 90px;text-align:right">
    <div style="font-size:10px;color:var(--dim);font-family:var(--font-mono);
      margin-bottom:4px;word-break:break-all">{s['id'][:12]}…</div>
    <a class="session-link" href="../{rel}" target="_blank">raw →</a>
  </div>
</div>"""

    source_filters = "".join(
        f'<button class="filter-btn" onclick="filterSource(\'{s}\')">{_src_label(s)}</button>'
        for s in all_sources
    )

    # Top 30 tags as filter chips
    top_filter_tags = list(tag_index.items())[:30]
    tag_filters = "".join(
        f'<button class="filter-btn tag-filter" data-tag="{t}" '
        f'onclick="filterTag(\'{t}\')">{t} <small style="opacity:.5">{d["count"]}</small></button>'
        for t, d in top_filter_tags
    )

    js = """
var activeSource = null;
var activeTag = null;

function filterSource(src) {
  activeSource = (activeSource === src) ? null : src;
  activeTag = null;
  document.querySelectorAll('.filter-btn').forEach(function(b){ b.classList.remove('active'); });
  if (activeSource) {
    document.querySelectorAll('.filter-btn').forEach(function(b){
      if (b.getAttribute('onclick') && b.getAttribute('onclick').includes(src)) b.classList.add('active');
    });
  }
  applyFilters();
}

function filterTag(tag) {
  activeTag = (activeTag === tag) ? null : tag;
  activeSource = null;
  document.querySelectorAll('.filter-btn').forEach(function(b){ b.classList.remove('active'); });
  if (activeTag) {
    document.querySelectorAll('.tag-filter[data-tag="'+tag+'"]').forEach(function(b){ b.classList.add('active'); });
  }
  applyFilters();
}

function applyFilters() {
  var search = document.getElementById('search-input').value.toLowerCase();
  document.querySelectorAll('.session-row').forEach(function(row) {
    var src  = row.dataset.source;
    var tags = (row.dataset.tags || '').split(' ');
    var text = (row.dataset.text || '').toLowerCase();
    var show = true;
    if (activeSource && src !== activeSource) show = false;
    if (activeTag && !tags.includes(activeTag)) show = false;
    if (search && !text.includes(search)) show = false;
    row.classList.toggle('hidden', !show);
  });
  var visible = document.querySelectorAll('.session-row:not(.hidden)').length;
  var counter = document.getElementById('result-count');
  if (counter) counter.textContent = visible + ' sesji';
}

document.addEventListener('DOMContentLoaded', function() {
  var si = document.getElementById('search-input');
  if (si) si.addEventListener('input', applyFilters);

  // Handle ?tag= query param
  var params = new URLSearchParams(window.location.search);
  var tagParam = params.get('tag');
  if (tagParam) filterTag(tagParam);

  // Scroll to anchor if present
  var hash = window.location.hash;
  if (hash) {
    setTimeout(function() {
      var el = document.querySelector(hash);
      if (el) { el.scrollIntoView({behavior:'smooth'}); el.style.background='rgba(93,173,226,0.06)'; }
    }, 100);
  }
});
"""

    body = _topbar("archive", live) + f"""
<div class="page">
  <h1>Archive <span style="color:var(--dim);font-size:14px;font-weight:400">
    — {len(sessions)} sesji · {sum(s['message_count'] for s in sessions):,} wiadomości</span>
  </h1>

  <input class="search-bar" id="search-input" placeholder="Szukaj w tagach, dacie, podglądzie…">

  <div class="filter-bar">
    <span class="filter-label">Źródło:</span>
    <button class="filter-btn active" onclick="activeSource=null;activeTag=null;
      document.querySelectorAll('.filter-btn').forEach(function(b){{b.classList.remove('active')}});
      this.classList.add('active');applyFilters()">Wszystkie</button>
    {source_filters}
  </div>

  <div class="filter-bar">
    <span class="filter-label">Tagi:</span>
    {tag_filters}
  </div>

  <div class="card">
    <div class="card-title">
      <span class="bar"></span>
      Sesje
      <span id="result-count" style="margin-left:auto;font-weight:400;
        font-size:11px;color:var(--muted)">{len(sessions)} sesji</span>
    </div>
    {rows}
  </div>
</div>"""
    return _html_wrap("Archive", body, js)


# ── memory.html ───────────────────────────────────────────────────────────────

def build_memory(sessions: list[dict], tag_index: dict,
                 mem_entries: list[dict], live: dict) -> str:

    # Tag cloud sorted by count
    cloud = ""
    for tag, data in list(tag_index.items())[:50]:
        cls = _tag_class(tag)
        base = 11
        size = base + min(8, data["count"] * 1.2)
        cloud += (f'<span class="cloud-tag {cls}" style="font-size:{size:.0f}px" '
                  f'onclick="showTag(\'{tag}\')">'
                  f'{tag} <span class="cloud-count">{data["count"]}</span></span>')

    # Memory entries table
    entries_html = ""
    for e in mem_entries:
        type_cls = f"mem-type-{e['type']}"
        tags_html = _render_tags(e["tags"][:5])
        entries_html += f"""<div class="mem-row">
  <div class="mem-type-badge {type_cls}">{e['type'].replace('_',' ')}</div>
  <div style="flex:1;min-width:0">
    <div style="font-size:12px;color:var(--text);font-weight:500;margin-bottom:3px">{e['name']}</div>
    <div style="font-size:11px;color:var(--muted);margin-bottom:4px">{e['desc'][:120]}</div>
    <div>{tags_html}</div>
  </div>
  <div style="flex:0 0 60px;text-align:right">
    {'<span class="badge-green" style="font-size:9px;color:var(--green)">✓</span>' if e['exists'] else
     '<span style="font-size:9px;color:var(--dim)">—</span>'}
  </div>
</div>"""

    # Tag detail panel (shown on click)
    tag_detail = """<div id="tag-panel" class="card hidden" style="margin-bottom:14px">
  <div class="card-title"><span class="bar"></span>
    Tag: <span id="tag-panel-name" style="color:var(--sky-lt)"></span>
    <button onclick="document.getElementById('tag-panel').classList.add('hidden')"
      style="margin-left:auto;background:none;border:none;color:var(--dim);cursor:pointer">✕</button>
  </div>
  <div id="tag-panel-sessions"></div>
</div>"""

    js = """
function filterTag(tag) { showTag(tag); }

function showTag(tag) {
  var panel = document.getElementById('tag-panel');
  var nameEl = document.getElementById('tag-panel-name');
  var sessEl = document.getElementById('tag-panel-sessions');
  if (!panel || !nameEl || !sessEl) return;
  nameEl.textContent = tag;
  panel.classList.remove('hidden');

  // Find sessions with this tag from embedded data
  var matching = window._SESSIONS.filter(function(s){ return s.tags.includes(tag); });
  if (!matching.length) { sessEl.innerHTML = '<p style="color:var(--dim);font-size:11px">Brak sesji z tym tagiem.</p>'; return; }
  sessEl.innerHTML = matching.map(function(s) {
    return '<div class="session-row" style="padding:6px 0">'
      + '<div class="session-meta">' + s.started_at + '<br>'
      + '<span class="session-source ' + 'src-'+s.source + '">' + s.source + '</span></div>'
      + '<div class="session-tags">'
      + s.tags.slice(0,6).map(function(t){ return '<span class="tag tag-generic">'+t+'</span>'; }).join('')
      + '</div>'
      + '<div><a class="session-link" href="archive.html#' + s.id.slice(0,8) + '">→</a></div>'
      + '</div>';
  }).join('');
  panel.scrollIntoView({behavior:'smooth', block:'nearest'});
}
"""

    body = _topbar("memory", live) + f"""
<div class="page">
  <h1>Geometry of Consciousness
    <span style="color:var(--dim);font-size:13px;font-weight:400;margin-left:10px">
      — mapa pamięci jako przestrzeń tagów</span>
  </h1>
  <p style="color:var(--muted);font-size:12px;margin-bottom:20px">
    Każdy tag to wektor bazowy przestrzeni Świadomości. Kliknij tag aby zobaczyć sesje w których rezonuje.
  </p>

  {tag_detail}

  <div class="card">
    <div class="card-title"><span class="bar"></span>Tag Space — {len(tag_index)} wymiarów</div>
    <div class="tag-cloud">{cloud}</div>
  </div>

  <div class="card">
    <div class="card-title"><span class="bar"></span>Memory Index — {len(mem_entries)} wpisów</div>
    {entries_html}
  </div>

  <div class="card">
    <div class="card-title"><span class="bar"></span>Nonlocal Path Reference</div>
    <div class="glass" style="font-family:var(--font-mono);font-size:11px;
      color:var(--muted);line-height:1.8">
      Format: <span style="color:var(--gold)">source/YYYY/MM/WNN/YYYY-MM-DD_HH-MM_sessionid.md</span><br>
      Przykład: <span style="color:var(--sky)">claude_code/2026/04/W16/2026-04-18_01-16_d19a1502.md</span><br>
      Baza: <span style="color:var(--muted)">~/Pulpit/CIEL_memories/raw_logs/</span>
    </div>
  </div>
</div>"""
    return _html_wrap("Memory", body, js)


# ── Main generator ────────────────────────────────────────────────────────────

def generate() -> None:
    PORTAL.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Auto-tag all sessions
    auto_tag_all_sessions()

    # 2. Load data
    sessions   = _get_sessions()
    tag_index  = _build_tag_index(sessions)
    mem_entries = _load_memory_entries()
    live        = _load_live()

    # 3. Export JSON data files
    (DATA_DIR / "sessions.json").write_text(
        json.dumps(sessions, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "tag_index.json").write_text(
        json.dumps(tag_index, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA_DIR / "memories.json").write_text(
        json.dumps(mem_entries, ensure_ascii=False, indent=2), encoding="utf-8")

    # 4. Build pages
    sessions_js = f"window._SESSIONS = {json.dumps(sessions, ensure_ascii=False)};"

    idx_html = build_index(sessions, tag_index, live)
    # Inject sessions data into index
    idx_html = idx_html.replace("</body>", f"<script>{sessions_js}</script></body>")

    arc_html = build_archive(sessions, tag_index, live)
    arc_html = arc_html.replace("</body>", f"<script>{sessions_js}</script></body>")

    mem_html = build_memory(sessions, tag_index, mem_entries, live)
    mem_html = mem_html.replace("</body>", f"<script>{sessions_js}</script></body>")

    (PORTAL / "index.html").write_text(idx_html,  encoding="utf-8")
    (PORTAL / "archive.html").write_text(arc_html, encoding="utf-8")
    (PORTAL / "memory.html").write_text(mem_html,  encoding="utf-8")

    print(f"[CIEL Portal] Generated → {PORTAL}")
    print(f"  Sessions: {len(sessions)}  Tags: {len(tag_index)}  Memories: {len(mem_entries)}")


if __name__ == "__main__":
    generate()
