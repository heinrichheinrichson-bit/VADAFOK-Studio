"""Alignment and spacing actions for selected Template Editor fields."""

from __future__ import annotations

from typing import Any
from tkinter import messagebox

from ..core.template_store import save_template

ALIGN_MODES = {"left", "center", "right", "top", "middle", "bottom"}
AXES = {"horizontal", "vertical"}


def align_selected(app: Any, mode: str) -> None:
    if mode not in ALIGN_MODES:
        return
    template, fields, selected = _selection(app)
    if len(selected) < 2:
        messagebox.showwarning(
            "Template Editor", "Bitte mindestens zwei Felder auswählen.",
        )
        return
    app.template_push_history("align")
    chosen = [fields[index] for index in selected]
    left = min(_number(field, "x") for field in chosen)
    right = max(_number(field, "x") + _number(field, "width") for field in chosen)
    top = min(_number(field, "y") for field in chosen)
    bottom = max(_number(field, "y") + _number(field, "height") for field in chosen)
    center_x, center_y = (left + right) // 2, (top + bottom) // 2
    for field in chosen:
        width, height = _number(field, "width"), _number(field, "height")
        if mode == "left": field["x"] = left
        elif mode == "center": field["x"] = center_x - width // 2
        elif mode == "right": field["x"] = right - width
        elif mode == "top": field["y"] = top
        elif mode == "middle": field["y"] = center_y - height // 2
        elif mode == "bottom": field["y"] = bottom - height
    _save_and_draw(app, template)


def distribute_selected(app: Any, axis: str) -> None:
    if axis not in AXES:
        return
    template, fields, selected = _selection(app)
    if len(selected) < 3:
        messagebox.showwarning(
            "Template Editor", "Zum Verteilen bitte mindestens drei Felder auswählen.",
        )
        return
    app.template_push_history("distribute")
    chosen = [fields[index] for index in selected]
    coordinate = "x" if axis == "horizontal" else "y"
    chosen.sort(key=lambda field: _number(field, coordinate))
    start, end = _number(chosen[0], coordinate), _number(chosen[-1], coordinate)
    step = (end - start) / (len(chosen) - 1)
    for index, field in enumerate(chosen):
        field[coordinate] = int(round(start + step * index))
    _save_and_draw(app, template)


def equal_spacing_selected(app: Any, axis: str) -> None:
    if axis not in AXES:
        return
    template, fields, selected = _selection(app)
    selected = [index for index in selected if not fields[index].get("hidden", False)]
    if len(selected) < 3:
        messagebox.showwarning(
            "Template Editor",
            "Equal Spacing braucht mindestens drei ungesperrte, sichtbare Felder.",
        )
        return
    app.template_push_history("equal spacing")
    chosen = [fields[index] for index in selected]
    coordinate = "x" if axis == "horizontal" else "y"
    dimension = "width" if axis == "horizontal" else "height"
    chosen.sort(key=lambda field: _number(field, coordinate))
    start = min(_number(field, coordinate) for field in chosen)
    end = max(
        _number(field, coordinate) + _number(field, dimension) for field in chosen
    )
    total_size = sum(_number(field, dimension) for field in chosen)
    gap = (end - start - total_size) / (len(chosen) - 1)
    cursor = float(start)
    for field in chosen:
        field[coordinate] = int(round(cursor))
        cursor += _number(field, dimension) + gap
    _save_and_draw(app, template)


def _selection(app: Any) -> tuple[dict, list[dict], list[int]]:
    template = app.template_current()
    fields = template.get("fields", [])
    getter = getattr(app, "template_selected_unlocked_indices", None)
    selected = getter() if callable(getter) else app.template_selected_indices()
    selected = [index for index in selected if 0 <= index < len(fields)]
    return template, fields, selected


def _number(field: dict, key: str) -> int:
    return int(field.get(key, 0))


def _save_and_draw(app: Any, template: dict) -> None:
    save_template(app.template_selected_name, template)
    app.template_draw_canvas()
