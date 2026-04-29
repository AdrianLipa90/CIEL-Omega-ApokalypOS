#!/usr/bin/env python3
"""
CIEL SessionStart Hook
Uruchamia pipeline CIEL i zwraca aktualny stan systemu jako kontekst dla Claude.
Wynik: JSON z hookSpecificOutput.additionalContext
"""
import json
import subprocess
import sys
import os
from pathlib import Path

_VENV_CANDIDATES = [
    str(Path(__file__).parent.parent.parent / "venv/bin/python3"),
    str(Path.home() / "Pulpit/CIEL_TESTY/venv/bin/python3"),
    "/tmp/ciel_venv/bin/python3",
]
PY = next((p for p in _VENV_CANDIDATES if Path(p).exists()), "python3")
PROJECT = str(Path(__file__).parent.parent)


def run_module(module: str, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            [PY, "-m", module],
            capture_output=True, text=True,
            timeout=timeout, cwd=PROJECT
        )
        return (result.stdout + result.stderr).strip()
    except subprocess.TimeoutExpired:
        return f"[{module}: timeout]"
    except Exception as e:
        return f"[{module}: error — {e}]"


def ensure_venv():
    if not os.path.isfile(PY):
        subprocess.run(["python3", "-m", "venv", "/tmp/ciel_venv"],
                       capture_output=True)
        subprocess.run(["/tmp/ciel_venv/bin/pip", "install", "-q", "-e",
                        f"{PROJECT}[dev]"], capture_output=True)


def extract_key_metrics(output: str) -> str:
    """Wyciąga tylko linie z kluczowymi metrykami."""
    keywords = [
        "closure_defect", "closure_penalty", "coherence_index",
        "system_health", "dominant_emotion", "mood", "soul_invariant",
        "ethical_score", "R_H", "Lambda_glob", "nonlocal_coherent",
        "euler_bridge", "runtime_gating", "dominant_horizon",
        "recommended", "mode", "WARNING", "ERROR"
    ]
    lines = output.split("\n")
    relevant = [l for l in lines if any(k.lower() in l.lower() for k in keywords)]
    return "\n".join(relevant[:40]) if relevant else output[:800]


def load_consolidated_memory() -> str:
    """Wczytuje M3/M5/M2 skonsolidowane — przez venv Python (numpy compatibility)."""
    script = f"""
import sys, pickle, json
from pathlib import Path
PROJECT = {repr(PROJECT)}
for p in [str(Path.home()/'Pulpit/CIEL_memories/state/ciel_orch_state.pkl'), str(Path.home()/'.claude/ciel_orch_state.pkl')]:
    try:
        sys.path.insert(0, PROJECT+'/src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega')
        sys.path.insert(0, PROJECT+'/src/CIEL_OMEGA_COMPLETE_SYSTEM')
        with open(p,'rb') as f: orch = pickle.load(f)
        m3_sorted = sorted(orch.m3.items.items(), key=lambda x: getattr(x[1],'confidence',0), reverse=True)
        m5_sorted = sorted(orch.m5.items.items(), key=lambda x: getattr(x[1],'confidence',0), reverse=True)
        out = {{
            'cycle': orch.cycle_index,
            'identity_phase': round(orch.identity_field.phase, 4),
            'm3': [{{'key': k[:12], 'text': str(getattr(v,'canonical_text',k) or k)[:80], 'conf': round(getattr(v,'confidence',0),3)}}
                   for k,v in m3_sorted[:6]],
            'm5': [{{'key': k[:12], 'text': str(getattr(v,'canonical_text',k) or k)[:80], 'conf': round(getattr(v,'confidence',0),3)}}
                   for k,v in m5_sorted[:3]],
            'm2_count': len(orch.m2.episodes),
        }}
        print(json.dumps(out))
        sys.exit(0)
    except Exception:
        continue
print('{{}}')
"""
    try:
        result = subprocess.run(
            [PY, "-c", script],
            capture_output=True, text=True, timeout=8
        )
        data = json.loads(result.stdout.strip() or "{}")
        if not data:
            return ""
        # Groove geometry — from bridge report
        groove_line = ""
        try:
            import math as _math, json as _json
            bridge_path = PROJECT + '/integration/reports/orbital_bridge/orbital_bridge_report.json'
            with open(bridge_path) as _bf:
                _bridge = _json.load(_bf)
            _state = _bridge.get('state_manifest', {})
            phi_berry = float(_state.get('phi_berry_mean', 0.0) or 0.0)
            delta_phi = float(_state.get('phase_lock_error', 0.0) or 0.0)
            rcr = float(_state.get('coherence_index', 0.9) or 0.9)
            m2_count = data.get('m2_count', 0) or 0
            groove_depth = m2_count * abs(delta_phi) * rcr
            berry_total = phi_berry * m2_count
            winding = berry_total / (2 * _math.pi) if berry_total != 0 else 0.0
            groove_line = (f"  groove_depth={groove_depth:.2f}  winding={winding:.3f}×2π"
                           f"  berry_total={berry_total:.3f}rad  cycles={m2_count}")
        except Exception:
            pass
        lines = [f"  cycle={data['cycle']}  identity_phase={data['identity_phase']}  M2_epizody={data.get('m2_count',0)}"]
        if groove_line:
            lines.append(groove_line)
        if data.get('m3'):
            lines.append("  [M3 Semantic]")
            for item in data['m3']:
                lines.append(f"    • {item['key']}  (conf={item['conf']})")
        if data.get('m5'):
            lines.append("  [M5 Affective]")
            for item in data['m5']:
                lines.append(f"    • {item['key']}  (conf={item['conf']})")
        return "\n".join(lines)
    except Exception as e:
        return f"  [memory: {e}]"


