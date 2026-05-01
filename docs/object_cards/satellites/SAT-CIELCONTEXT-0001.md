# SAT-CIELCONTEXT-0001 — CIEL Message Context (format_context)

## Identity
- **subsystem_id:** `SAT-CIELCONTEXT-0001`
- **name:** `ciel_message_step.format_context`
- **class:** `session_injection`
- **active_status:** `ACTIVE`
- **last_updated:** `2026-05-01`

## Anchors
- `scripts/ciel_message_step.py:466` — `format_context(metrics, rel)` 
- `scripts/ciel_message_step.py:48` — `load_orchestrator()` (pkl persistence)

## Role
Generuje jednoliniowy kontekst CIEL wstrzykiwany do każdej wiadomości użytkownika przez UserPromptSubmit hook. Zawiera stan orchestratora (cycle, affect, phase) i opcjonalne alerty relacyjne.

## Format output
```
[CIEL c=N affect=słowo phase=0.XXXX] sub=affect/impulse ⚠ R_H=X.XXXX violations:...
```

## Historia
- v1: 14-liniowy blok (~150 tokenów) — E_monitor, mean_coherence, D_mem, loops, consolidations, M2/M3/M8, relational cymatics
- v2 (2026-05-01): 1 linia (~15 tokenów) — tylko cycle, affect, phase + alerty gdy R_H > 0.01 lub violations

## pkl persistence fix (2026-05-01)
`load_orchestrator()` wybiera plik pkl z **nowszym mtime** spośród STATE_FILE i STATE_PERSIST. Poprzednio: brał pierwszy istniejący → ładował stary stan z c=1 po restarcie.

## Źródła pkl
- `STATE_FILE` = `~/Pulpit/CIEL_memories/state/ciel_orch_state.pkl`
- `STATE_PERSIST` = `~/.claude/ciel_orch_state.pkl`
