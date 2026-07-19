@echo off
setlocal
cd /d "%~dp0"

echo.
echo VADAFOK Studio 2.27.0.5 - Zertifikate pruefen
echo ===============================================
echo.
py -m pip install --upgrade certifi

if errorlevel 1 (
    echo.
    echo FEHLER: certifi konnte nicht installiert oder aktualisiert werden.
    echo Bitte ein Foto dieser Meldung senden.
    pause
    exit /b 1
)

echo.
echo OK: Zertifikate sind aktuell.
pause
