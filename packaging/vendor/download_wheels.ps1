#Requires -Version 5.1
<#
.SYNOPSIS
    Pre-download all required Python wheels for offline installation (Windows).

.DESCRIPTION
    Run this script ONCE on a machine with internet access to populate the vendor\
    directory.  Afterwards the main installer (packaging\install.ps1) will use these
    cached wheels and work completely offline.

.EXAMPLE
    .\packaging\vendor\download_wheels.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step  { param([string]$Msg) Write-Host "`n==> $Msg" -ForegroundColor Cyan }
function Write-Ok    { param([string]$Msg) Write-Host "[vendor] $Msg" -ForegroundColor Green }
function Write-Warn  { param([string]$Msg) Write-Host "[vendor] WARNING: $Msg" -ForegroundColor Yellow }
function Write-Fail  { param([string]$Msg) Write-Host "[vendor] ERROR: $Msg" -ForegroundColor Red }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ---------------------------------------------------------------------------
# Locate Python 3.11+
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
    Write-Fail "Python 3.11 or newer is required to download wheels."
    Write-Fail "Download from: https://www.python.org/downloads/"
    exit 1
}

$PythonVer = & $Python -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}')"
Write-Ok "Using Python $PythonVer"

# ---------------------------------------------------------------------------
# Packages to vendor (pinned runtime + gui dependencies)
# ---------------------------------------------------------------------------
$Packages = @(
    "PyYAML==6.0.1",
    "numpy==2.4.4",
    "flask==3.1.3",
    "Werkzeug>=3.0",
    "Jinja2>=3.1",
    "itsdangerous>=2.1",
    "click>=8.1",
    "MarkupSafe>=2.1",
    "scipy>=1.11",
    "requests>=2.31"
)

Write-Step "Downloading wheels to: $ScriptDir"
Write-Ok "Packages: $($Packages -join ', ')"

& $Python -m pip download `
    --dest $ScriptDir `
    --prefer-binary `
    @Packages

$WheelCount = (Get-ChildItem -Path $ScriptDir -Filter "*.whl" -ErrorAction SilentlyContinue).Count
$TarCount   = (Get-ChildItem -Path $ScriptDir -Filter "*.tar.gz" -ErrorAction SilentlyContinue).Count
$Total = $WheelCount + $TarCount
Write-Ok "Done — $Total package file(s) downloaded to: $ScriptDir"
Write-Ok "You can now run packaging\install.ps1 offline."
