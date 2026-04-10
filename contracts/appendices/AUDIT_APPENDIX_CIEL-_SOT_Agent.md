# Audit Appendix — CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold

## Repository
CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold

## Purpose
This appendix binds the immutable CIEL ethics core to the integration-attractor repository that hosts registries, orbital bridge logic, Sapiens interaction seed, and machine-readable audit surfaces.

## Local observables
- repository synchronization reports
- GitHub coupling reports
- orbital bridge reports
- Sapiens client and panel artifacts
- machine-readable registry and index coherence

## Scope separation
This repository is the integration kernel and Source-of-Truth side of the ecosystem.
It may certify SoT-side bindings, reports, registries, and packet-visible artifacts that are present here.

It may not claim that `CIEL-Desktop` runtime behavior is verified merely because desktop bindings are declared here.
Desktop boot, GUI behavior, audio I/O, STT, TTS, GGUF-backed inference, and other operator-surface runtime claims require evidence from the desktop repository or from a runtime environment where those paths are actually executed.

## Evidence classes
Every audit claim in this repository should be marked with exactly one of:
- `run_and_measured`
- `inferred_from_code`
- `documented_but_not_run`
- `unverified`

Unknown runtime status must remain `unverified`.
Bindings and architecture notes visible in this repository but not executed here should normally be marked `documented_but_not_run` or `inferred_from_code`, not `run_and_measured`.

## Runtime mode discipline
Audits should separate at least these modes when applicable:
- `core_only`
- `sot_agent_without_desktop`
- `desktop_binding_in_sot`
- `desktop_runtime_external`
- `gguf`
- `no_gguf`
- `audio_in`
- `audio_out`
- `stt`
- `tts`
- `panel_client_bridge`

For each mode, the audit should state:
- whether it builds,
- whether it starts,
- the concrete entrypoint,
- what behavior was directly observed,
- which dependencies are load-bearing,
- what remains a placeholder, binding, or contract-only surface.

When performance is claimed, the audit should also state the evidence class for:
- cold start,
- warm start,
- time to first response,
- resource usage.

If those measurements were not taken, the performance claim remains `unverified`.

## Runtime bindings
Representative bindings include:
- `src/ciel_sot_agent/index_validator_v2.py`
- `src/ciel_sot_agent/gh_coupling_v2.py`
- `src/ciel_sot_agent/synchronize_v2.py`
- `scripts/run_index_validator_v2.py`
- `scripts/run_gh_repo_coupling_v2.py`
- `scripts/run_repo_sync_v2.py`

## Additional thresholds
This appendix may define stricter repository-local thresholds, but it may not weaken the immutable core.

## Desktop audit boundary
In this repository, `CIEL-Desktop` is auditable as:
- a declared fixed attribute,
- a downstream dependency relation,
- a contract-visible artifact consumer,
- an SoT-facing binding target.

In this repository, `CIEL-Desktop` is not by itself audited as:
- a proven desktop boot path,
- a proven GUI runtime,
- a proven audio runtime,
- a proven local-model runtime.

Any report that collapses those categories into one readiness claim violates this appendix.

## Non-derogation clause
Nothing in this appendix may weaken:
- truth over smoothing,
- explicit uncertainty,
- marked inference,
- or the required audit channels false / unmarked / omit / hall / smooth.
