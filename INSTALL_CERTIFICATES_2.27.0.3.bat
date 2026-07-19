@echo off
setlocal
cd /d "%~dp0"

echo.
echo VADAFOK Studio 2.27.0.3 - Zertifikate installieren
echo ===================================================
echo.
echo Installiere bzw. aktualisiere certifi fuer die aktive Python-Version...
py -m pip install --upgrade certifi

if errorlevel 1 (
    echo.
    echo FEHLER: certifi konnte nicht installiert werden.
    echo Bitte dieses Fenster fotografieren und die Meldung senden.
    pause
    exit /b 1
)

echo.
echo OK: certifi wurde installiert/aktualisiert.
echo VADAFOK Studio jetzt schliessen und wieder starten.
pause
