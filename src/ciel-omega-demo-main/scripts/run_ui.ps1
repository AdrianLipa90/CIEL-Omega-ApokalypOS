Param(
  [string]$VenvDir = ".venv",
  [string]$HostAddr = "127.0.0.1",
  [int]$Port = 8080
)

$ErrorActionPreference = "Stop"

$exe = Join-Path $VenvDir "Scripts\ciel-omega.exe"
if (-Not (Test-Path $exe)) {
  Write-Error "Missing venv entrypoint: $exe (run scripts\\install_local.ps1 first)"
}

$env:CIEL_HOST = $HostAddr
$env:CIEL_PORT = "$Port"

& $exe
