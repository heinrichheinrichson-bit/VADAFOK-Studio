@echo off
setlocal
cd /d "%~dp0"

echo.
echo VADAFOK Studio 2.25.0.1 - Template Drag Partial Refresh Tests
echo ==============================================================
echo.

python -m unittest discover -s tests -v
if errorlevel 1 goto :failed

echo.
python -m compileall vadafok_studio
if errorlevel 1 goto :failed

echo.
echo [OK] Alle automatisierten Tests bestanden.
echo [OK] Compileall bestanden.
echo.
pause
exit /b 0

:failed
echo.
echo [FEHLER] Mindestens ein Test ist fehlgeschlagen.
echo.
pause
exit /b 1
