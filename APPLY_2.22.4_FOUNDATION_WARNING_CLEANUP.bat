@echo off
setlocal
cd /d "%~dp0"

echo.
echo VADAFOK Studio 2.22.4 - Foundation - Warning Cleanup
echo =====================================================
echo.
python tools\apply_warning_cleanup_2_22_4.py
if errorlevel 1 (
  echo.
  echo FEHLER: Bitte Screenshot senden.
  pause
  exit /b 1
)
echo.
echo Erfolgreich angewendet.
echo Jetzt RUN_2.22.4_WARNING_CLEANUP_TESTS.bat ausfuehren.
pause
