"""Small Windows launcher for the live VADAFOK Studio Python project.

The frozen launcher intentionally does not bundle the Studio application. It starts
``run.py`` from the directory containing ``VADAFOK Studio.exe`` so future source
updates continue to work without rebuilding the launcher.
"""

from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

APP_NAME = "VADAFOK Studio"
LOG_NAME = "vadafok_launcher.log"
CREATE_NO_WINDOW = 0x08000000
DETACHED_PROCESS = 0x00000008


def _launcher_directory() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _write_log(base_dir: Path, message: str) -> None:
    try:
        log_path = base_dir / LOG_NAME
        timestamp = datetime.now().isoformat(timespec="seconds")
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"[{timestamp}] {message.rstrip()}\n")
    except OSError:
        pass


def _message_box(message: str, title: str = APP_NAME) -> None:
    try:
        ctypes.windll.user32.MessageBoxW(None, message, title, 0x10)
    except Exception:
        pass


def _candidate_commands(run_script: Path) -> list[list[str]]:
    commands: list[list[str]] = []

    # The user's current batch file uses the Python launcher (`py`). Its windowless
    # sibling (`pyw`) is therefore the preferred option.
    pyw = shutil.which("pyw.exe") or shutil.which("pyw")
    if pyw:
        commands.append([pyw, str(run_script)])

    pythonw = shutil.which("pythonw.exe") or shutil.which("pythonw")
    if pythonw:
        commands.append([pythonw, str(run_script)])

    # Last-resort fallback: use the normal launchers but suppress their console.
    py = shutil.which("py.exe") or shutil.which("py")
    if py:
        commands.append([py, str(run_script)])

    python = shutil.which("python.exe") or shutil.which("python")
    if python:
        commands.append([python, str(run_script)])

    return commands


def _start_studio(base_dir: Path) -> None:
    run_script = base_dir / "run.py"
    if not run_script.is_file():
        raise FileNotFoundError(
            f"run.py wurde nicht gefunden.\n\nErwarteter Pfad:\n{run_script}\n\n"
            "Lege VADAFOK Studio.exe direkt neben run.py ab."
        )

    commands = _candidate_commands(run_script)
    if not commands:
        raise RuntimeError(
            "Keine Python-Installation wurde gefunden.\n\n"
            "Der bisherige Start über 'py run.py' muss auf diesem PC funktionieren."
        )

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0

    failures: list[str] = []
    for command in commands:
        try:
            subprocess.Popen(
                command,
                cwd=str(base_dir),
                close_fds=True,
                creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
                startupinfo=startupinfo,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            _write_log(base_dir, f"Studio gestartet mit: {command[0]}")
            return
        except OSError as exc:
            failures.append(f"{command[0]}: {exc}")

    raise RuntimeError("Python konnte nicht gestartet werden:\n" + "\n".join(failures))


def main() -> int:
    base_dir = _launcher_directory()
    try:
        os.chdir(base_dir)
        _start_studio(base_dir)
        return 0
    except Exception as exc:
        details = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        _write_log(base_dir, details)
        _message_box(
            f"VADAFOK Studio konnte nicht gestartet werden.\n\n{exc}\n\n"
            f"Weitere Details stehen in:\n{base_dir / LOG_NAME}"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
