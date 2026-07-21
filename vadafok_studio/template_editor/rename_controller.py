"""Inline field and group renaming."""

from __future__ import annotations

from typing import Any

from ..core.template_store import save_template


def commit_inline_rename(app: Any, event=None):
    entry = app.template_rename_entry
    if entry is None:
        return "break"
    value = entry.get().strip()
    kind, target = app.template_renaming_kind, app.template_renaming_target
    try:
        entry.destroy()
    except Exception:
        pass
    app.template_rename_entry = None
    app.template_renaming_kind = None
    app.template_renaming_target = None
    if not value:
        app.template_build_layers_panel()
        return "break"

    template = app.template_current()
    changed = False
    if kind == "group":
        group = app.template_find_group(target)
        if group and group.get("name") != value:
            app.template_push_history("rename group")
            group["name"] = value
            changed = True
    elif kind == "field":
        fields = template.get("fields", [])
        if target is not None and 0 <= target < len(fields):
            if fields[target].get("name") != value:
                app.template_push_history("rename field")
                fields[target]["name"] = value
                changed = True
                if target == app.template_selected_field:
                    app.template_load_selected_properties()
                    if hasattr(app, "template_props_body"):
                        app.template_build_properties_panel()
    if changed:
        save_template(app.template_selected_name, template)
        app.template_draw_canvas()
    else:
        app.template_build_layers_panel()
    return "break"
