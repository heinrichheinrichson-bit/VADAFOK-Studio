@echo off
setlocal
cd /d "%~dp0"
echo.
echo VADAFOK Studio 2.24.3.1 - Partial Selection Fix
echo =================================================
echo.
python tools\apply_template_editor_partial_selection_2_24_3.py
if errorlevel 1 (
  echo.
  echo FEHLER: Bitte die vollstaendige Ausgabe senden.
  pause
  exit /b 1
)
echo.
echo Erfolgreich angewendet.
echo Danach RUN_2.24.3_TESTS.bat ausfuehren.
pause
