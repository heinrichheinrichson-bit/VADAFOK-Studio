@echo off
setlocal
cd /d "%~dp0"
python tools\run_tests_2_24_4_1.py
set TEST_RESULT=%ERRORLEVEL%
echo.
if not "%TEST_RESULT%"=="0" (
  echo Mindestens ein Test ist fehlgeschlagen.
) else (
  echo Alle automatisierten 2.24.4.1-Tests wurden bestanden.
)
pause
exit /b %TEST_RESULT%
