@echo off
setlocal
cd /d "%~dp0"
echo VADAFOK Studio 2.25.0.5 - Incremental Properties GUI Refresh
 echo.
python -m unittest discover -s tests -v
if errorlevel 1 goto :error
python -m compileall vadafok_studio
if errorlevel 1 goto :error
echo.
echo ALLE AUTOMATISCHEN TESTS UND COMPILEALL BESTANDEN.
pause
exit /b 0
:error
echo.
echo TEST FEHLGESCHLAGEN. NOCH NICHT COMMITTEN.
pause
exit /b 1
