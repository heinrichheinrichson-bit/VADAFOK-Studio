@echo off
setlocal
cd /d "%~dp0"
python tools\apply_card_creator_recent_templates_2_23_1.py
if errorlevel 1 (
 echo FEHLER: Bitte Screenshot senden.
 pause
 exit /b 1
)
echo Erfolgreich angewendet.
echo Jetzt RUN_2.23.1_TESTS.bat ausfuehren.
pause
