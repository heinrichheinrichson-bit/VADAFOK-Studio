@echo off
setlocal
cd /d "%~dp0"
echo.
echo VADAFOK Studio 2.25.0.3 - Automated Tests
echo ================================================
echo.
python -m unittest discover -s tests -v
if errorlevel 1 goto :fail
echo.
python -m compileall vadafok_studio
if errorlevel 1 goto :fail
echo.
echo ALL TESTS PASSED.
pause
exit /b 0

:fail
echo.
echo TESTS FAILED.
pause
exit /b 1
