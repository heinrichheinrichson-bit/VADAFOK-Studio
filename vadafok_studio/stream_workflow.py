"""Stream Workflow improvements for VADAFOK Studio 2.18 RC1D.

This runtime extension keeps the large app.py untouched. It adds:
- OBS Workflow as the startup page.
- Session-only Quick Caption draft recovery.
- A visible live voice-status line in Quick Caption.
- A consistent SHOW / RESET / STOP action bar.

Existing context-sensitive voice help remains provided by voice_control.voice_help.
"""
from __future__ import annotations

from typing import Any

from vadafok_studio.workspace_state import restore_window, save_window, watch_window

_INSTALLED = False
_SYNC_INTERVAL_MS = 180


def _window_exists(window: Any) -> bool:
    try:
        return bool(window is not None and window.winfo_exists())
    except Exception:
        return False


def _entry_text(app: Any) -> str:
    entry = getattr(app, "quick_caption_entry", None)
    if entry is None:
        return ""
    try:
        return entry.get("1.0", "end").strip()
    except Exception:
        return ""


def _set_entry_text(app: Any, text: str) -> None:
    entry = getattr(app, "quick_caption_entry", None)
    if entry is None:
        return
    try:
        entry.delete("1.0", "end")
        if text:
            entry.insert("1.0", text)
        entry.mark_set("insert", "end")
        entry.see("end")
        entry.focus_set()
    except Exception:
        pass


def _sync_draft(app: Any) -> None:
    # Never repopulate a deliberately discarded draft while SHOW, RESET or
    # STOP is being processed. This closes a timing race with the periodic
    # draft monitor.
    if getattr(app, "_quick_caption_discard_in_progress", False):
        return
    if _window_exists(getattr(app, "quick_window", None)):
        app.quick_caption_draft = _entry_text(app)


def _set_voice_status(app: Any, text: str) -> None:
    try:
        app.voice_status_var.set(text)
    except Exception:
        pass


def _clear_draft(app: Any) -> None:
    """Clear the retained Quick Caption draft through one shared path."""
    app.quick_caption_draft = ""


def _close_quick_caption_keep_draft(app: Any) -> None:
    """Close Quick Caption while retaining its current session draft.

    This path is used only for the window X and Escape key. It deliberately
    bypasses the public voice-cancel handler because VADAFOK STOP means a full
    cancellation and must discard the draft.
    """
    _sync_draft(app)
    original_cancel = getattr(app, "_stream_workflow_original_cancel", None)
    if callable(original_cancel):
        try:
            if original_cancel(app):
                _set_voice_status(app, "LISTENING · draft kept · waiting for Live Card")
                return
        except Exception:
            pass

    window = getattr(app, "quick_window", None)
    try:
        app.quick_caption_entry = None
        if _window_exists(window):
            window.destroy()
    except Exception:
        pass
    app.quick_window = None
    _set_voice_status(app, "LISTENING · draft kept · waiting for Live Card")


def _stop_quick_caption(app: Any) -> None:
    """Cancel Quick Caption completely and discard its retained draft."""
    app._quick_caption_discard_in_progress = True
    _clear_draft(app)
    try:
        from vadafok_studio.voice_control.foundation import _cancel_quick_caption

        if _cancel_quick_caption(app):
            _clear_draft(app)
            _set_voice_status(app, "LISTENING · caption cancelled · waiting for Live Card")
            return
    except Exception:
        pass

    window = getattr(app, "quick_window", None)
    try:
        app.quick_caption_entry = None
        if _window_exists(window):
            window.destroy()
    except Exception:
        pass
    app.quick_window = None
    _clear_draft(app)
    app._quick_caption_discard_in_progress = False
    _set_voice_status(app, "LISTENING · caption cancelled · waiting for Live Card")

def _reset_quick_caption(app: Any) -> None:
    """Deliberately clear both the visible field and the retained draft."""
    app._quick_caption_discard_in_progress = True
    try:
        _clear_draft(app)
        _set_entry_text(app, "")
        _clear_draft(app)
    finally:
        app._quick_caption_discard_in_progress = False
    _set_voice_status(app, "DICTATING · text cleared · say VADAFOK SHOW to send")