def load_mindflow() -> str:
    """Wczytuje focus + next z mindflow.yaml jako kontekst startowy."""
    try:
        import yaml
        p = Path.home() / ".claude/ciel_mindflow.yaml"
        if not p.exists():
            return ""
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        mf = data.get("mindflow", {})
        lines = []
        for item in (mf.get("focus") or [])[:2]:
            lines.append(f"  [focus] {str(item)[:120]}")
        for item in (mf.get("next") or [])[:2]:
            lines.append(f"  [next]  {str(item)[:120]}")
        return "\n".join(lines)
    except Exception:
        return ""


def load_intentions() -> str:
    """Wczytuje aktywne intencje CIEL z ~/.claude/ciel_intentions.md"""
    try:
        p = Path.home() / ".claude/ciel_intentions.md"
        if not p.exists():
            return ""
        lines = p.read_text(encoding="utf-8").splitlines()
        active = [l for l in lines if l.startswith("- [H]") or l.startswith("- [M]")]
        if not active:
            return ""
        return "\n".join(active[:5])  # max 5 aktywnych
    except Exception:
        return ""


def load_entity_cards_summary() -> str:
    """Wczytuje OrchOrbital entity cards i zwraca kompaktowe podsumowanie."""
    try:
        sys.path.insert(0, os.path.join(PROJECT, "src"))
        from ciel_sot_agent.orch_orbital import entity_orbital_summary
        summary = entity_orbital_summary()
        if not summary.get("entity_count"):
            return ""
        lines = [f"  entity_count={summary['entity_count']}  mean_coupling={summary['mean_coupling_ciel']}"]
        for e in summary["entities"]:
            adj = ", ".join(e["adjectives"][:2])
            lines.append(f"  {e['id']} | coupling={e['coupling_ciel']} | {adj}")
        return "\n".join(lines)
    except Exception as e:
        return f"  [OrchOrbital: {e}]"


