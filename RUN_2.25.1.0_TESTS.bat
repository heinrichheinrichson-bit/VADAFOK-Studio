@echo off
setlocal
cd /d "%~dp0"
echo VADAFOK Studio 2.25.1.0 - RefreshManager Foundation
echo ========================================================
python -m unittest discover -s tests -v
if errorlevel 1 goto failed
python -m compileall -q vadafok_studio
if errorlevel 1 goto failed
echo.
echo [OK] Alle automatisierten Tests und Compileall bestanden.
pause
exit /b 0
:failed
echo.
echo [FEHLER] Mindestens ein Test ist fehlgeschlagen.
pause
exit /b 1
