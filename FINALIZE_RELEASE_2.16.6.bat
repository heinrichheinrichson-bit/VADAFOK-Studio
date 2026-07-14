@echo off
setlocal
cd /d "%~dp0"
py tools\finalize_release_2_16_6.py
if errorlevel 1 python tools\finalize_release_2_16_6.py
if errorlevel 1 (
  echo.
  echo Finalization failed. No Git commit should be created.
  pause
  exit /b 1
)
echo.
echo Documentation was appended and obsolete TEST files were removed.
pause
