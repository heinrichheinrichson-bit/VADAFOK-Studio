@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0ANALYZE_CLEANUP_2.19_RC2.ps1"
set RC=%ERRORLEVEL%
echo.
if %RC%==0 (
  echo Analysis complete. No project files were moved or deleted.
  echo Reports: docs\cleanup_reports\2.19_RC2
) else (
  echo Analysis failed with exit code %RC%.
)
echo.
pause
exit /b %RC%
