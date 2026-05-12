# CIELingo v2.3 — Language Family Grammar Algorithms

CIELingo must not treat grammar as one global parser. Grammar algorithms are layered:

```text
language family -> language profile -> dialect/variant adapter -> prompt-level route
```

Shared semantic invariant does not imply shared grammar algorithm. If a family/language algorithm is missing, emit an explicit unresolved state such as `UNRESOLVED_LANGUAGE_PROFILE` or `UNRESOLVED_GRAMMAR_ALGORITHM`. Do not guess.
