#!/usr/bin/env bash
# download_wheels.sh — Pre-download all required Python wheels for offline installation.
#
# Run this script ONCE on a machine with internet access to populate the vendor/
# directory.  Afterwards the main installer (packaging/install.sh) will use these
# cached wheels and work completely offline.
#
# Usage:
#   bash packaging/vendor/download_wheels.sh
#   # or from the packaging/vendor/ directory:
#   bash download_wheels.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

log_info()  { echo -e "${GREEN}[vendor]${RESET} $*"; }
log_warn()  { echo -e "${YELLOW}[vendor] WARNING:${RESET} $*"; }
log_error() { echo -e "${RED}[vendor] ERROR:${RESET} $*" >&2; }
log_step()  { echo -e "\n${BOLD}==> $*${RESET}"; }

# ---------------------------------------------------------------------------
# Locate Python 3.11+
# ---------------------------------------------------------------------------
PYTHON=""
for candidate in python3.12 python3.11 python3 python; do
    if command -v "${candidate}" &>/dev/null; then
        ver=$("${candidate}" -c "import sys; print(sys.version_info >= (3,11))" 2>/dev/null || echo "False")
        if [[ "${ver}" == "True" ]]; then
            PYTHON="${candidate}"
            break
        fi
    fi
done

if [[ -z "${PYTHON}" ]]; then
    log_error "Python 3.11 or newer is required to download wheels."
    exit 1
fi

PYTHON_VER=$("${PYTHON}" -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}')")
log_info "Using Python ${PYTHON_VER} at $(command -v "${PYTHON}")"

# ---------------------------------------------------------------------------
# Packages to vendor (pinned runtime + gui dependencies)
# ---------------------------------------------------------------------------
PACKAGES=(
    "PyYAML==6.0.1"
    "numpy==2.4.4"
    "flask==3.1.3"
    "Werkzeug>=3.0"
    "Jinja2>=3.1"
    "itsdangerous>=2.1"
    "click>=8.1"
    "MarkupSafe>=2.1"
    "scipy>=1.11"
    "requests>=2.31"
)

log_step "Downloading wheels to: ${SCRIPT_DIR}"
log_info "Packages: ${PACKAGES[*]}"
echo ""

"${PYTHON}" -m pip download \
    --dest "${SCRIPT_DIR}" \
    --prefer-binary \
    "${PACKAGES[@]}"

echo ""
WHEEL_COUNT=$(find "${SCRIPT_DIR}" -maxdepth 1 -name "*.whl" -o -name "*.tar.gz" | wc -l)
log_info "Done — ${WHEEL_COUNT} package file(s) downloaded to: ${SCRIPT_DIR}"
log_info "You can now run packaging/install.sh offline."
