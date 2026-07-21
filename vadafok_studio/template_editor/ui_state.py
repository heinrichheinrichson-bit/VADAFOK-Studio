"""Selection-aware state for Template Editor toolbar controls."""

from __future__ import annotations

from typing import Any


def refresh_toolbar_state(app: Any) -> None:
    buttons = getattr(app, "template_action_buttons", None)
    if not buttons:
        return
    template = app.template_current()
    fields = template.get("fields", [])
    selected = _selected_indices(app, fields)
    unlocked = [index for index in selected if not app.template_is_field_locked(index)]
    grouped = _selection_touches_group(app, selected)

    states = {
        "copy": bool(selected),
        "delete": bool(unlocked),
        "align": len(unlocked) >= 2,
        "distribute": len(unlocked) >= 3,
        "equal_spacing": len(unlocked) >= 3,
        "group": len(selected) >= 2,
        "ungroup": grouped,
        "undo": bool(getattr(app, "template_undo_stack", [])),
        "redo": bool(getattr(app, "template_redo_stack", [])),
    }
    for action, enabled in states.items():
        for button in _as_list(buttons.get(action)):
            try:
                button.configure(state="normal" if enabled else "disabled")
            except Exception:
                pass

    undo_count = len(getattr(app, "template_undo_stack", []))
    redo_count = len(getattr(app, "template_redo_stack", []))
    undo_reasons = getattr(app, "template_undo_reasons", [])
    redo_reasons = getattr(app, "template_redo_reasons", [])
    undo_text = f"UNDO · {undo_reasons[-1]}" if undo_count and undo_reasons else "UNDO"
    redo_text = f"REDO · {redo_reasons[-1]}" if redo_count and redo_reasons else "REDO"
    _set_text(buttons.get("undo"), undo_text)
    _set_text(buttons.get("redo"), redo_text)
    _update_summary(app, selected, unlocked)


def _selected_indices(app: Any, fields: list[dict]) -> list[int]:
    selected = set(getattr(app, "template_selected_fields", set()))
    if app.template_selected_field is not None:
        selected.add(app.template_selected_field)
    return sorted(
        index for index in selected
        if 0 <= index < len(fields) and not fields[index].get("hidden", False)
    )


def _selection_touches_group(app: Any, selected: list[int]) -> bool:
    selected_ids = {app.template_field_id(index) for index in selected}
    selected_ids.discard(None)
    return any(
        selected_ids.intersection(group.get("field_ids", []))
        for group in app.template_groups()
    )


def _update_summary(app: Any, selected: list[int], unlocked: list[int]) -> None:
    label = getattr(app, "template_selection_summary_label", None)
    if label is None:
        return
    locked_count = len(selected) - len(unlocked)
    if not selected:
        text, color = "Keine Felder ausgewählt", "#8F8058"
    else:
        text = f"Auswahl: {len(selected)}"
        if locked_count:
            text += f" · 🔒 {locked_count}"
        color = "#D9C58C"
    try:
        label.configure(text=text, text_color=color)
    except Exception:
        pass


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _set_text(value: Any, text: str) -> None:
    for button in _as_list(value):
        try:
            button.configure(text=text)
        except Exception:
            pass