def _show_quick_caption(app: Any) -> None:
    """Reuse the existing SHOW path and clear the draft only after success."""
    entry = getattr(app, "quick_caption_entry", None)
    if entry is None:
        return
    text = _entry_text(app)
    if not text:
        _set_voice_status(app, "WARNING: Quick Caption is empty · nothing sent")
        return

    # Clear the retained draft before invoking the existing SHOW callback.
    # While the send is in progress, the draft monitor is paused, so it cannot
    # write the visible text back into the draft. If the original SHOW path
    # leaves Quick Caption open, the operation is treated as unsuccessful and
    # the draft is restored below.
    app._quick_caption_discard_in_progress = True
    _clear_draft(app)
    try:
        entry.event_generate("<Return>")
    except Exception:
        app._quick_caption_discard_in_progress = False
        app.quick_caption_draft = text
        _set_voice_status(app, "ERROR: Quick Caption SHOW action failed")
        return

    def finalize_show() -> None:
        # Successful SHOW closes Quick Caption: keep the draft empty.
        # If the window is still open, preserve the text as a safety draft.
        if _window_exists(getattr(app, "quick_window", None)):
            app.quick_caption_draft = _entry_text(app) or text
        else:
            _clear_draft(app)
        app._quick_caption_discard_in_progress = False

    try:
        app.after(500, finalize_show)
    except Exception:
        finalize_show()


def _remove_original_show_button(window: Any) -> None:
    """Replace the single legacy SHOW button with the common action bar."""
    try:
        import customtkinter as ctk

        for widget in list(window.winfo_children()):
            if not isinstance(widget, ctk.CTkButton):
                continue
            try:
                if str(widget.cget("text")).strip().upper() == "SHOW":
                    widget.destroy()
            except Exception:
                continue
    except Exception:
        pass


