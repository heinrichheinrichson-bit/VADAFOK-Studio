@echo off
setlocal
cd /d "%~dp0"
python tools\run_tests_2_24_4_3.py
set R=%ERRORLEVEL%
pause
exit /b %R%
