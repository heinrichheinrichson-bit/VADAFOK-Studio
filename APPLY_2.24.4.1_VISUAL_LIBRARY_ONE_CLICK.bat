@echo off
setlocal
cd /d "%~dp0"
echo.
echo VADAFOK Studio 2.24.4.1 - Visual Library One-Click Apply
echo ============================================================
echo.
python tools\apply_visual_library_one_click_2_24_4_1.py
if errorlevel 1 (
  echo.
  echo FEHLER: Bitte die vollstaendige Ausgabe senden.
  pause
  exit /b 1
)
echo.
echo Erfolgreich angewendet.
echo Jetzt RUN_2.24.4.1_TESTS.bat ausfuehren.
pause