def _install_quick_caption_ui(app: Any) -> None:
    window = getattr(app, "quick_window", None)
    entry = getattr(app, "quick_caption_entry", None)
    if not _window_exists(window) or entry is None:
        return

    # Do not build duplicate controls when F8 is pressed again while open.
    try:
        existing = getattr(window, "_vadafok_stream_workflow_actions", None)
        if existing is not None and existing.winfo_exists():
            return
    except Exception:
        pass

    try:
        restore_window(window, "quick_caption")
        watch_window(window, "quick_caption")
    except Exception:
        pass

    # Older saved Quick Caption dimensions predate the in-window English
    # preview. Keep the overlay compact, but never let that preview or the
    # action bar be pushed outside the visible area.
    if getattr(app, "quick_caption_translation_label", None) is not None:
        try:
            window.minsize(520, 320)
            window.update_idletasks()
            if window.winfo_height() < 320:
                window.geometry(f"520x340+{window.winfo_x()}+{window.winfo_y()}")
        except Exception:
            pass

    try:
        import customtkinter as ctk
        from vadafok_studio.app import GOLD, GOLD_DARK, TEXT
    except Exception:
        return

    # Restore only unsent text from the current application session.
    draft = str(getattr(app, "quick_caption_draft", "") or "").strip()
    if draft and not _entry_text(app):
        _set_entry_text(app, draft)

    _remove_original_show_button(window)

    status_frame = ctk.CTkFrame(
        window,
        fg_color="#0D0D0D",
        corner_radius=8,
        border_width=1,
        border_color="#3A2A0D",
    )
    status_frame.pack(side="bottom", fill="x", padx=14, pady=(4, 6))
    ctk.CTkLabel(
        status_frame,
        text="VOICE STATUS",
        text_color=GOLD,
        font=ctk.CTkFont(size=10, weight="bold"),
    ).pack(anchor="w", padx=10, pady=(6, 0))
    ctk.CTkLabel(
        status_frame,
        textvariable=app.voice_status_var,
        text_color="#8FE6A0",
        font=ctk.CTkFont(size=10),
        anchor="w",
        justify="left",
        wraplength=470,
    ).pack(fill="x", padx=10, pady=(0, 6))

    actions = ctk.CTkFrame(window, fg_color="transparent")
    actions.pack(side="bottom", fill="x", padx=14, pady=(2, 4))
    actions.grid_columnconfigure((0, 1, 2), weight=1)
    ctk.CTkButton(
        actions,
        text="SHOW",
        fg_color=GOLD,
        text_color="#111111",
        hover_color=GOLD_DARK,
        command=lambda: _show_quick_caption(app),
    ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
    ctk.CTkButton(
        actions,
        text="RESET",
        fg_color="#333333",
        text_color=TEXT,
        hover_color="#444444",
        command=lambda: _reset_quick_caption(app),
    ).grid(row=0, column=1, sticky="ew", padx=4)
    ctk.CTkButton(
        actions,
        text="STOP",
        fg_color="#333333",
        text_color=TEXT,
        hover_color="#444444",
        command=lambda: _stop_quick_caption(app),
    ).grid(row=0, column=2, sticky="ew", padx=(4, 0))

    window._vadafok_stream_workflow_actions = actions
    window._vadafok_stream_workflow_status = status_frame

    # Override only closing behavior. The existing Return/SHOW path remains.
    def close_quick_caption() -> None:
        save_window(window, "quick_caption")
        _close_quick_caption_keep_draft(app)

    window.protocol("WM_DELETE_WINDOW", close_quick_caption)
    window.bind("<Escape>", lambda _event: (close_quick_caption(), "break"))

    def monitor() -> None:
        if not _window_exists(window):
            return
        _sync_draft(app)
        try:
            window.after(_SYNC_INTERVAL_MS, monitor)
        except Exception:
            pass

    monitor()
    try:
        entry.focus_set()
    except Exception:
        pass


def install_stream_workflow() -> None:
    """Install Stream Workflow once on the current VadafokStudio class."""
    global _INSTALLED
    if _INSTALLED:
        return

    from vadafok_studio.app import VadafokStudio

    original_init = VadafokStudio.__init__
    original_open_quick_caption = VadafokStudio.open_quick_caption

    # Keep the original cancel implementation for X/Escape, but make every
    # public voice STOP path discard the draft consistently. The command
    # parser resolves this module-level function at runtime, so replacing it
    # here also covers STOP while the Quick-Card suggestion window is open.
    from vadafok_studio.voice_control import foundation as voice_foundation

    original_cancel_quick_caption = voice_foundation._cancel_quick_caption

    def cancel_quick_caption_and_discard_draft(app: Any) -> bool:
        app._quick_caption_discard_in_progress = True
        _clear_draft(app)
        try:
            result = original_cancel_quick_caption(app)
        finally:
            # The original cancellation destroys the window synchronously.
            # Clear once more after destruction so no pending monitor callback
            # can restore the visible text.
            _clear_draft(app)
            app._quick_caption_discard_in_progress = False
        if result:
            _set_voice_status(app, "LISTENING · caption cancelled · waiting for Live Card")
        return result

    voice_foundation._cancel_quick_caption = cancel_quick_caption_and_discard_draft

    # Route the spoken VADAFOK SHOW command through the exact same central
    # action used by the visible SHOW button. Earlier RC builds let the voice
    # module generate Return directly, which bypassed the Stream Workflow draft
    # cleanup. Keeping one path prevents the two actions from drifting apart.
    def voice_show_through_stream_workflow(app: Any) -> bool:
        if not _window_exists(getattr(app, "quick_window", None)):
            _set_voice_status(app, "WARNING: Quick Caption is not open")
            return False
        if not _entry_text(app):
            _set_voice_status(app, "WARNING: Quick Caption is empty · nothing sent")
            return False
        _show_quick_caption(app)
        return True

    voice_foundation._send_quick_caption_with_existing_action = (
        voice_show_through_stream_workflow
    )

    def stream_init(self: Any, *args: Any, **kwargs: Any) -> None:
        original_init(self, *args, **kwargs)
        self.quick_caption_draft = ""
        self._quick_caption_discard_in_progress = False
        self._stream_workflow_original_cancel = original_cancel_quick_caption

        try:
            restore_window(self, "main_window")
            watch_window(self, "main_window")
        except Exception:
            pass

        # Save before the application's normal destroy/close sequence. Binding
        # with add='+' does not replace any existing close implementation.
        try:
            self.bind("<Destroy>", lambda event: save_window(self, "main_window") if event.widget is self else None, add="+")
        except Exception:
            pass

        # OBS Workflow is the practical first step before every stream. Delay
        # until the original startup page and all runtime extensions exist.
        try:
            self.after(120, self.show_obs_workflow_page)
        except Exception:
            pass

    def stream_open_quick_caption(
        self: Any, *args: Any, **kwargs: Any
    ) -> Any:
        result = original_open_quick_caption(self, *args, **kwargs)
        try:
            self.after(0, lambda: _install_quick_caption_ui(self))
        except Exception:
            pass
        return result

    VadafokStudio.__init__ = stream_init
    VadafokStudio.open_quick_caption = stream_open_quick_caption
    _INSTALLED = True
