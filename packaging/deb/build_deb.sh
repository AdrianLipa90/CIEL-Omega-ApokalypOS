#!/usr/bin/env bash
# build_deb.sh — Build the ciel-sot-agent .deb package.
#
# Usage (from repo root or from packaging/deb/):
#   bash packaging/deb/build_deb.sh
#
# Output:
#   dist/ciel-sot-agent_<version>_all.deb
#
# What this script does:
#   1. Builds the ciel-sot-agent Python wheel from the repo source.
#   2. Downloads all runtime + GUI dependency wheels (binary-only, no
#      source builds) so the resulting .deb is self-contained and can be
#      installed completely offline.
#   3. Assembles a clean staging directory from the deb skeleton and the
#      bundled wheels.
#   4. Runs dpkg-deb --build to produce the final .deb archive.
#
# Requirements on the build machine:
#   python3 >= 3.11   (with pip — install via: python3 -m ensurepip --upgrade)
#   dpkg-deb          (pre-installed on all Debian/Ubuntu/Mint systems)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DIST_DIR="${REPO_ROOT}/dist"

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------
VERSION_FILE="${REPO_ROOT}/VERSION"
if [[ ! -f "${VERSION_FILE}" ]]; then
    echo "ERROR: VERSION file not found at ${VERSION_FILE}" >&2
    exit 1
fi
VERSION="$(tr -d '[:space:]' < "${VERSION_FILE}")"

PACKAGE="ciel-sot-agent"
OUTPUT="${DIST_DIR}/${PACKAGE}_${VERSION}_all.deb"

echo "[build_deb] Building ${PACKAGE} ${VERSION}..."

# Verify pip is available
if ! python3 -m pip --version >/dev/null 2>&1; then
    echo "ERROR: pip is not available. Install it with: python3 -m ensurepip --upgrade" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Create a clean staging area
# ---------------------------------------------------------------------------
STAGING="$(mktemp -d /tmp/ciel-sot-deb-XXXXXX)"
trap 'rm -rf "${STAGING}"' EXIT

# Copy the entire deb skeleton (DEBIAN/, usr/, var/, opt/ layout)
cp -a "${SCRIPT_DIR}/." "${STAGING}/"

# Remove git-only placeholders that must not appear in the installed package
find "${STAGING}" -name ".gitkeep" -delete

# ---------------------------------------------------------------------------
# Update version in DEBIAN/control
# ---------------------------------------------------------------------------
sed -i "s/^Version:.*/Version: ${VERSION}/" "${STAGING}/DEBIAN/control"

# ---------------------------------------------------------------------------
# Build the ciel-sot-agent wheel and bundle all dependency wheels
# ---------------------------------------------------------------------------
WHEELS_DIR="${STAGING}/opt/ciel-sot-agent/wheels"
mkdir -p "${WHEELS_DIR}"

echo "[build_deb] Building wheel from source..."
python3 -m pip wheel \
    --quiet \
    --no-deps \
    --wheel-dir "${WHEELS_DIR}" \
    "${REPO_ROOT}"

echo "[build_deb] Downloading dependency wheels (offline bundle)..."
python3 -m pip wheel \
    --quiet \
    --wheel-dir "${WHEELS_DIR}" \
    "${REPO_ROOT}[gui]"

# ---------------------------------------------------------------------------
# Fix permissions
# ---------------------------------------------------------------------------
chmod 0755 "${STAGING}/DEBIAN/postinst"
chmod 0755 "${STAGING}/DEBIAN/prerm"
chmod 0755 "${STAGING}/DEBIAN/postrm"
find "${STAGING}/usr/bin" -type f -exec chmod 0755 {} +

# ---------------------------------------------------------------------------
# Build the package
# ---------------------------------------------------------------------------
mkdir -p "${DIST_DIR}"
dpkg-deb --build "${STAGING}" "${OUTPUT}"

echo "[build_deb] Package built: ${OUTPUT}"
