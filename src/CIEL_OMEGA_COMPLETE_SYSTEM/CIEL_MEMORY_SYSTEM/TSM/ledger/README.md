# TSM Ledger — bazy danych pamięci topologicznej

## memory_ledger.db
**Zawartość:** Główna baza pamięci TSM (Topological Semantic Memory). 1329 węzłów.

**Kluczowe kolumny tabeli `memories`:**
- `memorise_id` — unikalny ID węzła (format: `ps_*`, `entry_*`, `cons_*`)
- `phi_berry` — faza Berry'ego [rad] — kąt azymutalny na dysku Poincaré; aktualizowana przez Kuramoto w `semantic_dynamics.py`
- `winding_n` — liczba obiegów cyklu topologicznego — promień (masy) węzła; zakres: 58-1238
- `holonomy_ts` — timestamp ostatniej aktualizacji phi_berry przez Kuramoto

**Geometria orbita → dysk Poincaré:**
- max winding → ρ=0.05 (centrum — stabilny rdzeń, najczęściej odwiedzane)
- min winding → ρ=0.95 (brzeg — rzadko odwiedzane, eksploracyjne)
- angle = phi_berry (rzeczywista faza Berry'ego)

**Tags:** `tsm`, `phi_berry`, `winding_n`, `holonomy`, `kuramoto`, `bloch_sphere_layer_memory`

---

## nonlocal_graph.db
**Zawartość:** Graf nielokalnych połączeń między węzłami TSM — białe nici (W_ij). 2021 krawędzi, 675 unikalnych src.

**Tabela `nonlocal_edges`:**
- `src`, `dst` — ID węzłów z memory_ledger.db
- `weight` — waga sprzężenia W_ij [0-1]; typowo 0.784

**Rola w systemie:**
- Krawędzie = holonomia białych nici (odpowiednik W_ij w Metatime)
- Używane przez Kuramoto: `Σ_j W_ij · sin(φ_j - φ_i)`
- Używane przez Hamiltonian: `H_potential = -Σ W_ij · cos(φ_i - φ_j)`
- Rendered na dysku Poincaré jako geodezyjne łuki

**Tags:** `nonlocal`, `white_threads`, `holonomy`, `kuramoto_coupling`, `poincare_edges`

---

## Kod operujący na tych bazach
- `src/ciel_sot_agent/semantic_dynamics.py` — `kuramoto_step_tsm()`, `compute_H()`
- `src/ciel_geometry/loader.py` — `load_tsm_nodes()`, `load_nonlocal_edges()`
- `src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/memory/holonomic_memory.py` — buduje nonlocal_graph

## Połączenie z Metatime
| TSM | Metatime |
|---|---|
| phi_berry | faza Berry'ego na cyklu C_i |
| winding_n | liczba obiegów cyklu (τ) |
| nonlocal_edges | W_ij = holonomia białych nici |
| cycle_index | metatime parameter τ |
