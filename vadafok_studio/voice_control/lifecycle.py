"""PowerShell voice-listener process lifecycle."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import threading
from typing import Any


class VoiceLifecycleController:
    """Start and stop the listener without leaking processes or reader threads."""

    def __init__(self, app: Any) -> None:
        self.app = app

    @staticmethod
    def script_path() -> Path:
        return Path(__file__).resolve().parents[1] / "tools" / "voice_listener.ps1"

    def start(self) -> None:
        app = self.app
        if sys.platform != "win32":
            app.voice_status_var.set("WINDOWS ONLY")
            return
        if self._is_running():
            app.voice_status_var.set("LISTENING")
            return
        script = self.script_path()
        if not script.exists():
            app.voice_status_var.set("ERROR: voice_listener.ps1 missing")
            return

        app.voice_stop_requested = False
        app.voice_status_var.set("STARTING...")
        command = [
            "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(script), "-Culture", app.voice_culture.get().strip(),
        ]
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            app.voice_process = process
            thread = threading.Thread(
                target=app.voice_reader_loop, args=(process,), daemon=True,
                name="VADAFOK Voice Reader",
            )
            app.voice_reader_thread = thread
            thread.start()
        except Exception as error:
            app.voice_process = None
            app.voice_reader_thread = None
            app.voice_status_var.set(f"ERROR: {str(error)[:70]}")

    def stop(self) -> None:
        app = self.app
        app.voice_stop_requested = True
        process = app.voice_process
        thread = app.voice_reader_thread
        app.voice_process = None
        app.voice_reader_thread = None
        if process is not None:
            self._terminate_process(process)
        # Once stdout closes, the daemon reader should finish immediately.
        # A short join prevents an old reader racing a quick restart.
        if thread is not None and thread is not threading.current_thread():
            try:
                thread.join(timeout=0.35)
            except Exception:
                pass
        app.voice_status_var.set("OFF")

    def restart(self) -> None:
        self.stop()
        if self.app.voice_enabled.get():
            self.app.after(250, self.start)

    def toggle(self) -> None:
        self.app.save_config()
        if self.app.voice_enabled.get():
            self.start()
        else:
            self.stop()

    def test_trigger(self) -> None:
        self.app.voice_last_heard_var.set("Manual F8 test")
        self.app.open_quick_caption()

    def close_app(self) -> None:
        self.stop()
        self.app.destroy()

    def _is_running(self) -> bool:
        process = self.app.voice_process
        if process is None:
            return False
        try:
            return process.poll() is None
        except Exception:
            return False

    @staticmethod
    def _terminate_process(process: Any) -> None:
        try:
            process.terminate()
            process.wait(timeout=1.2)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass
