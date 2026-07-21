"""Undo/redo history for Template Editor documents."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from ..core.template_store import save_template


def snapshot(app: Any) -> dict:
    return deepcopy(app.template_current())


def push_history(app: Any, reason: str = "edit") -> bool:
    return push_snapshot(app, snapshot(app), reason)


def push_snapshot(app: Any, value: dict, reason: str = "edit") -> bool:
    _ensure_stacks(app)
    value = deepcopy(value)
    if app.template_undo_stack and app.template_undo_stack[-1] == value:
        return False
    app.template_undo_stack.append(value)
    app.template_undo_reasons.append(str(reason or "edit"))
    limit = int(getattr(app, "template_history_limit", 80))
    if len(app.template_undo_stack) > limit:
        app.template_undo_stack = app.template_undo_stack[-limit:]
        app.template_undo_reasons = app.template_undo_reasons[-limit:]
    app.template_redo_stack.clear()
    app.template_redo_reasons.clear()
    _refresh_toolbar(app)
    return True


def restore_snapshot(app: Any, value: dict) -> None:
    app.template_working_data = deepcopy(value)
    save_template(app.template_selected_name, app.template_working_data)
    count = len(app.template_working_data.get("fields", []))
    app.template_selected_fields = {
        index for index in getattr(app, "template_selected_fields", set())
        if 0 <= index < count
    }
    if app.template_selected_field is not None and not (
        0 <= app.template_selected_field < count
    ):
        app.template_selected_field = next(
            iter(app.template_selected_fields), None,
        )
    app.template_draw_canvas()
    app.template_load_selected_properties()
    if hasattr(app, "template_props_body"):
        app.template_build_properties_panel()
    _refresh_toolbar(app)


def undo(app: Any):
    _ensure_stacks(app)
    if not app.template_undo_stack:
        return "break"
    current = snapshot(app)
    previous = app.template_undo_stack.pop()
    reason = app.template_undo_reasons.pop() if app.template_undo_reasons else "edit"
    app.template_redo_stack.append(current)
    app.template_redo_reasons.append(reason)
    restore_snapshot(app, previous)
    return "break"


def redo(app: Any):
    _ensure_stacks(app)
    if not app.template_redo_stack:
        return "break"
    current = snapshot(app)
    next_value = app.template_redo_stack.pop()
    reason = app.template_redo_reasons.pop() if app.template_redo_reasons else "edit"
    app.template_undo_stack.append(current)
    app.template_undo_reasons.append(reason)
    restore_snapshot(app, next_value)
    return "break"


def _ensure_stacks(app: Any) -> None:
    for name in (
        "template_undo_stack", "template_redo_stack",
        "template_undo_reasons", "template_redo_reasons",
    ):
        if not hasattr(app, name):
            setattr(app, name, [])


def _refresh_toolbar(app: Any) -> None:
    refresh = getattr(app, "template_refresh_toolbar_state", None)
    if callable(refresh):
        refresh()
