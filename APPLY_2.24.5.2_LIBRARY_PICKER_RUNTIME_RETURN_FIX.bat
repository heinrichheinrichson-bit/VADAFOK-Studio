@echo off
setlocal
cd /d "%~dp0"
python tools\apply_library_picker_runtime_return_2_24_5_2.py
if errorlevel 1 (
 echo FEHLER: Bitte Ausgabe senden.
 pause
 exit /b 1
)
echo Erfolgreich angewendet.
echo Jetzt RUN_2.24.5.2_TESTS.bat ausfuehren.
pause
