@echo off
setlocal
cd /d "%~dp0"

echo.
echo VADAFOK Studio 2.23.3 - Partial Recent Refresh
echo =================================================
echo.
python tools\apply_partial_recent_refresh_2_23_3.py
if errorlevel 1 (
  echo.
  echo FEHLER: Bitte Screenshot senden.
  pause
  exit /b 1
)
echo.
echo Erfolgreich angewendet.
echo Jetzt RUN_2.23.3_TESTS.bat ausfuehren.
pause
