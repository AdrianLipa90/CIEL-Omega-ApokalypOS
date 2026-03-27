param(
  [string]$VenvDir = ".venv",
  [string]$Host = $(if ($env:CIEL_HOST) { $env:CIEL_HOST } else { "127.0.0.1" }),
  [int]$Port = $(if ($env:CIEL_PORT) { [int]$env:CIEL_PORT } else { 8081 })
)

$python = Join-Path $VenvDir "Scripts\python.exe"
if (-not (Test-Path $python)) {
  Write-Error "Missing venv: $VenvDir (run scripts\install_local.ps1 first)"
  exit 1
}

$env:CIEL_HOST = $Host
$env:CIEL_PORT = "$Port"
& $python -m main.apps.omega_orbital_app
