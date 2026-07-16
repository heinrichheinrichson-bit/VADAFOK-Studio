@echo off
setlocal
cd /d "%~dp0"
echo.
echo VADAFOK Studio 2.24.4 - Visual Library Background Picker
echo ============================================================
echo.
python tools\apply_visual_library_background_picker_2_24_4.py
if errorlevel 1 (
  echo.
  echo FEHLER: Bitte die vollstaendige Ausgabe senden.
  pause
  exit /b 1
)
echo.
echo Erfolgreich angewendet.
echo Jetzt RUN_2.24.4_TESTS.bat ausfuehren.
pause
