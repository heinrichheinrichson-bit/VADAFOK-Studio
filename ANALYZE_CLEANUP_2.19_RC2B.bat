@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0ANALYZE_CLEANUP_2.19_RC2B.ps1"

echo.
pause
