@echo off
setlocal
python -m compileall -q vadafok_studio tests
if errorlevel 1 exit /b 1
python -m unittest discover -s tests -p "test_*.py"
if errorlevel 1 exit /b 1
echo.
echo SOUND GUI SPRINT 2 TESTS: OK
endlocal
