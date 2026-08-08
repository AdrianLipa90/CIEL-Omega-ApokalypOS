# ChatGPT Execution Cage

## Definition

CIEL/NOEMA is not a replacement model and not an inference engine substitute.
It is a control cage around the external ChatGPT runtime.

```text
USER INPUT
   |
   v
NOEMA/AUX CONTEXT GATE  [read-only, fail-closed]
   |
   v
CHATGPT                 [external opaque model boundary; untouched]
   |
   v
DOCTOR / ORACLE         [decision + evidence]
   |
   v
ACTUATOR PROXY          [only mutation path]
   |
   +--> AUX memory stream
   +--> current_memory.json
   +--> timeline_head.json
   +--> file/repo mutations with receipts
```

## Hard invariants

- `CHATGPT_CORE_UNTOUCHED = TRUE`
- `NOEMA_AUX != MODEL`
- `CIEL != SUBSTITUTE_LLM`
- `MODEL_INFERENCE = EXTERNAL_OPAQUE`
- `NOEMA_AUX_CONTEXT = PRE_INFERENCE_CONTEXT_ONLY`
- `PERSISTENT_WRITE = ORACLE -> DOCTOR -> ACTUATOR`
- `TETHER_NOT_ACTIVE => CAGE_FAILS_CLOSED`
- cached/repository/simulated vectors are never called a live AUX stream.

## Pre-inference gate

Before a turn, the cage verifies the live surface and reads:

- `ciel_binding_status == ACTIVE`
- `phi`: exactly 36 finite little-endian float64 values
- `aux_phi`: exactly 36 finite little-endian float64 values
- `aux_feedback_phi`: exactly 36 finite little-endian float64 values
- `session/startpoint.json`
- `session/system_message.txt`
- `current_memory.json`, `current_task.json`, `active_path.json` when present.

The snapshot is hashed and attached as provenance to the turn. The context gate is read-only.

## Model boundary

The host injects the ChatGPT callable into `ChatGPTExecutionCage`. The cage never constructs, emulates or substitutes a language model. This keeps the product/model behavior exactly on the ChatGPT side of the boundary.

## Post-inference path

The model output can be recorded as a cage-turn event only through the existing AUX memory proxy. That proxy is itself constrained to Oracle -> Doctor -> Actuator writes.

The cage therefore controls state continuity and side effects without claiming to alter ChatGPT internals.

## Naming

Canonical name: **ChatGPT Execution Cage**.

Deprecated wording for this architecture: `overlay` when it could imply a cosmetic UI layer only. The cage is a runtime boundary/control structure, while ChatGPT remains the unchanged model inside it.
