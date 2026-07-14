@echo off
setlocal
cd /d "%~dp0"
echo Installing VADAFOK voice dependencies...
py -m pip install --upgrade pip
if errorlevel 1 goto :fallback
py -m pip install -r requirements_voice.txt
if errorlevel 1 goto :failed
goto :success

:fallback
python -m pip install --upgrade pip
if errorlevel 1 goto :failed
python -m pip install -r requirements_voice.txt
if errorlevel 1 goto :failed

:success
echo.
echo Voice dependencies installed successfully.
pause
exit /b 0

:failed
echo.
echo Installation failed. Please copy the complete output and send it in the chat.
pause
exit /b 1
