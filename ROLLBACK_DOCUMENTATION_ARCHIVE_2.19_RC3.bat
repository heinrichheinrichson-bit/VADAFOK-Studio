@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0ROLLBACK_DOCUMENTATION_ARCHIVE_2.19_RC3.ps1"
echo.
pause
