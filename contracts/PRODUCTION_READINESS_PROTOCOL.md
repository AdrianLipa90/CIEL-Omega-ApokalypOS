# Production Readiness Protocol

## Purpose

This contract prevents false-positive claims that the repository is production ready.
A repository may be described as **tested**, **operationally useful**, or **production ready** only if the matching gate below is explicitly satisfied.

## Allowed status labels

### 1. Tested
May be used only if:
- local automated tests pass,
- the exact test command is stated,
- the scope of those tests is stated.

### 2. Operational Preview
May be used only if:
- `Tested` is satisfied,
- known limitations are listed,
- packaging and deployment status are stated.

### 3. Production Ready
May be used only if **all** of the following are true:
- the repository is installable from the root,
- CI runs automatically on pull requests,
- lint and tests are gating checks,
- runtime dependencies are declared,
- a version is defined,
- a changelog exists,
- rollback or release traceability exists through tags or release commits,
- all open blockers are stated as zero.

If any item above is false or unknown, the only valid label is **not production ready**.

## Scope-separated readiness rule

For multi-repository systems, every readiness claim must state both:
- the repository being assessed,
- the execution mode being assessed.

Examples of execution mode include:
- `core_only`
- `sot_agent_without_desktop`
- `desktop_runtime`
- `gguf`
- `no_gguf`
- `audio_in`
- `audio_out`
- `stt`
- `tts`

A downstream desktop runtime may not be described as tested, operational, or production ready from SoT-side bindings alone.
If the runtime was not executed in the repository that owns it, the claim must stay scoped to binding, contract, or documentation status.

## Evidence classes

Every concrete claim in a readiness audit must be marked as one of:
- `run_and_measured`
- `inferred_from_code`
- `documented_but_not_run`
- `unverified`

## Mandatory response format for future audits

Any readiness assessment must contain these fields:
- `repository_scope`
- `execution_mode`
- `status_label`
- `evidence`
- `evidence_class`
- `performance_evidence`
- `blockers`
- `unknowns`
- `next_actions`

## Forbidden behavior

The following are contract violations:
- claiming production readiness from passing tests alone,
- collapsing a binding declaration into a runtime certification,
- hiding missing packaging, CI, or versioning,
- collapsing unknowns into assumptions,
- using vague phrases such as “should be fine” in place of evidence.

## Release gate checklist

A release candidate can be called production ready only after this command path succeeds and its outputs are attached to the audit:

```bash
python -m pip install -e .[dev]
ruff check src/ciel_sot_agent
pytest
```

## Breach handling

If a prior readiness claim is found to be false, the next response must:
1. state the incorrect claim,
2. state the missing evidence,
3. list the concrete blockers,
4. provide the branch or patch that remedies them.
