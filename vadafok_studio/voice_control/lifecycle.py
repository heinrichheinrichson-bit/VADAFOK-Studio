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

    def reader_loop(self, process: Any) -> None:
        """Read and dispatch structured listener output."""
        # Imported lazily to avoid a module cycle while the optional voice
        # foundation installs its UI integrations.
        from .foundation import _handle_heard, _set_status

        app = self.app
        saw_error = False
        try:
            while not app.voice_stop_requested:
                line = process.stdout.readline()
                if line == "":
                    break
                line = line.strip()
                if not line:
                    continue
                if line.startswith("__READY__|"):
                    parts = line.split("|", 2)
                    culture = parts[1] if len(parts) > 1 else ""
                    description = parts[2] if len(parts) > 2 else ""
                    label = f"LISTENING · {culture}"
                    if description:
                        label += f" · {description}"
                    app.after(0, lambda value=label: _set_status(app, value))
                elif line.startswith("__HEARD__|"):
                    parts = line.split("|", 3)
                    confidence = parts[1] if len(parts) > 1 else ""
                    grammar_kind = parts[2] if len(parts) > 2 else ""
                    heard = parts[3] if len(parts) > 3 else ""
                    if len(parts) == 3:  # Compatibility with TEST01 protocol.
                        heard = parts[2]
                        grammar_kind = ""
                    app.after(
                        0,
                        lambda value=heard, conf=confidence, kind=grammar_kind: _handle_heard(
                            app, value, conf, kind,
                        ),
                    )
                elif line.startswith("__WARN__|"):
                    warning = line.split("|", 1)[1]
                    app.after(
                        0,
                        lambda value=warning: _set_status(
                            app, f"WARNING: {value[:110]}",
                        ),
                    )
                elif line.startswith("__ERROR__|"):
                    saw_error = True
                    error = line.split("|", 1)[1]
                    app.after(
                        0,
                        lambda value=error: _set_status(app, f"ERROR: {value[:110]}"),
                    )
                else:
                    app.after(0, lambda value=line: _handle_heard(app, value))
        except Exception as error:
            if not app.voice_stop_requested:
                saw_error = True
                message = str(error)
                app.after(
                    0,
                    lambda value=message: _set_status(app, f"ERROR: {value[:110]}"),
                )
        finally:
            if not app.voice_stop_requested and not saw_error:
                try:
                    exit_code = process.poll()
                except Exception:
                    exit_code = None
                detail = f" · exit {exit_code}" if exit_code is not None else ""
                app.after(
                    0, lambda: _set_status(app, f"STOPPED{detail}"),
                )

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
        cancel_hide = getattr(self.app, "cancel_live_card_hide_timer", None)
        if callable(cancel_hide):
            cancel_hide()
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
