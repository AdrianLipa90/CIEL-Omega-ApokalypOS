#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, shutil, urllib.request, zipfile, hashlib
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def find_local_archive(repo_root: Path, drop_dirs: list[str], local_candidates: list[str]) -> Path | None:
    for drop in drop_dirs:
        base = (repo_root / drop).resolve() if not os.path.isabs(drop) else Path(drop)
        for cand in local_candidates:
            p = base / cand
            if p.exists():
                return p
    return None

def download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as r, target.open('wb') as w:
        shutil.copyfileobj(r, w)

def extract_zip(archive: Path, target: Path) -> None:
    if target.exists():
        return
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        members = zf.namelist()
        common = None
        if members:
            roots = {m.split('/',1)[0] for m in members if m and not m.startswith('__MACOSX')}
            if len(roots) == 1:
                common = next(iter(roots))
        zf.extractall(target.parent)
        if common:
            extracted = target.parent / common
            if extracted.exists() and extracted != target:
                if target.exists():
                    shutil.rmtree(target)
                extracted.rename(target)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root', default='.')
    ap.add_argument('--config', default='integration/imports/audio_orbital_stack/assets_audio_stack.json')
    ap.add_argument('--skip-download', action='store_true')
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    config_path = (repo_root / args.config).resolve()
    cfg = json.loads(config_path.read_text(encoding='utf-8'))

    state = {"schema": "ciel/audio-orbital-stack-state/v0.1", "archives": {}, "models": {}}
    drop_dirs = cfg.get("drop_dir_candidates", ["..", "/mnt/data"])

    for key, meta in cfg["archives"].items():
        archive = find_local_archive(repo_root, drop_dirs, meta["local_candidates"])
        archive_state = {"display_name": meta["display_name"], "found": False, "downloaded": False, "extracted": False, "active_pipeline": meta.get("active_pipeline", False)}
        if archive is None and meta.get("source_url") and not args.skip_download:
            dl_target = repo_root / 'integration' / 'imports' / 'audio_orbital_stack' / 'archives' / meta["local_candidates"][0]
            dl_target.parent.mkdir(parents=True, exist_ok=True)
            download(meta["source_url"], dl_target)
            archive = dl_target
            archive_state["downloaded"] = True
        if archive is not None and archive.exists():
            archive_state["found"] = True
            archive_state["path"] = str(archive)
            archive_state["sha256"] = sha256_file(archive)
            should_extract = meta.get("extract_default", True)
            if should_extract:
                extract_target = repo_root / 'integration' / 'imports' / 'audio_orbital_stack' / meta["extract_to"]
                extract_zip(archive, extract_target)
                archive_state["extract_target"] = str(extract_target)
                archive_state["extracted"] = extract_target.exists()
            else:
                archive_state["extract_target"] = None
        state["archives"][key] = archive_state

    for key, meta in cfg.get("models", {}).items():
        target = repo_root / 'integration' / 'imports' / 'audio_orbital_stack' / meta["target_path"]
        model_state = {"description": meta["description"], "path": str(target), "present": target.exists(), "downloaded": False}
        if not target.exists() and meta.get("source_url") and not args.skip_download:
            target.parent.mkdir(parents=True, exist_ok=True)
            download(meta["source_url"], target)
            model_state["downloaded"] = True
            model_state["present"] = target.exists()
        state["models"][key] = model_state

    out = repo_root / 'integration' / 'imports' / 'audio_orbital_stack' / 'state' / 'audio_orbital_stack_state.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(state, indent=2), encoding='utf-8')
    print(json.dumps(state, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
