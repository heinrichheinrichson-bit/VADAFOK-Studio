"""Apply the VADAFOK application icon to Tk and CustomTkinter windows."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from typing import Any

ICON_DIR = Path(__file__).resolve().parents[1] / "assets" / "icons"
ICO_PATH = ICON_DIR / "vadafok_icon.ico"
PNG_PATH = ICON_DIR / "vadafok_icon.png"


def apply_window_icon(window: Any, owner: Any = None) -> None:
    """Apply the branded icon now and after native window creation."""
    def apply() -> None:
        try:
            if ICO_PATH.exists():
                window.iconbitmap(str(ICO_PATH))
        except Exception:
            pass
        photo = _owner_icon(owner)
        if photo is None and PNG_PATH.exists():
            try:
                photo = tk.PhotoImage(master=window, file=str(PNG_PATH))
            except Exception:
                photo = None
        if photo is not None:
            try:
                window.iconphoto(False, photo)
                window._vadafok_icon_photo = photo
            except Exception:
                pass

    apply()
    for delay in (0, 100):
        try:
            window.after(delay, apply)
        except Exception:
            pass


def _owner_icon(owner: Any) -> Any:
    current = owner
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        photo = getattr(current, "_vadafok_icon_photo", None)
        if photo is not None:
            return photo
        current = getattr(current, "master", None)
    return None
