# Phased Seed Trajectory Encoding

This note records a working concept for a two-layer encoding scheme built from deterministic seed families, phase assignment, and observable trajectory coding.

status: concept note / not yet implemented / exploratory encoding model

## Core split

The proposed scheme separates the system into two layers:

1. internal seed layer
2. observable trajectory layer

The intention is to keep the seed-generation rule configurable while keeping the structural trajectory coder explicit and auditable.

## Layer 1. Seed generator

For object or node `i`, define a configuration-dependent generator

`k_i = G_seed(i)`

Candidate families discussed so far:
- twin-prime driven sequence: `k_i = p_i + 1` where `(p_i, p_i + 2)` is a twin-prime pair,
- Fibonacci-driven sequence: `k_i = F_i + 1`.

Operational role of the seed layer:
- stable hidden ordering inside the system,
- phase initialization,
- sparse activation or channel selection,
- deterministic but nontrivial object ordering.

## Layer 2. Observable trajectory coder

Use a Collatz-type coder to derive observable trajectory structure from the seed:

`T(n) = n / 2` for even `n`,
`T(n) = 3n + 1` for odd `n`.

From the resulting orbit one may extract:
- parity word,
- braid or operator word,
- stopping-time proxy,
- curvature or entropy surrogate,
- trajectory fingerprint.

In this split, Collatz acts as the observable structural encoder.

## Local phase-state assignment

Given a seed-derived key `k_i`, define a phase and amplitude:

`phi_i = 2 * pi * frac(g(k_i))`

`a_i = sqrt(E_i_tilde)`

and the local complex state

`psi_i = a_i * exp(i * phi_i)`

with global normalization

`sum_i |psi_i|^2 = 1`.

This turns each object into a locally phased state instead of a plain identifier.

## Seed-trajectory bundle

A compact conceptual bundle is therefore:
- seed: `k_i = G_seed(i)`
- trajectory: `b_i = CollatzWord(k_i)`
- phase: `phi_i = 2 * pi * frac(g(k_i))`
- state: `psi_i = a_i * exp(i * phi_i)`

Possible coupling surface:

`C_ij = a_i * a_j * cos(phi_i - phi_j)`

or the complex form

`C_ij = psi_i * conj(psi_j)`.

## Why this may be useful

Potential benefits:
- separates initialization from visible structural coding,
- supports phase-based state geometry,
- can be reused for encoding, compression, or resonance mapping,
- keeps the trajectory layer auditable,
- allows deterministic reconstruction when the seed rule is known.

## Immediate implementation path

A minimal prototype could:
1. generate `k_i` from a selectable family (`twin_prime_plus_one`, `fib_plus_one`),
2. compute a Collatz parity word,
3. assign `phi_i` and `psi_i`,
4. build pairwise coupling diagnostics,
5. compare resulting structure with ordinary hash-only indexing.

## Open unknowns

- Which seed family produces the most stable phase distribution?
- Should phase correction depend only on the seed or also on object type and layer?
- Is Collatz the best observable coder, or only the first workable one?
- Can the same split support both compression-oriented and indexing-oriented pipelines without conflict?
- What observable advantage does the phased representation provide over ordinary graph embeddings?

## Recommended interpretation

Treat this as a repository-level concept note for:
- phased object encoding,
- seed/trajectory split in structural coding,
- future experiments in orbital indexing, coupling, or compression.
