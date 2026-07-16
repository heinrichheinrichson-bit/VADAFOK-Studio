@echo off
setlocal
cd /d "%~dp0"

echo.
echo VADAFOK Studio 2.22.2 - Foundation - Logging
echo =================================================
echo.

python tools\apply_foundation_logging_2_22_2.py
if errorlevel 1 (
    echo.
    echo FEHLER: Logging wurde nicht sicher angewendet.
    echo Bitte den gesamten Text oder einen Screenshot senden.
    pause
    exit /b 1
)

echo.
echo Erfolgreich angewendet.
echo Bitte VADAFOK jetzt starten und den Testplan ausfuehren.
pause
