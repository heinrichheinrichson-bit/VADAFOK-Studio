"""Reusable context-sensitive voice command hints for VADAFOK windows."""

from __future__ import annotations

from typing import Any, Iterable


def _command_text(commands: Iterable[str]) -> str:
    return "  •  ".join(str(item).strip() for item in commands if str(item).strip())


def add_voice_help(
    parent: Any,
    commands: Iterable[str],
    *,
    state_text: str = "Listening",
    attribute_name: str = "_vadafok_voice_help",
) -> Any | None:
    """Add one unobtrusive help bar to a CTk window or frame.

    The function is deliberately defensive because voice help must never stop
    the actual caption workflow if the UI changes in a later VADAFOK release.
    """

    try:
        existing = getattr(parent, attribute_name, None)
        if existing is not None and existing.winfo_exists():
            return existing
    except Exception:
        pass

    try:
        import customtkinter as ctk

        frame = ctk.CTkFrame(
            parent,
            fg_color="#0D0D0D",
            corner_radius=8,
            border_width=1,
            border_color="#3A2A0D",
        )
        frame.pack(side="bottom", fill="x", padx=14, pady=(6, 12))

        ctk.CTkLabel(
            frame,
            text=f"VOICE · {state_text}",
            text_color="#D6A43A",
            font=ctk.CTkFont(size=11, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(7, 1))

        ctk.CTkLabel(
            frame,
            text=_command_text(commands),
            text_color="#BCA870",
            font=ctk.CTkFont(size=11),
            anchor="w",
            justify="left",
            wraplength=620,
        ).pack(fill="x", padx=12, pady=(0, 7))

        setattr(parent, attribute_name, frame)
        return frame
    except Exception:
        return None


def install_quick_caption_voice_help(app: Any) -> None:
    """Show commands that are valid in the normal F8 Quick Caption window."""

    window = getattr(app, "quick_window", None)
    try:
        if window is None or not window.winfo_exists():
            return
    except Exception:
        return

    add_voice_help(
        window,
        ("Vadafok Show", "Vadafok Reset", "Vadafok Stop"),
        state_text="Quick Caption",
        attribute_name="_vadafok_quick_caption_voice_help",
    )
