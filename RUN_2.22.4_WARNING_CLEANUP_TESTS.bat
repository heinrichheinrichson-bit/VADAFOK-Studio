@echo off
setlocal
cd /d "%~dp0"
python tools\run_warning_cleanup_tests_2_22_4.py
set TEST_RESULT=%ERRORLEVEL%
echo.
if not "%TEST_RESULT%"=="0" (
  echo Mindestens ein Test ist fehlgeschlagen.
) else (
  echo Alle automatisierten 2.22.4-Tests wurden bestanden.
)
pause
exit /b %TEST_RESULT%
