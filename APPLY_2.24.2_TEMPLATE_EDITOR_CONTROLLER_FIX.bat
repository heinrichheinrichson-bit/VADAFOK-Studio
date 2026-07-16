@echo off
setlocal
cd /d "%~dp0"
echo.
echo VADAFOK Studio 2.24.2.1 - Template Editor Controller Apply Fix
echo ================================================================
echo.
python tools\apply_template_editor_controller_2_24_2.py
if errorlevel 1 (
  echo.
  echo FEHLER: Bitte Screenshot senden.
  pause
  exit /b 1
)
echo.
echo Erfolgreich angewendet.
echo Danach RUN_2.24.2_TESTS.bat aus dem vorhandenen 2.24.2-Paket ausfuehren.
pause
