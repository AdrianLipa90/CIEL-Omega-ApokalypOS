#!/usr/bin/env bash
# install.sh — Production installer for CIEL/Ω — ἀποκάλυψOS Integration Attractor and Operational Manifold
#
# One-liner usage:
#   bash <(curl -fsSL https://raw.githubusercontent.com/AdrianLipa90/CIEL-_SOT_Agent/main/packaging/install.sh)
#
# Options (set as environment variables before running):
#   CIEL_MODEL    model key to download, e.g. tinyllama-1.1b-chat-q4 (default),
#                 qwen2.5-0.5b-q4, qwen2.5-1.5b-q4, phi-2-q4, none
#   CIEL_SKIP_LLAMA_CPP  set to 1 to skip llama-cpp-python installation
#   CIEL_MODELS_DIR      custom directory for GGUF models
#
# Examples:
#   CIEL_MODEL=qwen2.5-0.5b-q4 bash install.sh
#   CIEL_MODEL=none bash install.sh   # skip model download

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
CIEL_MODEL="${CIEL_MODEL:-tinyllama-1.1b-chat-q4}"
CIEL_SKIP_LLAMA_CPP="${CIEL_SKIP_LLAMA_CPP:-0}"

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
RESET='\033[0m'

log_info()  { echo -e "${GREEN}[ciel-install]${RESET} $*"; }
log_warn()  { echo -e "${YELLOW}[ciel-install] WARNING:${RESET} $*"; }
log_error() { echo -e "${RED}[ciel-install] ERROR:${RESET} $*" >&2; }
log_step()  { echo -e "\n${BOLD}==> $*${RESET}"; }

# ---------------------------------------------------------------------------
# Step 0 — Check Python version
# ---------------------------------------------------------------------------
log_step "Checking Python version"
PYTHON=""
for candidate in python3.12 python3.11 python3; do
    if command -v "${candidate}" &>/dev/null; then
        ver=$("${candidate}" -c "import sys; print(sys.version_info >= (3,11))")
        if [[ "${ver}" == "True" ]]; then
            PYTHON="${candidate}"
            break
        fi
    fi
done

if [[ -z "${PYTHON}" ]]; then
    log_error "Python 3.11 or newer is required."
    log_error "Install it with: sudo apt install python3.11   (Debian/Ubuntu/Mint)"
    log_error "                  brew install python@3.12      (macOS)"
    exit 1
fi

PYTHON_VER=$("${PYTHON}" -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}.{v.micro}')")
log_info "Python ${PYTHON_VER} found at $(command -v "${PYTHON}")"

# ---------------------------------------------------------------------------
# Detect local vendor directory for offline installation
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENDOR_DIR="${SCRIPT_DIR}/vendor"

# Check whether vendor/ contains any wheel/sdist files
VENDOR_WHEELS=0
if [[ -d "${VENDOR_DIR}" ]]; then
    VENDOR_WHEELS=$(find "${VENDOR_DIR}" -maxdepth 1 \( -name "*.whl" -o -name "*.tar.gz" \) | wc -l)
fi

if [[ "${VENDOR_WHEELS}" -gt 0 ]]; then
    log_info "Offline mode — using ${VENDOR_WHEELS} pre-downloaded package(s) from: ${VENDOR_DIR}"
    PIP_SOURCE_ARGS=(--no-index --find-links "${VENDOR_DIR}")
else
    log_info "Online mode — installing from PyPI (run packaging/vendor/download_wheels.sh to enable offline install)."
    PIP_SOURCE_ARGS=()
fi

# ---------------------------------------------------------------------------
# Step 1 — Install the CIEL SOT Agent package
# ---------------------------------------------------------------------------
log_step "Installing ciel-sot-agent[gui]"
_pip_install_agent() {
    "${PYTHON}" -m pip install --quiet --upgrade "${PIP_SOURCE_ARGS[@]}" 'ciel-sot-agent[gui]'
}
if ! _pip_install_agent 2>/dev/null; then
    log_warn "pip install from PyPI failed — trying editable install from current directory"
    if [[ -f "${REPO_ROOT}/pyproject.toml" ]]; then
        "${PYTHON}" -m pip install --quiet --upgrade "${PIP_SOURCE_ARGS[@]}" "${REPO_ROOT}[gui]"
    else
        log_error "Could not find pyproject.toml. Run this script from within the repository."
        exit 1
    fi
fi
log_info "ciel-sot-agent installed."

# ---------------------------------------------------------------------------
# Step 2 — Install llama-cpp-python (provides the llama.cpp binary)
# ---------------------------------------------------------------------------
if [[ "${CIEL_SKIP_LLAMA_CPP}" != "1" ]]; then
    log_step "Installing llama-cpp-python (llama.cpp binaries)"
    echo "  This may take a few minutes on the first install."
    echo "  To skip, set CIEL_SKIP_LLAMA_CPP=1"
    if "${PYTHON}" -m pip install --quiet "${PIP_SOURCE_ARGS[@]}" 'llama-cpp-python'; then
        log_info "llama-cpp-python installed."
    else
        log_warn "llama-cpp-python installation failed (optional — GGUF inference will be unavailable)."
        log_warn "You can install it manually: pip install llama-cpp-python"
    fi
else
    log_info "Skipping llama-cpp-python (CIEL_SKIP_LLAMA_CPP=1)."
fi

# ---------------------------------------------------------------------------
# Step 3 — Download GGUF model
# ---------------------------------------------------------------------------
if [[ "${CIEL_MODEL}" == "none" ]]; then
    log_info "Skipping model download (CIEL_MODEL=none)."
else
    log_step "Downloading GGUF model: ${CIEL_MODEL}"
    echo "  Available models:"
    echo "    tinyllama-1.1b-chat-q4  TinyLlama 1.1B Chat Q4_K_M  ~670 MB  [DEFAULT]"
    echo "    qwen2.5-0.5b-q4         Qwen2.5 0.5B Instruct Q4_K_M  ~397 MB"
    echo "    qwen2.5-1.5b-q4         Qwen2.5 1.5B Instruct Q4_K_M  ~986 MB"
    echo "    phi-2-q4                Microsoft Phi-2 Q4_K_M        ~1.6 GB"
    echo ""
    echo "  Downloading: ${CIEL_MODEL}"

    INSTALL_CMD=("${PYTHON}" -m ciel_sot_agent.gguf_manager.cli --model "${CIEL_MODEL}")
    if [[ -n "${CIEL_MODELS_DIR:-}" ]]; then
        INSTALL_CMD+=(--models-dir "${CIEL_MODELS_DIR}")
    fi

    if "${INSTALL_CMD[@]}"; then
        log_info "Model download complete."
    else
        log_warn "Model download failed. You can download it later:"
        log_warn "  ciel-sot-install-model --model ${CIEL_MODEL}"
    fi
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
log_step "Installation complete!"
echo ""
echo "  Launch the GUI:    ciel-sot-gui"
echo "  Download models:   ciel-sot-install-model --list"
echo "                     ciel-sot-install-model --model qwen2.5-0.5b-q4"
echo ""
