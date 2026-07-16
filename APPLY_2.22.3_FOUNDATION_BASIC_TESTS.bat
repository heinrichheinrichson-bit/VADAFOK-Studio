@echo off
setlocal
cd /d "%~dp0"

echo.
echo VADAFOK Studio 2.22.3 - Foundation - Basic Tests
echo ==================================================
echo.

python tools\apply_foundation_basic_tests_2_22_3.py
if errorlevel 1 (
    echo.
    echo FEHLER: Basic Tests wurden nicht sicher angewendet.
    echo Bitte den gesamten Text oder einen Screenshot senden.
    pause
    exit /b 1
)

echo.
echo Erfolgreich angewendet.
echo Jetzt bitte RUN_2.22.3_BASIC_TESTS.bat ausfuehren.
pause
