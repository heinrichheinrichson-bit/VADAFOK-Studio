@echo off
setlocal
cd /d "%~dp0"
echo VADAFOK Studio 2.25.0.2 - Tests
echo =================================
python -m unittest discover -s tests -v
if errorlevel 1 goto :fail

echo.
echo Compileall...
python -m compileall vadafok_studio
if errorlevel 1 goto :fail

echo.
echo ALLE TESTS UND COMPILEALL BESTANDEN.
pause
exit /b 0

:fail
echo.
echo TEST ODER COMPILEALL FEHLGESCHLAGEN.
pause
exit /b 1
