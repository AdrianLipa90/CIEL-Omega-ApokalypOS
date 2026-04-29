Param(
  [string]$VenvDir = ".venv",
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$Args
)

$ErrorActionPreference = "Stop"

$exe = Join-Path $VenvDir "Scripts\ciel-cli.exe"
if (-Not (Test-Path $exe)) {
  Write-Error "Missing venv entrypoint: $exe (run scripts\\install_local.ps1 first)"
}

& $exe @Args
