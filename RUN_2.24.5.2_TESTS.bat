@echo off
setlocal
cd /d "%~dp0"
python tools\run_tests_2_24_5_2.py
set R=%ERRORLEVEL%
pause
exit /b %R%
