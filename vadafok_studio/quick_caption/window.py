"""Compact F8 Quick Caption window.

This module owns only the small F8 window. The large Live Card page remains
separate. Voice-control and stream-workflow extensions continue to wrap the
public ``VadafokStudio.open_quick_caption`` method.
"""
from __future__ import annotations

from typing import Any

import customtkinter as ctk
from ..core.window_icon import apply_window_icon


GOLD = "#D9A928"
GOLD_DARK = "#9B7418"


def open_quick_caption_window(app: Any) -> None:
    """Open or focus the compact F8 Quick Caption window."""

    def focus_quick_caption() -> None:
        try:
            if app.quick_window and app.quick_window.winfo_exists():
                app.quick_window.lift()
                app.quick_window.focus_force()
        except Exception:
            pass
        try:
            entry = getattr(app, "quick_caption_entry", None)
            if entry is not None:
                entry.focus_force()
                entry.focus_set()
                entry.mark_set("insert", "end")
                entry.see("end")
        except Exception:
            pass

    if app.quick_window and app.quick_window.winfo_exists():
        focus_quick_caption()
        try:
            app.quick_window.after(50, focus_quick_caption)
            app.quick_window.after(150, focus_quick_caption)
        except Exception:
            pass
        return

    app.quick_window = ctk.CTkToplevel(app)
    apply_window_icon(app.quick_window, app)
    app.quick_window.title("Quick Caption")
    app.quick_window.geometry("520x340")
    app.quick_window.minsize(520, 320)
    app.quick_window.attributes("-topmost", True)

    ctk.CTkLabel(
        app.quick_window,
        text="Quick Caption",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=GOLD,
    ).pack(anchor="w", padx=16, pady=(14, 4))

    entry = ctk.CTkTextbox(
        app.quick_window,
        height=70,
        font=ctk.CTkFont(size=18),
        fg_color="#050505",
        border_color=GOLD_DARK,
        border_width=1,
    )
    entry.pack(fill="both", expand=True, padx=16, pady=8)
    app.quick_caption_entry = entry

    translation_frame = ctk.CTkFrame(
        app.quick_window,
        fg_color="#0B0B0B",
        corner_radius=8,
        border_color="#3A2A0D",
        border_width=1,
    )
    translation_frame.pack(fill="x", padx=16, pady=(0, 8))
    ctk.CTkLabel(
        translation_frame,
        text="ENGLISH",
        font=ctk.CTkFont(size=11, weight="bold"),
        text_color=GOLD,
    ).pack(anchor="w", padx=10, pady=(7, 1))
    app.quick_caption_translation_label = ctk.CTkLabel(
        translation_frame,
        text="Speak to prepare English…",
        font=ctk.CTkFont(size=14),
        text_color="#D9C58C",
        justify="left",
        anchor="w",
        wraplength=470,
    )
    app.quick_caption_translation_label.pack(fill="x", padx=10, pady=(0, 8))

    try:
        app.quick_window.after_idle(focus_quick_caption)
        app.quick_window.after(1, focus_quick_caption)
        app.quick_window.after(50, focus_quick_caption)
        app.quick_window.after(150, focus_quick_caption)
        app.quick_window.after(300, focus_quick_caption)
        app.after(350, focus_quick_caption)
    except Exception:
        pass

    def send(_event: Any = None) -> str:
        text = entry.get("1.0", "end").strip()
        if text:
            try:
                app.quick_window.destroy()
            except Exception:
                pass
            app.quick_window = None
            app.quick_caption_entry = None
            app.quick_caption_translation_label = None
            app.voice_live_card_mode = False

            app.show_live_card()
            app.set_message(text)
            app.show_card()
        return "break"

    def close_window() -> None:
        try:
            app.quick_caption_entry = None
            app.quick_caption_translation_label = None
            app.voice_live_card_mode = False
            app.quick_window.destroy()
        except Exception:
            pass
        app.quick_window = None

    entry.bind("<Return>", send)
    entry.bind("<Escape>", lambda _event=None: (close_window(), "break"))
    app.quick_window.protocol("WM_DELETE_WINDOW", close_window)

    ctk.CTkButton(
        app.quick_window,
        text="SHOW",
        fg_color=GOLD,
        text_color="#111111",
        hover_color=GOLD_DARK,
        command=send,
    ).pack(fill="x", padx=16, pady=(0, 14))
