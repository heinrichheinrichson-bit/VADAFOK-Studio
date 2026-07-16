@echo off
setlocal
cd /d "%~dp0"

echo.
echo VADAFOK Studio 2.23.4 - Partial Template Selection
echo ====================================================
echo.
python tools\apply_partial_template_selection_2_23_4.py
if errorlevel 1 (
  echo.
  echo FEHLER: Bitte Screenshot senden.
  pause
  exit /b 1
)
echo.
echo Erfolgreich angewendet.
echo Jetzt RUN_2.23.4_TESTS.bat ausfuehren.
pause
