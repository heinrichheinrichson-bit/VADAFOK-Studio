@echo off
setlocal
cd /d "%~dp0"
python tools\apply_explicit_picker_return_2_24_4_3.py
if errorlevel 1 (
 echo FEHLER: Bitte Ausgabe senden.
 pause
 exit /b 1
)
echo Erfolgreich angewendet.
echo Jetzt RUN_2.24.4.3_TESTS.bat ausfuehren.
pause
