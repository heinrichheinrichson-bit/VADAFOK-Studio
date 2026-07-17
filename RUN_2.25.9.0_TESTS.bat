@echo off
setlocal
cd /d "%~dp0"
echo === VADAFOK Studio 2.25.9.0 Tests ===
python -m unittest discover -s tests -p "test_template_refresh_*.py" -v
if errorlevel 1 goto :fail
python -m compileall -q vadafok_studio tests
if errorlevel 1 goto :fail
echo.
echo ALLE TESTS BESTANDEN.
pause
exit /b 0
:fail
echo.
echo TESTS FEHLGESCHLAGEN.
pause
exit /b 1
