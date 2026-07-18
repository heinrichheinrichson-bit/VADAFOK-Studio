@echo off
setlocal
cd /d "%~dp0"
echo [1/2] compileall
python -m compileall -q vadafok_studio tests
if errorlevel 1 goto :failed
echo [2/2] unittest
python -m unittest discover -s tests -p "test_*.py"
if errorlevel 1 goto :failed
echo.
echo ALL TESTS PASSED
exit /b 0
:failed
echo.
echo TESTS FAILED
exit /b 1
