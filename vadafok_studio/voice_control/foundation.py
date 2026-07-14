"""Hybrid voice control for Quick Caption.

Windows System.Speech handles fixed commands while faster-whisper handles
German and English free dictation locally.
"""

from __future__ import annotations

import re
from typing import Any

from .matcher import classify_command, match_known_phrase
from .whisper_dictation import start_whisper_dictation, stop_whisper_dictation

_INSTALLED = False

# Command phrases and matching thresholds live in voice_library.json.


def _set_status(app: Any, text: str) -> None:
    try:
        app.voice_status_var.set(text)
    except Exception:
        pass


def _set_last_heard(app: Any, text: str) -> None:
    try:
        app.voice_last_heard_var.set(text)
    except Exception:
        pass


def _normalize(value: Any) -> str:
    text = str(value or "").strip().casefold()
    # Speech recognition may add terminal punctuation. Commands should still
    # work for results such as "Show." or "Senden!".
    text = re.sub(r"[^\wäöüß]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def _quick_caption_is_open(app: Any) -> bool:
    try:
        return bool(app.quick_window and app.quick_window.winfo_exists())
    except Exception:
        return False


def _quick_caption_text(app: Any) -> str:
    entry = getattr(app, "quick_caption_entry", None)
    if entry is None:
        return ""
    try:
        return entry.get("1.0", "end").strip()
    except Exception:
        return ""


def _append_quick_caption_text(app: Any, text: str) -> bool:
    """Append one recognized phrase to the open Quick Caption text box."""

    phrase = str(text or "").strip()
    if not phrase or not _quick_caption_is_open(app):
        return False

    entry = getattr(app, "quick_caption_entry", None)
    if entry is None:
        return False

    try:
        existing = entry.get("1.0", "end").strip()
        if existing:
            entry.insert("end", " " + phrase)
        else:
            entry.insert("1.0", phrase)
        entry.mark_set("insert", "end")
        entry.see("end")
        entry.focus_set()
        return True
    except Exception:
        return False




def _clear_quick_caption(app: Any) -> bool:
    if not _quick_caption_is_open(app):
        _set_status(app, "WARNING: Quick Caption is not open")
        return False

    entry = getattr(app, "quick_caption_entry", None)
    if entry is None:
        _set_status(app, "WARNING: Quick Caption input is unavailable")
        return False

    try:
        entry.delete("1.0", "end")
        entry.focus_set()
        _set_status(app, "DICTATING · text cleared · say VADAFOK SHOW to send")
        return True
    except Exception as exc:
        _set_status(app, f"ERROR: Quick Caption could not be cleared · {str(exc)[:70]}")
        return False


def _cancel_quick_caption(app: Any) -> bool:
    if not _quick_caption_is_open(app):
        _set_status(app, "WARNING: Quick Caption is not open")
        return False

    try:
        app.voice_dictation_active = False
        stop_whisper_dictation(app)
        app.quick_window.destroy()
        app.quick_window = None
        app.after(150, lambda: _return_to_listening(app))
        return True
    except Exception as exc:
        app.voice_dictation_active = True
        _set_status(app, f"ERROR: Quick Caption could not close · {str(exc)[:75]}")
        return False


def _handle_whisper_text(app: Any, text: str) -> None:
    """Insert one Whisper result on the Tk main thread."""

    if not getattr(app, "voice_dictation_active", False):
        return
    if not _quick_caption_is_open(app):
        stop_whisper_dictation(app)
        return

    command = classify_command(text)
    if command.wake_detected:
        # Command audio is handled by the Windows command grammar. Never place
        # a VADAFOK phrase in the visible caption.
        return

    phrase_match = match_known_phrase(text)
    insert_text = phrase_match.text if phrase_match is not None else text
    if _append_quick_caption_text(app, insert_text):
        if phrase_match is not None:
            _set_status(
                app,
                f"WHISPER · matched {phrase_match.source} · {phrase_match.score:.0%}",
            )
        else:
            _set_status(app, "WHISPER DICTATING · say VADAFOK SHOW to send")


def _activate_dictation(app: Any) -> None:
    app.voice_dictation_active = True
    _set_status(app, "WHISPER STARTING · first model load can take a while")

    def on_text(value: str) -> None:
        app.after(0, lambda text=value: _handle_whisper_text(app, text))

    def on_status(value: str) -> None:
        app.after(0, lambda text=value: _set_status(app, text))

    try:
        start_whisper_dictation(app, on_text=on_text, on_status=on_status)
    except Exception as exc:
        _set_status(app, f"WHISPER ERROR · {str(exc)[:90]}")


def _return_to_listening(app: Any) -> None:
    if not getattr(app, "voice_stop_requested", False):
        _set_status(app, "LISTENING · waiting for Live Card")


def _send_quick_caption_with_existing_action(app: Any) -> bool:
    """Trigger the existing Quick Caption Enter/SHOW action.

    The original application binds Return in the Quick Caption textbox to the
    same local function used by the SHOW button. Generating Return therefore
    reuses the application's existing send path instead of implementing a
    second OBS path in the voice module.
    """

    if not _quick_caption_is_open(app):
        _set_status(app, "WARNING: Quick Caption is not open")
        return False

    if not _quick_caption_text(app):
        _set_status(app, "WARNING: Quick Caption is empty · nothing sent")
        return False

    entry = getattr(app, "quick_caption_entry", None)
    if entry is None:
        _set_status(app, "WARNING: Quick Caption input is unavailable")
        return False

    app.voice_dictation_active = False
    stop_whisper_dictation(app)
    _set_status(app, "SENDING · Quick Caption")

    try:
        # This invokes the existing Return binding, which calls the exact same
        # send function as the SHOW button in app.py.
        entry.event_generate("<Return>")
        app.after(350, lambda: _return_to_listening(app))
        return True
    except Exception as exc:
        app.voice_dictation_active = True
        _set_status(app, f"ERROR: Quick Caption could not be sent · {str(exc)[:75]}")
        return False


def _handle_heard(
    app: Any,
    heard: str,
    confidence: str = "",
    grammar_kind: str = "",
) -> None:
    text = str(heard or "").strip()
    if not text:
        return

    grammar_label = str(grammar_kind or "").strip()
    suffix = f"  [{confidence}]" if confidence else ""
    if grammar_label:
        suffix += f"  · {grammar_label}"
    _set_last_heard(app, text + suffix)

    try:
        trigger = _normalize(app.voice_trigger_phrase.get())
    except Exception:
        trigger = "live card"

    normalized = _normalize(text)

    # Wake command. Use exact matching so normal dictated sentences that happen
    # to contain the words "live card" are not treated as commands.
    if trigger and normalized == trigger:
        _set_status(app, "COMMAND DETECTED · opening Quick Caption")
        try:
            app.open_quick_caption()
            app.after(100, lambda: _activate_dictation(app))
        except Exception as exc:
            app.voice_dictation_active = False
            _set_status(app, f"ERROR: Quick Caption could not open · {str(exc)[:80]}")
        return

    if not getattr(app, "voice_dictation_active", False):
        return

    if not _quick_caption_is_open(app):
        app.voice_dictation_active = False
        stop_whisper_dictation(app)
        _set_status(app, "LISTENING · Quick Caption closed")
        return

    # During dictation, Windows Speech is command-only. Whisper supplies the
    # free text. Ignore any non-command result from System.Speech.
    if grammar_label and grammar_label != "command":
        return

    # Fuzzy command matching is restricted to wake-word phrases. Unknown
    # phrases that resemble a VADAFOK command are blocked so they can never
    # appear in the visible banner.
    command = classify_command(text)
    if command.action == "show":
        _send_quick_caption_with_existing_action(app)
        return

    if command.action == "reset":
        _clear_quick_caption(app)
        return

    if command.action == "stop":
        _cancel_quick_caption(app)
        return

    if command.wake_detected:
        _set_status(
            app,
            "COMMAND NOT RECOGNIZED · use VADAFOK SHOW / RESET / STOP",
        )
        return

    # Non-command speech is transcribed by Whisper and arrives through
    # _handle_whisper_text().
    return


def _voice_reader_loop(self: Any, process: Any) -> None:
    """Read structured output from the PowerShell listener."""

    saw_error = False
    try:
        while not getattr(self, "voice_stop_requested", False):
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
                self.after(0, lambda value=label: _set_status(self, value))

            elif line.startswith("__HEARD__|"):
                parts = line.split("|", 3)
                confidence = parts[1] if len(parts) > 1 else ""
                grammar_kind = parts[2] if len(parts) > 2 else ""
                heard = parts[3] if len(parts) > 3 else ""

                # Compatibility with TEST01 protocol.
                if len(parts) == 3:
                    heard = parts[2]
                    grammar_kind = ""

                self.after(
                    0,
                    lambda value=heard, conf=confidence, kind=grammar_kind: _handle_heard(
                        self, value, conf, kind
                    ),
                )

            elif line.startswith("__WARN__|"):
                warning = line.split("|", 1)[1]
                self.after(
                    0,
                    lambda value=warning: _set_status(self, f"WARNING: {value[:110]}"),
                )

            elif line.startswith("__ERROR__|"):
                saw_error = True
                error = line.split("|", 1)[1]
                self.after(
                    0,
                    lambda value=error: _set_status(self, f"ERROR: {value[:110]}"),
                )

            else:
                self.after(0, lambda value=line: _handle_heard(self, value))

    except Exception as exc:
        if not getattr(self, "voice_stop_requested", False):
            saw_error = True
            message = str(exc)
            self.after(
                0,
                lambda value=message: _set_status(self, f"ERROR: {value[:110]}"),
            )
    finally:
        if getattr(self, "voice_stop_requested", False) or saw_error:
            return

        try:
            exit_code = process.poll()
        except Exception:
            exit_code = None

        detail = f" · exit {exit_code}" if exit_code is not None else ""
        self.after(0, lambda: _set_status(self, f"STOPPED{detail}"))


def install_voice_foundation() -> None:
    """Install the hybrid voice-control integration."""

    global _INSTALLED
    if _INSTALLED:
        return

    from vadafok_studio.app import VadafokStudio
    from vadafok_studio.version import APP_TITLE, VERSION

    original_init = VadafokStudio.__init__
    original_build_sidebar = VadafokStudio.build_sidebar

    def release_init(self: Any, *args: Any, **kwargs: Any) -> None:
        original_init(self, *args, **kwargs)
        try:
            self.wm_title(APP_TITLE)
        except Exception:
            pass

    def release_build_sidebar(self: Any, *args: Any, **kwargs: Any) -> Any:
        result = original_build_sidebar(self, *args, **kwargs)
        try:
            for widget in self.sidebar.winfo_children():
                try:
                    text = str(widget.cget("text"))
                except Exception:
                    continue
                if text.startswith("Studio "):
                    widget.configure(text=f"Studio {VERSION}")
                    break
        except Exception:
            pass
        return result

    VadafokStudio.__init__ = release_init
    VadafokStudio.build_sidebar = release_build_sidebar
    VadafokStudio.voice_reader_loop = _voice_reader_loop
    _INSTALLED = True
