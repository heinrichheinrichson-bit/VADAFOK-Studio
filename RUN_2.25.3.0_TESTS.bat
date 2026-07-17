@echo off
setlocal
cd /d "%~dp0"

echo VADAFOK Studio 2.25.3.0 - RefreshProfiler Foundation
echo ======================================================

py -m unittest discover -s tests -v
if errorlevel 1 goto :failed

echo.
echo Starte compileall ...
py -m compileall -q vadafok_studio tests
if errorlevel 1 goto :failed

echo.
echo [OK] Alle Tests und compileall wurden erfolgreich abgeschlossen.
pause
exit /b 0

:failed
echo.
echo [FEHLER] Mindestens ein Test oder compileall ist fehlgeschlagen.
pause
exit /b 1
