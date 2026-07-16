@echo off
setlocal
cd /d "%~dp0"
python tools\apply_template_editor_controller_2_24_2.py
if errorlevel 1 (
  echo FEHLER: Bitte Screenshot senden.
  pause
  exit /b 1
)
echo Erfolgreich angewendet.
echo Jetzt RUN_2.24.2_TESTS.bat ausfuehren.
pause
