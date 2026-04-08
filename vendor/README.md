# Vendor Bundle

This directory hosts repository-local offline dependency material.

## Current contents
- `vendor/manifests/offline_dependency_bundle_v1.yaml` — machine-readable description of the offline bundle surface.
- `vendor/wheels/runtime/` — runtime wheelhouse target.
- `vendor/wheels/dev/` — dev/test wheelhouse target.

## Important status note
The current commit scaffolds the offline bundle structure and bootstrap scripts, but does **not** embed third-party wheel binaries.
Populate the wheelhouses before treating this vendor bundle as fully offline-capable.
