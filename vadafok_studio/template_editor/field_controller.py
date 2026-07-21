"""Create, copy, and delete Template Editor fields."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from tkinter import messagebox

from ..core.template_store import save_template


def add_field(app: Any) -> None:
    template = app.template_current()
    app.template_push_history("add field")
    fields = template.setdefault("fields", [])
    name = f"field_{len(fields) + 1}"
    fields.append({
        "name": name, "x": 160, "y": 120 + len(fields) * 70,
        "width": 500, "height": 90, "font_family": "Bebas Neue",
        "font_size": 90, "text_color": "#FFFFFF",
        "stroke_color": "#000000", "stroke_width": 3, "uppercase": True,
    })
    app.template_selected_field = len(fields) - 1
    app.template_selected_fields = {app.template_selected_field}
    _save_and_refresh(app, template, properties=True)


def copy_fields(app: Any) -> None:
    template = app.template_current()
    fields = template.get("fields", [])
    selected = _selected_indices(app, len(fields))
    if not selected:
        messagebox.showwarning("Template Editor", "Bitte zuerst ein Feld auswählen.")
        return

    # Invalid actions must not create empty UNDO entries.
    app.template_push_history("copy field")
    existing_names = {field.get("name", "") for field in fields}
    design_width, design_height = getattr(
        app, "template_canvas_design_size", (1280, 720),
    )
    copied_indices: list[int] = []
    source_to_copy_id: dict[Any, Any] = {}
    for source_index in selected:
        source = fields[source_index]
        copied = deepcopy(source)
        copied["id"] = app.template_new_id()
        copied["name"] = _unique_copy_name(
            source.get("name", "field"), existing_names,
        )
        copied["x"] = _offset_inside_canvas(
            copied.get("x", 0), copied.get("width", 100), design_width,
        )
        copied["y"] = _offset_inside_canvas(
            copied.get("y", 0), copied.get("height", 50), design_height,
        )
        fields.append(copied)
        copied_indices.append(len(fields) - 1)
        source_to_copy_id[source.get("id")] = copied.get("id")
    _copy_complete_groups(app, template, source_to_copy_id)
    app.template_selected_fields = set(copied_indices)
    app.template_selected_field = copied_indices[-1]
    _save_and_refresh(app, template, properties=True)
    if len(copied_indices) == 1:
        _focus_name_entry(app)


def delete_fields(app: Any) -> None:
    template = app.template_current()
    fields = template.get("fields", [])
    selected = set(_selected_indices(app, len(fields)))
    locked = {index for index in selected if app.template_is_field_locked(index)}
    selected -= locked
    if locked and not selected:
        messagebox.showwarning(
            "Template Editor", "Auswahl enthält nur gesperrte Felder.",
        )
        return
    if locked:
        messagebox.showinfo(
            "Template Editor",
            f"{len(locked)} gesperrte Felder wurden nicht gelöscht.",
        )
    if not selected:
        messagebox.showwarning("Template Editor", "Bitte zuerst ein Feld auswählen.")
        return
    if len(selected) > 1 and not messagebox.askyesno(
        "Template Editor", f"{len(selected)} Felder wirklich löschen?",
    ):
        return

    app.template_push_history("delete field")
    template["fields"] = [
        field for index, field in enumerate(fields) if index not in selected
    ]
    app.template_clean_groups()
    app.template_clear_selection()
    _save_and_refresh(app, template, properties=False)


def _selected_indices(app: Any, field_count: int) -> list[int]:
    selected = set(getattr(app, "template_selected_fields", set()))
    if app.template_selected_field is not None:
        selected.add(app.template_selected_field)
    return sorted(index for index in selected if 0 <= index < field_count)


def _unique_copy_name(base_name: str, existing: set[str]) -> str:
    candidate = f"{base_name}_copy"
    suffix = 2
    while candidate in existing:
        candidate = f"{base_name}_copy{suffix}"
        suffix += 1
    existing.add(candidate)
    return candidate


def _offset_inside_canvas(position: Any, size: Any, canvas_size: Any) -> int:
    maximum = max(0, int(canvas_size) - int(size))
    return min(max(0, int(position) + 15), maximum)


def _copy_complete_groups(
    app: Any, template: dict, source_to_copy_id: dict[Any, Any],
) -> None:
    source_ids = {field_id for field_id in source_to_copy_id if field_id}
    groups = template.setdefault("groups", [])
    for group in list(groups):
        group_ids = set(group.get("field_ids", []))
        if not group_ids or not group_ids.issubset(source_ids):
            continue
        existing_names = {candidate.get("name", "") for candidate in groups}
        name = _unique_copy_name(group.get("name", "Group"), existing_names)
        groups.append({
            "id": app.template_new_id(), "name": name,
            "field_ids": [
                source_to_copy_id[field_id]
                for field_id in group.get("field_ids", [])
                if field_id in source_to_copy_id
            ],
            "locked": bool(group.get("locked", False)),
            "hidden": bool(group.get("hidden", False)),
        })


def _save_and_refresh(
    app: Any, template: dict, *, properties: bool,
) -> None:
    save_template(app.template_selected_name, template)
    if properties:
        app.template_load_selected_properties()
    app.template_draw_canvas()
    if hasattr(app, "template_props_body"):
        app.template_build_properties_panel()


def _focus_name_entry(app: Any) -> None:
    try:
        entry = app.template_prop_name_entry
        entry.focus_set()
        entry.select_range(0, "end")
    except Exception:
        pass
