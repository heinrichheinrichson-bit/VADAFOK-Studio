@echo off
setlocal
cd /d "%~dp0"

echo VADAFOK Studio 2.25.1.0a - RefreshManager Compatibility
echo ========================================================
python -m unittest discover -s tests -v
if errorlevel 1 (
  echo.
  echo [FEHLER] Mindestens ein Test ist fehlgeschlagen.
  pause
  exit /b 1
)

echo.
echo Starte compileall ...
python -m compileall -q vadafok_studio
if errorlevel 1 (
  echo.
  echo [FEHLER] compileall ist fehlgeschlagen.
  pause
  exit /b 1
)

echo.
echo [OK] Alle Tests und compileall wurden erfolgreich abgeschlossen.
pause
