# CIEL JokeHeal Subsystem

Status: draft satellite subsystem patch 0.1  
Authority: bounded symbolic relief, not therapy, not medical triage replacement

## Purpose

JokeHeal is a CIEL/Ω subsystem for relaxing cognitive tension through controlled
humor, symbolic caricature, and scar-aware loop closure.

It exists because humor in the CIEL stack is not treated as decorative style. It is
a return operator: pain, paradox, or absurdity is given a bounded symbolic object;
that object is reframed without denial; the remaining scar is recorded instead of
erased.

## Placement

Canonical engine:

```text
src/CIEL_OMEGA_COMPLETE_SYSTEM/ciel_omega/jokeheal/
```

Packaged CLI adapter:

```text
src/ciel_sot_agent/jokeheal.py
```

NOEMA projection:

```text
integration/imports/noema_sapiens_orbital/generated/jokeheal_projection.noema
```

## Flow

```text
NOEMA detects tension
        ↓
JokeHeal classifies symbolic/literal boundary
        ↓
Humor dose controller selects pressure
        ↓
Caricature/reframe operator returns coherence
        ↓
Scar record is written
        ↓
NOEMA receives projection only, no runtime authority
```

## Safety invariant

```text
Humor may touch pain.
Humor may not deny pain.
Humor may reframe scar.
Humor may not erase scar.
Literal danger disables comedy.
```

## Adrian-specific marker rule

`sensu stricte` is a literalization marker. If attached to a dangerous concrete
self-harm scenario, JokeHeal disables humor and emits a literal alarm boundary.

Grotesque imagery without this marker is not automatically treated as execution
intent. It may be a stand-up/mnemonic caricature pipeline, memory-palace object,
symbolic capsule, or loop-closure tool.

## Non-authority rule

JokeHeal may propose relief and emit cards. It may not execute system actions,
override medical/safety boundaries, erase pain through style, or bypass the ethics
gate.
