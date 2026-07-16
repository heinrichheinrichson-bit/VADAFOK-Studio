@echo off
setlocal
cd /d "%~dp0"

echo.
python tools\run_basic_tests_2_22_3.py
set TEST_RESULT=%ERRORLEVEL%

echo.
if not "%TEST_RESULT%"=="0" (
    echo Mindestens ein Test ist fehlgeschlagen.
    echo Bitte den gesamten Text oder einen Screenshot senden.
) else (
    echo Alle automatisierten Basic Tests wurden bestanden.
)
pause
exit /b %TEST_RESULT%
