@echo off
setlocal
cd /d "%~dp0"
echo === VADAFOK Studio 2.26.2.0 - Sound SHOW Integration ===
python -m compileall -q vadafok_studio tests || goto :error
python -m unittest discover -s tests -p "test_*.py" || goto :error
echo.
echo ALL TESTS PASSED
pause
exit /b 0
:error
echo.
echo TESTS FAILED
pause
exit /b 1
