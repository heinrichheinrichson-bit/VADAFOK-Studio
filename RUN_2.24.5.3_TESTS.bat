@echo off
setlocal
cd /d "%~dp0"
python tools\run_tests_2_24_5_3.py
set TEST_RESULT=%ERRORLEVEL%
echo.
if not "%TEST_RESULT%"=="0" (
  echo Mindestens ein Test ist fehlgeschlagen.
) else (
  echo Alle automatisierten 2.24.5.3-Tests wurden bestanden.
)
pause
exit /b %TEST_RESULT%
