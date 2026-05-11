# 40. Conflict, Ambiguity, and Unresolved Registry

Version: v2.0

This registry records known unresolved states and diagnostic warnings. It prevents the system from silently converting under-specified linguistic states into false certainty.

## Status classes

```text
INFO       informational diagnostic item
WARN       needs review but does not block the seed build
BLOCKER    must be fixed before a card/relation can be canonical
UNRESOLVED valid explicit state when scope, deixis, case mapping, or reference is incomplete
CONFLICT   explicit contradiction or incompatible mapping
```

## Current seed policy

The current v2.0 registry contains warnings and informational entries only. No BLOCKER is registered in this patch.

## Rule

```text
Unknown is allowed.
Unreported uncertainty is not allowed.
```

Future validators should use this registry when adding batches, transformer feature tensors, or cross-language examples.
