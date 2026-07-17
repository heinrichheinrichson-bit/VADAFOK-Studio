@echo off
setlocal
cd /d "%~dp0"

echo VADAFOK Studio 2.25.2.0 - RefreshManager Adoption Phase 1
echo =============================================================

py -m unittest discover -s tests -p "test_*.py" -v
if errorlevel 1 goto :error

echo.
echo Starte compileall ...
py -m compileall -q vadafok_studio tests run.py
if errorlevel 1 goto :error

echo.
echo [OK] Alle Tests und compileall wurden erfolgreich abgeschlossen.
pause
exit /b 0

:error
echo.
echo [FEHLER] Mindestens ein Test oder compileall ist fehlgeschlagen.
pause
exit /b 1
