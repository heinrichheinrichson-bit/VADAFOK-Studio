@echo off
setlocal
cd /d "%~dp0"
echo.
echo VADAFOK Studio 2.24.5 - Foundation - Library Controller
echo ===========================================================
echo.
python tools\apply_library_controller_2_24_5.py
if errorlevel 1 (
  echo.
  echo FEHLER: Bitte die vollstaendige Ausgabe senden.
  pause
  exit /b 1
)
echo.
echo Erfolgreich angewendet.
echo Jetzt RUN_2.24.5_TESTS.bat ausfuehren.
pause
