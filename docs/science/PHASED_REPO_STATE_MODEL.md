# Phased Repository State Model

This document defines the canonical working model for representing repository files as a normalized phased state system.

status: canonical working definition / implementation-oriented / not a physical law claim

## Purpose

The goal of this model is to represent each file as a local complex state carrying:
- deterministic identity,
- normalized energy share,
- phase,
- and amplitude.

This allows:
- stable comparisons across repositories and subsystems,
- folder-level aggregation,
- coupling diagnostics,
- and future orbital or Bloch-like state projections.

## 1. Deterministic seed

For each file `i`, define the deterministic seed

`s_i = H(path_i, size_i, content_i)`

where `H` is a stable hash function.

Canonical implementation choice:
- `H = SHA256`
- `h_i = frac64(s_i)` is the normalized scalar extracted from the first 64 bits of the digest, mapped to `[0, 1)`.

## 2. Raw energy

For each file `i`, define the raw energy

`E_i_raw = w_type(tau_i) * w_layer(lambda_i) * f_size(B_i) * f_conn(r_i) * f_seed(s_i)`

where:
- `tau_i` = file type,
- `lambda_i` = repository layer,
- `B_i` = file size in bytes,
- `r_i` = connection or reference count,
- `s_i` = deterministic seed.

### 2.1 Size term

`f_size(B_i) = 1 + alpha * ln(1 + B_i / B0)`

Canonical bootstrap parameters:
- `alpha = 0.18`
- `B0 = 1024`

This suppresses the pathological case where large files dominate the total state only by byte count.

### 2.2 Connection term

`f_conn(r_i) = 1 + beta * ln(1 + r_i)`

Canonical bootstrap parameter:
- `beta = 0.12`

If no connection graph is available yet, use `r_i = 0`, which yields `f_conn = 1`.

### 2.3 Seed modulation term

`f_seed(s_i) = 0.95 + 0.10 * h_i`

This keeps seed modulation in the interval `[0.95, 1.05)`.
The seed modulates the local energy slightly, but does not dominate the system.

## 3. Type weights

Canonical bootstrap weights:

| File type | Weight |
| --- | ---: |
| `py` | 1.30 |
| `ipynb` | 1.20 |
| `json` | 1.10 |
| `yaml`, `yml` | 1.10 |
| `toml` | 1.05 |
| `md` | 1.00 |
| `txt` | 0.90 |
| `pdf` | 0.85 |
| `sh`, `bash` | 1.00 |
| `png`, `jpg`, `jpeg`, `svg` | 0.60 |
| `zip`, `tar.gz`, `bin`, `gguf` | 0.40 |
| fallback / unknown | 0.75 |

## 4. Layer weights

Canonical bootstrap weights:

| Repository layer | Weight |
| --- | ---: |
| `src/core` | 1.40 |
| `src/support` | 1.20 |
| `contracts` | 1.35 |
| `integration` | 1.25 |
| `docs/science` | 1.15 |
| `docs/general` | 1.00 |
| `scripts` | 0.95 |
| `tests` | 0.85 |
| `assets` | 0.60 |
| `archives`, `vendor`, opaque dumps | 0.40 |
| fallback / unknown | 0.90 |

## 5. Natural normalization

Normalize all raw energies by

`E_i_tilde = E_i_raw / sum_j E_j_raw`

with the global condition

`sum_i E_i_tilde = 1`

This is the natural energy normalization of the repository state system.

## 6. Amplitude and phase

### 6.1 Amplitude

`a_i = sqrt(E_i_tilde)`

which implies

`sum_i a_i^2 = 1`

### 6.2 Base phase

`phi_i^(0) = 2 * pi * h_i`

### 6.3 Structural phase correction

The effective phase is defined by

`phi_i = mod(phi_i^(0) + Delta_phi_type(tau_i) + Delta_phi_layer(lambda_i), 2*pi)`

#### Type phase offsets

| File type group | Offset |
| --- | ---: |
| code (`py`) | `0` |
| structured config (`json`, `yaml`, `yml`, `toml`) | `pi / 8` |
| narrative docs (`md`) | `pi / 4` |
| tests | `pi / 2` |
| assets | `3*pi / 4` |
| fallback | `0` |

#### Layer phase offsets

| Layer | Offset |
| --- | ---: |
| `src/core` | `0` |
| `contracts` | `pi / 12` |
| `integration` | `pi / 10` |
| `docs/science` | `pi / 6` |
| `docs/general` | `pi / 5` |
| `tests` | `pi / 3` |
| fallback | `0` |

## 7. Local state

Define the local complex state by

`psi_i = a_i * exp(i * phi_i)`

with the global normalization condition

`sum_i |psi_i|^2 = 1`

## 8. Folder and subsystem aggregation

### Folder energy

`E(F) = sum_{i in F} E_i_tilde`

### Folder state

`Psi_F = sum_{i in F} psi_i`

### Folder phase

`Phi_F = arg(Psi_F)`

### Folder amplitude

`A_F = |Psi_F|`

This provides the minimal orbital state representation of a folder or subsystem.

## 9. Minimal coupling diagnostics

### Real coupling

`C_ij = a_i * a_j * cos(phi_i - phi_j)`

### Complex overlap form

`K_ij = psi_i * conj(psi_j)`

These are the minimal coupling diagnostics for the phased file-state system.

## 10. Canonical bootstrap formula

The canonical working formula is:

`E_i_raw = w_type(tau_i) * w_layer(lambda_i) * (1 + 0.18 * ln(1 + B_i / 1024)) * (1 + 0.12 * ln(1 + r_i)) * (0.95 + 0.10 * h_i)`

followed by:

`E_i_tilde = E_i_raw / sum_j E_j_raw`

`a_i = sqrt(E_i_tilde)`

`psi_i = a_i * exp(i * phi_i)`

## 11. Interpretation boundaries

This model is currently intended as:
- a repository-state encoding scheme,
- a normalized structural comparison model,
- a coupling and aggregation basis,
- a bridge to future orbital indexing and compression experiments.

This document does not claim:
- a physical law of nature,
- an optimal compression bound,
- cryptographic hardness,
- or a final semantic phase theory.

## 12. Immediate executable use

A minimal implementation should:
1. hash each file,
2. infer its type and layer,
3. compute raw energy,
4. normalize globally,
5. assign amplitude and phase,
6. produce `psi_i`,
7. expose folder-level aggregation and coupling diagnostics.
