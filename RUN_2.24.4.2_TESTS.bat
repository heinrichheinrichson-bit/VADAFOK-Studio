@echo off
setlocal
cd /d "%~dp0"
python tools\run_tests_2_24_4_2.py
set TEST_RESULT=%ERRORLEVEL%
pause
exit /b %TEST_RESULT%
