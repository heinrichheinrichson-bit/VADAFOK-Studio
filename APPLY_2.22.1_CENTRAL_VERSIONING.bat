@echo off
setlocal
cd /d "%~dp0"

echo.
echo VADAFOK Studio 2.22.1 - Foundation - Central Versioning
echo ========================================================
echo.

python tools\apply_central_versioning_2_22_1.py
if errorlevel 1 (
    echo.
    echo FEHLER: Es wurde nichts Unsicheres uebernommen.
    echo Bitte den gesamten Text oder einen Screenshot senden.
    pause
    exit /b 1
)

echo.
echo Erfolgreich angewendet.
echo Bitte VADAFOK jetzt starten und den Testplan ausfuehren.
pause
