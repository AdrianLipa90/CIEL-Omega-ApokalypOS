#!/usr/bin/env bash
# build_deb.sh — Build the ciel-sot-agent .deb package.
#
# Usage (from repo root or from packaging/deb/):
#   bash packaging/deb/build_deb.sh
#
# Output:
#   dist/ciel-sot-agent_<version>_all.deb

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DIST_DIR="${REPO_ROOT}/dist"

# Read version from VERSION file
VERSION_FILE="${REPO_ROOT}/VERSION"
if [[ ! -f "${VERSION_FILE}" ]]; then
    echo "ERROR: VERSION file not found at ${VERSION_FILE}" >&2
    exit 1
fi
VERSION="$(tr -d '[:space:]' < "${VERSION_FILE}")"

PACKAGE="ciel-sot-agent"
OUTPUT="${DIST_DIR}/${PACKAGE}_${VERSION}_all.deb"

echo "[build_deb] Building ${PACKAGE} ${VERSION}..."

# Update version in DEBIAN/control
CONTROL="${SCRIPT_DIR}/DEBIAN/control"
sed -i "s/^Version:.*/Version: ${VERSION}/" "${CONTROL}"

# Ensure DEBIAN scripts are executable
chmod 0755 "${SCRIPT_DIR}/DEBIAN/postinst"
chmod 0755 "${SCRIPT_DIR}/DEBIAN/prerm"

# Ensure launcher is executable
chmod 0755 "${SCRIPT_DIR}/usr/bin/ciel-sot-gui"

# Create dist directory
mkdir -p "${DIST_DIR}"

# Build the package
dpkg-deb --build "${SCRIPT_DIR}" "${OUTPUT}"

echo "[build_deb] Package built: ${OUTPUT}"
