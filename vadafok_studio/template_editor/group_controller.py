"""Group creation and removal for Template Editor fields."""

from __future__ import annotations

from typing import Any
from tkinter import messagebox

from ..core.template_store import save_template


def create_group(app: Any) -> None:
    app.template_ensure_field_ids()
    selected = app.template_selected_indices()
    if len(selected) < 2:
        messagebox.showwarning(
            "Template Editor", "Bitte mindestens zwei Felder auswählen.",
        )
        return
    selected_ids = [app.template_field_id(index) for index in selected]
    selected_ids = [field_id for field_id in selected_ids if field_id]
    if len(selected_ids) < 2:
        messagebox.showwarning(
            "Template Editor",
            "Für eine Gruppe sind mindestens zwei gültige Felder nötig.",
        )
        return

    template = app.template_current()
    groups = template.setdefault("groups", [])
    app.template_push_history("group fields")
    selected_id_set = set(selected_ids)
    for group in groups:
        group["field_ids"] = [
            field_id for field_id in group.get("field_ids", [])
            if field_id not in selected_id_set
        ]
        group.pop("fields", None)
    groups[:] = [group for group in groups if group.get("field_ids")]
    groups.append({
        "id": app.template_new_id(),
        "name": _unique_group_name(groups),
        "field_ids": selected_ids,
        "locked": False,
        "hidden": False,
    })
    _save_and_refresh(app, template)


def ungroup_selected(app: Any) -> None:
    app.template_clean_groups()
    selected_ids = {
        app.template_field_id(index) for index in app.template_selected_indices()
    }
    selected_ids.discard(None)
    group_ids = {
        group.get("id") for group in app.template_groups()
        if selected_ids.intersection(group.get("field_ids", []))
    }
    group_ids.discard(None)
    if not group_ids:
        messagebox.showwarning("Template Editor", "Keine Gruppe ausgewählt.")
        return
    app.template_push_history("ungroup fields")
    template = app.template_current()
    template["groups"] = [
        group for group in template.get("groups", [])
        if group.get("id") not in group_ids
    ]
    _save_and_refresh(app, template)


def _unique_group_name(groups: list[dict]) -> str:
    existing = {group.get("name", "") for group in groups}
    name = "Group"
    suffix = 2
    while name in existing:
        name = f"Group {suffix}"
        suffix += 1
    return name


def _save_and_refresh(app: Any, template: dict) -> None:
    save_template(app.template_selected_name, template)
    app.template_update_fields_overlay()
    app.template_build_layers_panel()
