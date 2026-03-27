Param(
  [string]$PythonBin = "python"
)

$ErrorActionPreference = "Stop"

& $PythonBin -m pip install --upgrade pip
& $PythonBin -m pip install -e ".[bundle]"
& $PythonBin scripts\build_bundle.py
