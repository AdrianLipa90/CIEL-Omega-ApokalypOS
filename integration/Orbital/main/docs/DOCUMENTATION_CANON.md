# Documentation Canon

Status: **canonical documentation map** for this workspace.

## Canonical documents

### Repo-level canon
- `README.md` — repository purpose and scope
- `docs/MECHANISM_SCOPE.md` — what this repo is and is not
- `docs/FORMALISM_V0.md` — current mechanism-layer formal objects
- `docs/RUNTIME_TARGETS_V0.md` — conservative runtime target policy
- `docs/MD_AUDIT_NOTES.md` — markdown audit notes, drift, and update log

### Embedded runtime canon
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/README.md` — current build-level structure and verified behavior
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/README.md` — high-level package overview, but not the final source of truth for implementation status
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/orbital/README.md` — orbital subsystem scope

## Historical or non-canonical documents

These files remain useful, but should not be treated as the first source of truth for current behavior:
- `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/README_old.md` — historical architecture snapshot
- audit reports in `docs/` — point-in-time reports, not standing canon
- generated vocabulary summaries — derived artifacts, not normative spec
- manual upload markdown files under `references/manual_uploads/` — reference material only

## Single-file reference

`docs/DOCUMENTATION_MERGED.md` — canonical merged documentation embedding all source documents listed above into one clean and precise file. Start here for a consolidated reading.

## Reading order

1. `docs/DOCUMENTATION_MERGED.md` (single-file entry point)
2. `README.md`
3. `docs/MECHANISM_SCOPE.md`
4. `docs/FORMALISM_V0.md`
5. `docs/MD_AUDIT_NOTES.md`
6. `data/source/CIEL_OMEGA_COMPLETE_SYSTEM/README.md`
7. subsystem READMEs as needed

## Rule

If two markdown files disagree:
- prefer the file listed above as canonical,
- prefer the newest audited status over older marketing language,
- prefer implementation-backed claims over aspirational claims.
