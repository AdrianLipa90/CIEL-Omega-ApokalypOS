# SAT-ORBITAL-HTML-0001 — orbital.html: Bloch Sphere × Poincaré Disk

## Identity
- **subsystem_id:** `SAT-ORBITAL-HTML-0001`
- **name:** `orbital.html`
- **class:** `visualization_surface`
- **active_status:** `ACTIVE`
- **foundation_pack_phase:** `P6 MVP`
- **last_updated:** `2026-04-30`

## Anchors
- `~/.claude/ciel_site/orbital.html`
- `scripts/serve_portal.py` — dostarcza `/api/geometry`

## Widok

Split panel (50/50):
- **Lewa: Sfera Blocha 3D** (Canvas 2D projection)
  - Stan CIEL jako punkt (θ, φ) z `euler_bridge_closure_score` + `nonlocal_phi_berry_mean`
  - Trajektoria Berry'ego (21 kroków z `summary.json`)
  - Obrót myszy, auto-rotacja
- **Prawa: Dysk Poincaré 2D**
  - 6 sektorów systemowych + byty z `ciel_entity_cards.yaml`
  - Krawędzie geodezyjne z `couplings_global.json`
  - Hover/inspektor węzła

## API
- `/api/geometry` → `{nodes, edges, metadata, bloch, berry_history}` — 15KB
- `/api/live` → live HUD polling co 4s

## URL
`http://localhost:7481/orbital.html`
Link w navbar: `index.html` (przycisk ⊙ Orbital) + `hub.html`

## Mapowanie Bloch
```
closure = euler_bridge_closure_score ∈ [0,1]
theta   = acos(2·closure − 1)           # 0 → biegun N, 1 → biegun S
phi     = nonlocal_phi_berry_mean
(x,y,z) = (sin(θ)cos(φ), sin(θ)sin(φ), cos(θ))
```