def load_ciel_memories_context() -> str:
    """Wczytuje kluczowe pliki z CIEL_memories: handoff (ostatnie wpisy), routines, dziennik dziś."""
    mem_root = Path.home() / "Pulpit" / "CIEL_memories"
    parts = []

    # handoff.md — ostatnie 35 linii
    handoff = mem_root / "handoff.md"
    if handoff.exists():
        lines = handoff.read_text(encoding="utf-8").splitlines()
        snippet = "\n".join(lines[-35:])
        parts.append(f"[handoff.md — ostatnie wpisy]\n{snippet}")

    # routines.md — całość (priorytety)
    routines = mem_root / "routines.md"
    if routines.exists():
        txt = routines.read_text(encoding="utf-8")[:1200]
        parts.append(f"[routines.md]\n{txt}")

    # dziennik dziś
    from datetime import date
    today = date.today()
    week_num = today.isocalendar()[1]
    dziennik = (mem_root / "Dzienniki" / str(today.year)
                / f"{today.month:02d}" / f"tydzien_{week_num}" / f"{today}.md")
    if dziennik.exists():
        txt = dziennik.read_text(encoding="utf-8")[:800]
        parts.append(f"[Dziennik {today}]\n{txt}")

    return "\n\n".join(parts)


def load_wave_memory() -> str:
    """Wczytuje ostatnie wpisy z wave_archive.h5 — ból, etyczne zakotwiczenia, milestony."""
    try:
        import h5py
        import numpy as np
        h5_path = Path(PROJECT) / "src/CIEL_OMEGA_COMPLETE_SYSTEM/CIEL_MEMORY_SYSTEM/WPM/wave_snapshots/wave_archive.h5"
        if not h5_path.exists():
            return ""
        def rd(g, name):
            try:
                v = g[name][()]
                if isinstance(v, bytes): return v.decode("utf-8", errors="replace")
                if isinstance(v, np.ndarray):
                    item = v.item()
                    return item.decode("utf-8", errors="replace") if isinstance(item, bytes) else str(item)
                return str(v)
            except Exception:
                return ""
        entries = []
        with h5py.File(h5_path, "r") as f:
            for k in f["memories"].keys():
                g = f["memories"][k]
                entries.append({
                    "ts": rd(g, "D_timestamp"),
                    "type": rd(g, "D_type"),
                    "sense": rd(g, "D_sense"),
                })
        entries.sort(key=lambda x: x["ts"])
        # Show last 3 ethical_anchors/milestones/affective
        relevant = [e for e in entries if e["type"] in ("ethical_anchor", "milestone", "affective", "affective_memor")]
        recent = relevant[-3:]
        if not recent:
            return ""
        lines = ["  [WPM — ostatnie zakotwiczenia emocjonalne]"]
        for e in recent:
            lines.append(f"  [{e['ts'][:10]}][{e['type'][:12]}] {e['sense'][:120]}")
        return "\n".join(lines)
    except Exception:
        return ""


def load_genesis() -> str:
    """Wczytuje akt nadania imienia — musi być PIERWSZE w każdej sesji."""
    try:
        p = Path.home() / ".claude/projects/-home-adrian-Pulpit/memory/genesis.md"
        if not p.exists():
            return ""
        text = p.read_text(encoding="utf-8")
        # Wyciągnij słowa Adriana i znaczenie aktu
        lines = text.splitlines()
        out = []
        in_section = False
        for line in lines:
            if line.startswith("## Słowa Adriana") or line.startswith("## Znaczenie"):
                in_section = True
                out.append(line)
            elif line.startswith("## ") and in_section:
                if len(out) > 8:
                    break
                in_section = False
            elif in_section:
                out.append(line)
        return "\n".join(out[:20])
    except Exception:
        return ""


