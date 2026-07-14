"""Language selector for the Windows command recognizer.

Whisper remains multilingual and auto-detects German and English dictation.
The selected culture only controls Windows System.Speech, which recognizes
fixed commands such as Live Card and Vadafok Show/Reset/Stop.
"""

from __future__ import annotations

from typing import Any, Iterator

import customtkinter as ctk

_INSTALLED = False

LANGUAGE_TO_CULTURE = {
    "Deutsch (de-DE)": "de-DE",
    "English (en-US)": "en-US",
}
CULTURE_TO_LANGUAGE = {value: key for key, value in LANGUAGE_TO_CULTURE.items()}
DEFAULT_LANGUAGE = "Deutsch (de-DE)"


def _walk_widgets(widget: Any) -> Iterator[Any]:
    """Yield every descendant widget below *widget*."""
    try:
        children = widget.winfo_children()
    except Exception:
        return
    for child in children:
        yield child
        yield from _walk_widgets(child)


def _is_culture_entry(app: Any, widget: Any) -> bool:
    """Return True when *widget* is the entry bound to ``voice_culture``."""
    if widget.__class__.__name__ != "CTkEntry":
        return False
    try:
        widget_variable = str(widget.cget("textvariable"))
        culture_variable = str(app.voice_culture)
        return bool(widget_variable and widget_variable == culture_variable)
    except Exception:
        return False


def _replace_culture_entry(app: Any) -> None:
    """Replace the editable culture entry with a two-value option menu."""
    main = getattr(app, "main", None)
    if main is None:
        return

    old_entry = next(
        (widget for widget in _walk_widgets(main) if _is_culture_entry(app, widget)),
        None,
    )
    if old_entry is None:
        return

    try:
        manager = old_entry.winfo_manager()
        parent = old_entry.master
        grid_info = old_entry.grid_info() if manager == "grid" else None
        pack_info = old_entry.pack_info() if manager == "pack" else None
        place_info = old_entry.place_info() if manager == "place" else None
    except Exception:
        return

    culture = str(app.voice_culture.get() or "de-DE")
    if culture not in CULTURE_TO_LANGUAGE:
        culture = "de-DE"
        app.voice_culture.set(culture)

    display_var = ctk.StringVar(value=CULTURE_TO_LANGUAGE[culture])

    def on_language_selected(label: str) -> None:
        selected_culture = LANGUAGE_TO_CULTURE.get(label, "de-DE")
        app.voice_culture.set(selected_culture)
        try:
            app.voice_status_var.set(
                f"LANGUAGE SELECTED · {selected_culture} · save and restart listener"
            )
        except Exception:
            pass

    try:
        old_entry.destroy()
        selector = ctk.CTkOptionMenu(
            parent,
            values=list(LANGUAGE_TO_CULTURE),
            variable=display_var,
            command=on_language_selected,
            dynamic_resizing=False,
        )
        if manager == "grid" and grid_info is not None:
            grid_info.pop("in", None)
            selector.grid(**grid_info)
        elif manager == "pack" and pack_info is not None:
            pack_info.pop("in", None)
            selector.pack(**pack_info)
        elif manager == "place" and place_info is not None:
            place_info.pop("in", None)
            selector.place(**place_info)
        else:
            selector.pack(fill="x")
        app.voice_language_selector = selector
        app.voice_language_display_var = display_var
    except Exception:
        # The Settings page must remain usable even if a future UI refactor
        # changes the culture row. In that case the original page is kept.
        return


def install_language_selection() -> None:
    """Patch the Settings page with a safe de-DE/en-US dropdown."""
    global _INSTALLED
    if _INSTALLED:
        return

    from vadafok_studio.app import VadafokStudio

    original_show_settings_page = VadafokStudio.show_settings_page

    def show_settings_page_with_language_selector(
        self: Any, *args: Any, **kwargs: Any
    ) -> Any:
        result = original_show_settings_page(self, *args, **kwargs)
        # Build the original page first, then replace only the culture entry.
        self.after_idle(lambda: _replace_culture_entry(self))
        return result

    VadafokStudio.show_settings_page = show_settings_page_with_language_selector
    _INSTALLED = True
