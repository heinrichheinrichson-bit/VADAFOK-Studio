@echo off
setlocal
cd /d "%~dp0"
python tools\apply_picker_mode_persistence_2_24_4_2.py
if errorlevel 1 (
  echo FEHLER: Bitte die vollstaendige Ausgabe senden.
  pause
  exit /b 1
)
echo Erfolgreich angewendet.
echo Jetzt RUN_2.24.4.2_TESTS.bat ausfuehren.
pause
