@echo off
setlocal
cd /d "%~dp0"
python -m compileall -q vadafok_studio tests
if errorlevel 1 exit /b 1
python -m unittest discover -s tests -p "test_*.py"
if errorlevel 1 exit /b 1
echo.
echo VADAFOK Studio 2.26.3.0 tests successful.
pause
