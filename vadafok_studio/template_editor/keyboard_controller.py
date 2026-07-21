"""Keyboard shortcut routing for the Template Editor."""

from __future__ import annotations

from typing import Any

BLOCKED_WIDGET_CLASSES = {
    "Entry", "Text", "Spinbox", "TEntry", "TCombobox",
    "CTkEntry", "CTkTextbox", "CTkComboBox",
}


def shortcuts_allowed(app: Any, event=None) -> bool:
    if getattr(app, "active_page", None) != "Template Editor":
        return False
    widget = getattr(event, "widget", None) if event is not None else None
    try:
        widget_class = widget.winfo_class() if widget is not None else ""
    except Exception:
        widget_class = ""
    if widget_class in BLOCKED_WIDGET_CLASSES:
        return False
    widget_text = str(widget).casefold() if widget is not None else ""
    return not any(
        token in widget_text for token in ("entry", "textbox", "text", "combobox")
    )


def handle_key(app: Any, event):
    if not shortcuts_allowed(app, event):
        return None
    key = str(getattr(event, "keysym", "") or "")
    state = int(getattr(event, "state", 0) or 0)
    ctrl = bool(state & 0x0004) or bool(getattr(app, "template_ctrl_down", False))
    shift = bool(state & 0x0001) or bool(getattr(app, "template_shift_down", False))
    if ctrl and key.casefold() == "z": return app.template_undo()
    if ctrl and key.casefold() == "y": return app.template_redo()
    if ctrl and key.casefold() == "a": return app.template_keyboard_select_all()
    if ctrl and key.casefold() == "d": return app.template_keyboard_duplicate_selected()
    if key in {"Delete", "BackSpace"}: return app.template_keyboard_delete_selected()
    if key == "Escape": return app.template_keyboard_clear_selection()
    step = 10 if shift else 1
    moves = {
        "Left": (-step, 0), "Right": (step, 0),
        "Up": (0, -step), "Down": (0, step),
    }
    if key in moves:
        return app.template_keyboard_move_selected(*moves[key])
    return None
