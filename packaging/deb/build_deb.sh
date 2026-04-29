#!/usr/bin/env bash
# build_deb.sh — Build the ciel-sot-agent .deb package.
#
# Usage (from repo root or from packaging/deb/):
#   bash packaging/deb/build_deb.sh
#
# Output:
#   dist/ciel-sot-agent_<version>_<arch>.deb
#
# What this script does:
#   1. Builds the ciel-sot-agent Python wheel from the repo source.
#   2. Downloads all runtime + GUI dependency wheels (binary-only, pinned
#      via constraints.txt) so the resulting .deb is self-contained and
#      can be installed completely offline.
#   3. Assembles a clean staging directory from the deb skeleton and the
#      bundled wheels.
#   4. Runs dpkg-deb --build to produce the final .deb archive.
#
# Build-time requirements (NOT shipped inside the .deb):
#   python3 >= 3.11   (with pip — install via: python3 -m ensurepip --upgrade)
#   dpkg-deb          (pre-installed on all Debian/Ubuntu/Mint systems)
#
# Runtime requirements (declared in DEBIAN/control Depends):
#   python3 >= 3.11
#   python3-venv

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

# ---------------------------------------------------------------------------
# Architecture — detect from build host
# ---------------------------------------------------------------------------
if command -v dpkg >/dev/null 2>&1; then
    DEB_ARCH="$(dpkg --print-architecture)"
else
    # Fallback for build hosts without dpkg (CI, cross-compile, etc.)
    case "$(uname -m)" in
        x86_64)  DEB_ARCH="amd64" ;;
        aarch64) DEB_ARCH="arm64" ;;
        armv7l)  DEB_ARCH="armhf" ;;
        *)       DEB_ARCH="$(uname -m)" ;;
    esac
fi

PACKAGE="ciel-sot-agent"
OUTPUT="${DIST_DIR}/${PACKAGE}_${VERSION}_${DEB_ARCH}.deb"

echo "[build_deb] Building ${PACKAGE} ${VERSION} (${DEB_ARCH})..."

# Verify pip is available
if ! python3 -m pip --version >/dev/null 2>&1; then
    echo "ERROR: pip is not available. Install it with: python3 -m ensurepip --upgrade" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Constraints file for reproducible dependency resolution
# ---------------------------------------------------------------------------
CONSTRAINTS="${SCRIPT_DIR}/constraints.txt"
if [[ ! -f "${CONSTRAINTS}" ]]; then
    echo "WARNING: constraints.txt not found at ${CONSTRAINTS}; build will use unpinned deps" >&2
fi

# ---------------------------------------------------------------------------
# Create a clean staging area
# ---------------------------------------------------------------------------
STAGING="$(mktemp -d /tmp/ciel-sot-deb-XXXXXX)"
trap 'rm -rf "${STAGING}"' EXIT

# Copy the entire deb skeleton (DEBIAN/, usr/, etc/, var/, opt/ layout)
cp -a "${SCRIPT_DIR}/." "${STAGING}/"

# Remove git-only placeholders and build-only files that must not appear
# in the installed package
find "${STAGING}" -name ".gitkeep" -delete
rm -f "${STAGING}/constraints.txt"
rm -f "${STAGING}/build_deb.sh"
rm -f "${STAGING}/README.md"

# ---------------------------------------------------------------------------
# Update version and architecture in DEBIAN/control
# ---------------------------------------------------------------------------
sed -i "s/^Version:.*/Version: ${VERSION}/" "${STAGING}/DEBIAN/control"
sed -i "s/^Architecture:.*/Architecture: ${DEB_ARCH}/" "${STAGING}/DEBIAN/control"

# ---------------------------------------------------------------------------
# Build the ciel-sot-agent wheel and bundle all dependency wheels
# ---------------------------------------------------------------------------
WHEELS_DIR="${STAGING}/opt/ciel-sot-agent/wheels"
mkdir -p "${WHEELS_DIR}"

CONSTRAINT_ARGS=()
if [[ -f "${CONSTRAINTS}" ]]; then
    CONSTRAINT_ARGS=(--constraint "${CONSTRAINTS}")
fi

echo "[build_deb] Building wheel from source..."
python3 -m pip wheel \
    --quiet \
    --no-deps \
    --wheel-dir "${WHEELS_DIR}" \
    "${REPO_ROOT}"

echo "[build_deb] Downloading dependency wheels (offline bundle, binary-only)..."
python3 -m pip wheel \
    --quiet \
    --only-binary :all: \
    "${CONSTRAINT_ARGS[@]}" \
    --wheel-dir "${WHEELS_DIR}" \
    "${REPO_ROOT}[gui]"

# ---------------------------------------------------------------------------
# Fix permissions
# ---------------------------------------------------------------------------
chmod 0755 "${STAGING}/DEBIAN/postinst"
chmod 0755 "${STAGING}/DEBIAN/prerm"
chmod 0755 "${STAGING}/DEBIAN/postrm"
find "${STAGING}/usr/bin" -type f -exec chmod 0755 {} +

# Config files should be readable by all but writable only by root
find "${STAGING}/etc" -type f -exec chmod 0644 {} +

# ---------------------------------------------------------------------------
# Build the package
# ---------------------------------------------------------------------------
mkdir -p "${DIST_DIR}"
dpkg-deb --build "${STAGING}" "${OUTPUT}"

echo "[build_deb] Package built: ${OUTPUT}"
