@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_ui.ps1" %*

endlocal