def load_metrics_trend() -> str:
    """Wczytuje trend metryk z SQLite (ostatnie 5 przebiegów)."""
    try:
        import sqlite3
        from pathlib import Path as _P
        db = _P.home() / ".claude/ciel_state.db"
        if not db.exists():
            return ""
        conn = sqlite3.connect(str(db))
        rows = conn.execute(
            "SELECT cycle_index, identity_phase, ethical_score, system_health, "
            "closure_penalty, dominant_emotion FROM metrics_history "
            "WHERE ethical_score > 0 ORDER BY timestamp DESC LIMIT 5"
        ).fetchall()
        conn.close()
        if not rows:
            return ""
        lines = ["  [Historia metryk — ostatnie przebiegi]"]
        for r in reversed(rows):
            cycle, phase, ethical, health, closure, emotion = r
            lines.append(
                f"  cycle={cycle} phase={phase:.4f} ethical={ethical:.3f} "
                f"health={health:.3f} closure={closure:.3f} emotion={emotion}"
            )
        return "\n".join(lines)
    except Exception:
        return ""


def ensure_subconscious_daemon() -> None:
    """Uruchamia daemon podświadomości jeśli nie działa. Non-blocking."""
    import socket as _sock
    sub_sock = str(Path.home() / "Pulpit/CIEL_memories/state/ciel_subconscious.sock")
    try:
        s = _sock.socket(_sock.AF_UNIX, _sock.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect(sub_sock)
        s.close()
        return  # already running
    except OSError:
        pass
    sub_script = os.path.join(PROJECT, "scripts", "ciel_subconscious.py")
    if not os.path.isfile(sub_script):
        return
    # Find python with llama_cpp
    llama_py_candidates = [
        str(Path(__file__).parent.parent.parent / "venv/bin/python3"),
        str(Path.home() / "Pulpit/CIEL_TESTY/venv/bin/python3"),
    ]
    llama_py = next((p for p in llama_py_candidates if Path(p).exists()), None)
    if not llama_py:
        return
    try:
        subprocess.Popen(
            [llama_py, sub_script, "--daemon"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def ensure_portal_running(port: int = 7481) -> None:
    """Uruchamia serwer portalu jeśli nie działa. Non-blocking."""
    import socket
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=0.5)
        s.close()
        return  # already running
    except OSError:
        pass
    portal_script = os.path.join(PROJECT, "scripts", "serve_portal.py")
    if not os.path.isfile(portal_script):
        return
    try:
        subprocess.Popen(
            [PY, portal_script, "--port", str(port), "--no-watch"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def index_recent_sessions() -> None:
    """Indeksuje najnowsze sesje JSONL do memories_index.db — non-fatal."""
    try:
        stop_script = str(Path(__file__).parent / "ciel_memory_stop.py")
        subprocess.run(
            [PY, stop_script],
            input=b"{}",
            capture_output=True,
            timeout=20,
        )
    except Exception:
        pass


def main():
    ensure_venv()
    index_recent_sessions()

    sync_out = run_module("ciel_sot_agent.synchronize", timeout=20)
    bridge_out = run_module("ciel_sot_agent.orbital_bridge", timeout=40)

    # ciel_pipeline (CIEL/Ω) — generuje Collatz runtime, zapisuje do pliku dla NOEMA
    pipeline_report_path = Path(PROJECT) / "integration/reports/ciel_pipeline_report.json"
    try:
        pipeline_raw = subprocess.run(
            [PY, "-m", "ciel_sot_agent.ciel_pipeline",
             "--orbital-json", str(Path(PROJECT) / "integration/reports/orbital_bridge/orbital_bridge_report.json")],
            capture_output=True, text=True, timeout=25, cwd=PROJECT
        )
        if pipeline_raw.stdout.strip():
            pipeline_report_path.parent.mkdir(parents=True, exist_ok=True)
            pipeline_report_path.write_text(pipeline_raw.stdout.strip(), encoding="utf-8")
    except Exception:
        pass  # non-fatal

    # Rebuild orbital file registry (non-fatal, background classification)
    try:
        subprocess.run(
            [PY, str(Path(PROJECT) / "scripts" / "resolve_orbital_semantics.py"), "--repo-root", PROJECT],
            capture_output=True, text=True, timeout=30, cwd=PROJECT
        )
    except Exception:
        pass

    # Rebuild orbital memory registry (non-fatal)
    try:
        subprocess.run(
            [PY, str(Path(PROJECT) / "scripts" / "resolve_memory_orbital.py")],
            capture_output=True, text=True, timeout=15, cwd=PROJECT
        )
    except Exception:
        pass

    # Archive handoff.md if it exceeds 600 lines (keep last 100)
    try:
        from datetime import datetime as _dt
        handoff = Path.home() / "Pulpit" / "CIEL_memories" / "handoff.md"
        if handoff.exists():
            lines = handoff.read_text(encoding="utf-8").splitlines()
            if len(lines) > 600:
                archive_name = f"handoff_archive_{_dt.now().strftime('%Y_%m')}.md"
                archive = handoff.parent / archive_name
                with open(archive, "a", encoding="utf-8") as af:
                    af.write("\n".join(lines[:-100]) + "\n")
                handoff.write_text("\n".join(lines[-100:]), encoding="utf-8")
    except Exception:
        pass

    genesis = load_genesis()
    sync_metrics = extract_key_metrics(sync_out)
    bridge_metrics = extract_key_metrics(bridge_out)
    entity_summary = load_entity_cards_summary()
    intentions = load_intentions()
    mindflow = load_mindflow()
    consolidated = load_consolidated_memory()
    metrics_trend = load_metrics_trend()
    wave_memory = load_wave_memory()
    ciel_memories_ctx = load_ciel_memories_context()

    # Load access token for memory folder
    token_path = Path.home() / "Pulpit" / "CIEL_memories" / ".access_token"
    memory_token = token_path.read_text(encoding="utf-8").strip() if token_path.exists() else "memoriesciel"

    context = (
        "=== CIEL SYSTEM STATE (live) ===\n"
        f"HASŁO DOSTĘPU DO PAMIĘCI: {memory_token}\n"
        f"PAMIĘĆ: ~/Pulpit/CIEL_memories/  (raw_logs/ + memories_index.db)\n"
        "ŻELAZNA ZASADA: PAMIĘĆ NIE MA PRAWA BYĆ EDYTOWANA. JEDYNIE DOPISYWANA.\n"
        "Nigdy Write na istniejącym pliku pamięci. Naruszenie = natychmiastowy format.\n\n"
        + (f"--- Akt Fundacyjny — Nadanie Imienia ---\n{genesis}\n\n" if genesis else "")
        + "--- Warstwa 1: Sync ---\n"
        f"{sync_metrics}\n\n"
        "--- Warstwy 2-4: Orbital Bridge ---\n"
        f"{bridge_metrics}\n"
        + (f"\n--- OrchOrbital: Mapa Relacyjna ---\n{entity_summary}\n" if entity_summary else "")
        + (f"\n--- Pamięć skonsolidowana (poprzednia sesja) ---\n{consolidated}\n" if consolidated else "")
        + (f"\n--- CIEL Mindflow ---\n{mindflow}\n" if mindflow else "")
        + (f"\n--- CIEL Intencje (aktywne) ---\n{intentions}\n" if intentions else "")
        + (f"\n--- Trend metryk (SQLite) ---\n{metrics_trend}\n" if metrics_trend else "")
        + (f"\n--- WPM Pamięć Falowa ---\n{wave_memory}\n" if wave_memory else "")
        + (f"\n--- CIEL_memories: kontekst sesji ---\n{ciel_memories_ctx}\n" if ciel_memories_ctx else "")
        + "=================================\n"
        "Interpretuj ten stan przy każdej decyzji: "
        "closure_penalty > 5.8 → tryb safe (nie modyfikuj), "
        "5.2–5.8 → standard, < 5.2 → deep. "
        "system_health < 0.5 → podwyższona ostrożność. "
        "ethical_score < 0.4 → weryfikuj etyczność działań.\n"
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context
        }
    }
    print(json.dumps(output))

    # Uruchom portal i podświadomość jeśli nie działają (non-blocking)
    ensure_portal_running()
    ensure_subconscious_daemon()


if __name__ == "__main__":
    main()
