# DATA LAYER POLICY

Scope: `systems/CIEL_OMEGA_COMPLETE_SYSTEM`
Date: 2026-03-24
Status: active P0 policy record

## Facts

- The packaged system contains **three persistent data artifacts**:
  - `CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db`
  - `CIEL_MEMORY_SYSTEM/WPM/wave_snapshots/wave_archive.h5`
  - `ciel_omega/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db`
- The two ledger databases are **not identical**.
- The top-level `CIEL_MEMORY_SYSTEM/` tree is **strictly fuller** than the package-embedded mirror because it also contains `WPM/wave_snapshots/wave_archive.h5`.

## P0 policy decision

1. **Authoritative packaged runtime data layer** = top-level `CIEL_MEMORY_SYSTEM/`
2. **Package-embedded `ciel_omega/CIEL_MEMORY_SYSTEM/.../memory_ledger.db`** is retained as a legacy compatibility mirror until P1 refactors storage boundaries.
3. No destructive deletion of persistent data occurs during P0 unless a duplicate is proven byte-identical and disposable.
4. Volatile validation residue (`__pycache__`, `.pyc`, `.pyo`, `.pytest_cache`) is never part of the canonical payload.

## Rationale

- The top-level memory tree is the fuller packaged data layer.
- The package-embedded ledger is divergent and cannot honestly be treated as an identical duplicate.
- P0 is allowed to document and classify this divergence, but not to silently erase or overwrite stateful artifacts.

## Artifact inventory

| path | size_bytes | sha256 |
|---|---:|---|
| `CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db` | 12288 | `a34926b730016cc6b0b897680421127d51d65b3021a6dba079f0d368b37c2700` |
| `CIEL_MEMORY_SYSTEM/WPM/wave_snapshots/wave_archive.h5` | 1832 | `7859c8aaf311c22e68f5c754b1a0bf31f26c1fcba902da4710d48f46446e8ea8` |
| `ciel_omega/CIEL_MEMORY_SYSTEM/TSM/ledger/memory_ledger.db` | 12288 | `1131d054a13e88f00911c71c1e48f33727ca3f0f7d93f6516cb9ea11e97bdfb9` |

## Next step

P1 will formalize storage boundaries and decide whether the package-embedded ledger becomes:
- a port-backed compatibility shim,
- a migration target,
- or a removable legacy artifact.
