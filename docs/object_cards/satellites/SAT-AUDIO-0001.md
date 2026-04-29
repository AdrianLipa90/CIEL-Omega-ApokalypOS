# SAT-AUDIO-0001 — Audio Orbital Stack

## Identity
- **subsystem_id:** `SAT-AUDIO-0001`
- **name:** `Audio Orbital Stack`
- **class:** `satellite_io_stack`
- **active_status:** `ACTIVE_OPTIONAL_IMPORT_STACK`

## Anchors
- `integration/imports/audio_orbital_stack/README.md`
- `integration/imports/audio_orbital_stack/MANIFEST.json`
- `integration/imports/audio_orbital_stack/active_pipeline_semantics.json`
- `integration/imports/audio_orbital_stack/state/audio_orbital_stack_state.json`

## Role
Local speech skeleton around Omega and Orbital.

## Flow
- **input_from:** `audio/VAD/STT`
- **output_to:** `sapiens packet -> omega/orbital -> response -> TTS`

## Authority
### May
- provide optional local audio I/O around Omega and Orbital
- normalize audio into packet-facing forms
- remain auditable as a peripheral stack

### Must not
- override canonical Omega runtime semantics
- silently import heavy models as mandatory runtime requirements
- be treated as core source of truth rather than optional I/O

## Canonical dependency
Feeds Sapiens/Omega through optional I/O path.

## Horizon relation
Peripheral I/O layer around the main surface.

## Authority rule
Kept auditable and optional; heavy models remain external until configured.
