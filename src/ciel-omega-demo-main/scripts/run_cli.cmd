@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_cli.ps1" %*

endlocal
