@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo VADAFOK Studio 2.25.4.0 - RefreshProfiler Developer View
echo ============================================================
echo.

set "PYTHON_CMD=python"
where py >nul 2>nul
if not errorlevel 1 set "PYTHON_CMD=py -3"

echo [1/3] Vollstaendige Testsuite...
%PYTHON_CMD% -m unittest discover -s tests -p "test_*.py"
if errorlevel 1 goto :failed

echo.
echo [2/3] Gezielte Developer-View-Tests...
%PYTHON_CMD% -m unittest tests.test_template_refresh_profiler_developer_view
if errorlevel 1 goto :failed

echo.
echo [3/3] Compileall...
%PYTHON_CMD% -m compileall -q vadafok_studio tests
if errorlevel 1 goto :failed

echo.
echo ALLE TESTS BESTANDEN.
pause
exit /b 0

:failed
echo.
echo TESTS FEHLGESCHLAGEN. NICHT COMMITTEN.
pause
exit /b 1
