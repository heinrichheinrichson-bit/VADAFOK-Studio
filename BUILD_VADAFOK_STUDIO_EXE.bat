@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title VADAFOK Studio Launcher Build

set "PROJECT_DIR=%CD%"
set "LAUNCHER_SOURCE=%PROJECT_DIR%\launcher\vadafok_launcher.py"
set "VERSION_FILE=%PROJECT_DIR%\launcher\version_info.txt"
set "ICON_FILE=%PROJECT_DIR%\assets\icons\vadafok_icon.ico"
set "BUILD_ROOT=%PROJECT_DIR%\launcher_build"
set "DIST_DIR=%BUILD_ROOT%\dist"
set "WORK_DIR=%BUILD_ROOT%\work"

echo ============================================================
echo   VADAFOK Studio - Windows Launcher bauen
echo ============================================================
echo.

if not exist "%PROJECT_DIR%\run.py" goto :missing_run
if not exist "%LAUNCHER_SOURCE%" goto :missing_source
if not exist "%VERSION_FILE%" goto :missing_version
if not exist "%ICON_FILE%" goto :missing_icon

where py >nul 2>nul
if errorlevel 1 goto :missing_py

echo [1/4] Python wird geprueft ...
py -c "import sys; print(sys.version)"
if errorlevel 1 goto :failed

echo.
echo [2/4] PyInstaller wird geprueft ...
py -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo PyInstaller ist noch nicht installiert. Installation beginnt ...
    py -m pip install --user --upgrade pyinstaller
    if errorlevel 1 goto :failed
)

echo.
echo [3/4] Launcher wird gebaut ...
if exist "%BUILD_ROOT%" rmdir /s /q "%BUILD_ROOT%"

py -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name "VADAFOK Studio" ^
  --icon "%ICON_FILE%" ^
  --version-file "%VERSION_FILE%" ^
  --distpath "%DIST_DIR%" ^
  --workpath "%WORK_DIR%" ^
  --specpath "%BUILD_ROOT%" ^
  "%LAUNCHER_SOURCE%"
if errorlevel 1 goto :failed

if not exist "%DIST_DIR%\VADAFOK Studio.exe" goto :missing_output

echo.
echo [4/4] EXE wird in den Projektordner kopiert ...
copy /y "%DIST_DIR%\VADAFOK Studio.exe" "%PROJECT_DIR%\VADAFOK Studio.exe" >nul
if errorlevel 1 goto :failed

echo.
echo ============================================================
echo   ERFOLG
echo ============================================================
echo   VADAFOK Studio.exe wurde erstellt.
echo   Pfad: "%PROJECT_DIR%\VADAFOK Studio.exe"
echo.
echo   Starte sie jetzt per Doppelklick.
echo   Die bisherige BAT bleibt als Notfall-Starter erhalten.
echo ============================================================
echo.
pause
exit /b 0

:missing_run
echo FEHLER: run.py wurde im Projektordner nicht gefunden.
goto :failed

:missing_source
echo FEHLER: launcher\vadafok_launcher.py wurde nicht gefunden.
goto :failed

:missing_version
echo FEHLER: launcher\version_info.txt wurde nicht gefunden.
goto :failed

:missing_icon
echo FEHLER: assets\icons\vadafok_icon.ico wurde nicht gefunden.
goto :failed

:missing_py
echo FEHLER: Der Python Launcher 'py' wurde nicht gefunden.
echo Der bisherige Befehl 'py run.py' muss funktionieren.
goto :failed

:missing_output
echo FEHLER: PyInstaller meldete keinen Fehler, aber die EXE fehlt.
goto :failed

:failed
echo.
echo ============================================================
echo   BUILD FEHLGESCHLAGEN
echo ============================================================
echo Bitte dieses Fenster offen lassen und die Fehlermeldung senden.
echo.
pause
exit /b 1
