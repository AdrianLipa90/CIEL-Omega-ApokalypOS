@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_local.ps1" %*

endlocal
