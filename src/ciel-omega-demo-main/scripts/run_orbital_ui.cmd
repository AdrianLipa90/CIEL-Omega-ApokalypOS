@echo off
setlocal
set VENV_DIR=%1
if "%VENV_DIR%"=="" set VENV_DIR=.venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
  echo Missing venv: %VENV_DIR% ^(run scripts\install_local.cmd first^)
  exit /b 1
)
if "%CIEL_HOST%"=="" set CIEL_HOST=127.0.0.1
if "%CIEL_PORT%"=="" set CIEL_PORT=8081
"%PYTHON_EXE%" -m main.apps.omega_orbital_app
