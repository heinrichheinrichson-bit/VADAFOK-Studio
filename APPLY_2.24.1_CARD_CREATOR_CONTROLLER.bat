@echo off
setlocal
cd /d "%~dp0"
python tools\apply_card_creator_controller_2_24_1.py
if errorlevel 1 (
 echo FEHLER: Bitte Screenshot senden.
 pause
 exit /b 1
)
echo Erfolgreich angewendet.
echo Jetzt RUN_2.24.1_TESTS.bat ausfuehren.
pause
