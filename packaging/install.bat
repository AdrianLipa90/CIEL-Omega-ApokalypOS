@echo off
REM install.bat — Windows launcher for the CIEL SOT Agent PowerShell installer
REM
REM Usage:
REM   install.bat
REM   install.bat qwen2.5-0.5b-q4
REM
REM The first argument (optional) is the model key.
REM Leave empty for the default (TinyLlama 1.1B Chat Q4_K_M).

setlocal enabledelayedexpansion

set "MODEL=%~1"
if "%MODEL%"=="" set "MODEL=tinyllama-1.1b-chat-q4"

set "SCRIPT_DIR=%~dp0"

echo [ciel-install] Running CIEL SOT Agent installer...
echo [ciel-install] Model: %MODEL%
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%install.ps1" -Model "%MODEL%"

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ciel-install] Installation failed. See errors above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [ciel-install] Done. Press any key to close.
pause > nul
