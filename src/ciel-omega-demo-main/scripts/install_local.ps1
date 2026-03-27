Param(
  [string]$PythonBin = "python",
  [string]$VenvDir = ".venv",
  [int]$InstallLlama = 0,
  [ValidateSet("cpu","cuda")][string]$LlamaBackend = "cpu"
)

$ErrorActionPreference = "Stop"

$pythonExe = $PythonBin
$venvPython = Join-Path $VenvDir "Scripts\python.exe"
$venvPip = Join-Path $VenvDir "Scripts\pip.exe"

& $pythonExe -m venv $VenvDir

& $venvPython -m pip install --upgrade pip

if ($InstallLlama -eq 1) {
  if ($LlamaBackend -eq "cuda") {
    $env:CMAKE_ARGS = "-DLLAMA_CUBLAS=on"
    $env:FORCE_CMAKE = "1"
  }
  & $venvPip install -e ".[llama]"
} else {
  & $venvPip install -e .
}

Write-Host ""
Write-Host "Installed."
Write-Host "Run UI:   $VenvDir\Scripts\ciel-omega.exe"
Write-Host "Run CLI:  $VenvDir\Scripts\ciel-cli.exe list"
Write-Host ""
