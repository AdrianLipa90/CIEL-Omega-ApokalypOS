# Install/runtime fix artifacts

This branch contains a patch artifact for the packaging/runtime fix that makes the bridge installable and runnable after installation.

## Files
- `fix/ciel_install_runtime_fix.patch` — unified patch to apply at repo root

## Suggested usage
```bash
git checkout fix/install-runtime-patch-artifacts-20260404
git apply fix/ciel_install_runtime_fix.patch
# inspect changes
git add -A
git commit -m "Apply install/runtime bridge fix"
```

## Validation
```bash
pip install -e .
CIEL_SOT_ROOT=$PWD ciel-sot-orbital-bridge
CIEL_SOT_ROOT=$PWD ciel-sot-sapiens-client "test"
```
