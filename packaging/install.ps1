#Requires -Version 5.1
<#
.SYNOPSIS
    Production installer for CIEL SOT Agent (Windows).

.DESCRIPTION
    Installs the CIEL SOT Agent Python package, the llama.cpp Python bindings,
    and optionally downloads a GGUF language model (TinyLlama, Qwen2.5, etc.).

.PARAMETER Model
    GGUF model key to download.  Supported values:
        tinyllama-1.1b-chat-q4   TinyLlama 1.1B Chat Q4_K_M  (~670 MB)  [DEFAULT]
        qwen2.5-0.5b-q4          Qwen 2.5 0.5B Instruct Q4_K_M (~397 MB)
        qwen2.5-1.5b-q4          Qwen 2.5 1.5B Instruct Q4_K_M (~986 MB)
        phi-2-q4                 Microsoft Phi-2 Q4_K_M (~1.6 GB)
        none                     Skip model download

.PARAMETER SkipLlamaCpp
    Skip installation of llama-cpp-python (GGUF inference will be unavailable).

.PARAMETER ModelsDir
    Custom directory for GGUF models.  Defaults to %LOCALAPPDATA%\ciel\models.

.EXAMPLE
    .\install.ps1

.EXAMPLE
    .\install.ps1 -Model qwen2.5-0.5b-q4

.EXAMPLE
    .\install.ps1 -Model none -SkipLlamaCpp
#>
[CmdletBinding()]
param(
    [string]$Model = "tinyllama-1.1b-chat-q4",
    [switch]$SkipLlamaCpp,
    [string]$ModelsDir = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step  { param([string]$Msg) Write-Host "`n==> $Msg" -ForegroundColor Cyan }
function Write-Ok    { param([string]$Msg) Write-Host "[ciel-install] $Msg" -ForegroundColor Green }
function Write-Warn  { param([string]$Msg) Write-Host "[ciel-install] WARNING: $Msg" -ForegroundColor Yellow }
function Write-Fail  { param([string]$Msg) Write-Host "[ciel-install] ERROR: $Msg" -ForegroundColor Red }

# ---------------------------------------------------------------------------
# Step 0 — Find Python 3.11+
# ---------------------------------------------------------------------------
Write-Step "Checking Python version"

$Python = $null
foreach ($candidate in @("python", "python3", "py")) {
    try {
        $ver = & $candidate -c "import sys; print(sys.version_info >= (3,11))" 2>$null
        if ($ver -eq "True") {
            $Python = $candidate
            break
        }
    } catch { }
}

if (-not $Python) {
    Write-Fail "Python 3.11 or newer is required."
    Write-Fail "Download from: https://www.python.org/downloads/"
    Write-Fail "Make sure to tick 'Add Python to PATH' during install."
    exit 1
}

$PythonVer = & $Python -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}.{v.micro}')"
Write-Ok "Python $PythonVer found."

# ---------------------------------------------------------------------------
# Detect local vendor directory for offline installation
# ---------------------------------------------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir
$VendorDir = Join-Path $ScriptDir "vendor"

$WheelCount = 0
if (Test-Path $VendorDir) {
    $WheelCount  = (Get-ChildItem -Path $VendorDir -Filter "*.whl"    -ErrorAction SilentlyContinue).Count
    $WheelCount += (Get-ChildItem -Path $VendorDir -Filter "*.tar.gz" -ErrorAction SilentlyContinue).Count
}

if ($WheelCount -gt 0) {
    Write-Ok "Offline mode — using $WheelCount pre-downloaded package(s) from: $VendorDir"
    $PipSourceArgs = @("--no-index", "--find-links", $VendorDir)
} else {
    Write-Ok "Online mode — installing from PyPI (run packaging\vendor\download_wheels.ps1 to enable offline install)."
    $PipSourceArgs = @()
}

# ---------------------------------------------------------------------------
# Step 1 — Install ciel-sot-agent
# ---------------------------------------------------------------------------
Write-Step "Installing ciel-sot-agent[gui]"

$installed = $false
try {
    & $Python -m pip install --quiet --upgrade @PipSourceArgs "ciel-sot-agent[gui]"
    $installed = $true
} catch { }

if (-not $installed) {
    Write-Warn "PyPI install failed — trying editable install from repository root"
    if (Test-Path (Join-Path $RepoRoot "pyproject.toml")) {
        & $Python -m pip install --quiet --upgrade @PipSourceArgs "$RepoRoot[gui]"
        $installed = $true
    }
}

if (-not $installed) {
    Write-Fail "Could not install ciel-sot-agent. Check your Python/pip setup."
    exit 1
}
Write-Ok "ciel-sot-agent installed."

# ---------------------------------------------------------------------------
# Step 2 — Install llama-cpp-python
# ---------------------------------------------------------------------------
if (-not $SkipLlamaCpp) {
    Write-Step "Installing llama-cpp-python (llama.cpp binaries)"
    Write-Host "  This may take a few minutes on first install."
    try {
        & $Python -m pip install --quiet @PipSourceArgs "llama-cpp-python"
        Write-Ok "llama-cpp-python installed."
    } catch {
        Write-Warn "llama-cpp-python installation failed (optional)."
        Write-Warn "Install manually:  pip install llama-cpp-python"
    }
} else {
    Write-Ok "Skipping llama-cpp-python (-SkipLlamaCpp)."
}

# ---------------------------------------------------------------------------
# Step 3 — Download GGUF model
# ---------------------------------------------------------------------------
if ($Model -eq "none") {
    Write-Ok "Skipping model download (-Model none)."
} else {
    Write-Step "Downloading GGUF model: $Model"
    Write-Host "  Available models:"
    Write-Host "    tinyllama-1.1b-chat-q4   TinyLlama 1.1B Chat Q4_K_M  ~670 MB  [DEFAULT]"
    Write-Host "    qwen2.5-0.5b-q4          Qwen2.5 0.5B Instruct Q4_K_M  ~397 MB"
    Write-Host "    qwen2.5-1.5b-q4          Qwen2.5 1.5B Instruct Q4_K_M  ~986 MB"
    Write-Host "    phi-2-q4                 Microsoft Phi-2 Q4_K_M        ~1.6 GB"
    Write-Host ""

    $installArgs = @("--model", $Model)
    if ($ModelsDir) { $installArgs += @("--models-dir", $ModelsDir) }

    try {
        & $Python -m ciel_sot_agent.gguf_manager.cli @installArgs
        Write-Ok "Model download complete."
    } catch {
        Write-Warn "Model download failed.  Download later with:"
        Write-Warn "  ciel-sot-install-model --model $Model"
    }
}

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
Write-Step "Installation complete!"
Write-Host ""
Write-Host "  Launch the GUI:    ciel-sot-gui"
Write-Host "  Download models:   ciel-sot-install-model --list"
Write-Host "                     ciel-sot-install-model --model qwen2.5-0.5b-q4"
Write-Host ""
