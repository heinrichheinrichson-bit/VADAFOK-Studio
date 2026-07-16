@echo off
setlocal
cd /d "%~dp0"
python tools\apply_manage_recent_templates_2_23_2.py
if errorlevel 1 (
 echo FEHLER: Bitte Screenshot senden.
 pause
 exit /b 1
)
echo Erfolgreich angewendet.
echo Jetzt RUN_2.23.2_TESTS.bat ausfuehren.
pause
