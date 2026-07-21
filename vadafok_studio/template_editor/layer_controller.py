"""Layer ordering and interaction for the Template Editor."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from ..core.template_store import save_template

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"

def layer_drag_start(app: Any, event, idx):
    app.template_layer_drag_index = idx
    app.template_layer_drag_start_y = getattr(event, "y_root", 0)
    app.template_layer_drop_target = None

    try:
        event.widget.configure(fg_color=GOLD, text_color="#111111")
    except Exception:
        pass

    return "break"


def layer_clear_drop_indicator(app: Any):
    if hasattr(app, "template_layer_drop_indicator") and app.template_layer_drop_indicator is not None:
        try:
            app.template_layer_drop_indicator.destroy()
        except Exception:
            pass
    app.template_layer_drop_indicator = None


def layer_drag_motion(app: Any, event):
    try:
        app.template_layers_body.configure(cursor="hand2")
    except Exception:
        pass

    target_idx = app.template_layer_target_from_y(getattr(event, "y_root", 0))
    app.template_layer_drop_target = target_idx
    app.template_layer_show_drop_indicator(target_idx)

    return "break"


def layer_show_drop_indicator(app: Any, target_idx):
    app.template_layer_clear_drop_indicator()

    if target_idx is None:
        return

    try:
        row = app._template_layer_row_for_field.get(target_idx)
        if row is None:
            return

        # Add a thin gold bar above the target row.
        indicator = ctk.CTkFrame(
            app.template_layers_body,
            height=4,
            fg_color=GOLD,
            corner_radius=2
        )
        indicator.grid(row=row, column=0, columnspan=5, padx=8, pady=(0, 0), sticky="ew")
        try:
            indicator.lift()
        except Exception:
            pass

        app.template_layer_drop_indicator = indicator
    except Exception:
        app.template_layer_drop_indicator = None


def layer_drag_end(app: Any, event):
    try:
        app.template_layers_body.configure(cursor="")
    except Exception:
        pass

    app.template_layer_clear_drop_indicator()

    source_idx = getattr(app, "template_layer_drag_index", None)
    app.template_layer_drag_index = None

    if source_idx is None:
        app.template_build_layers_panel()
        return "break"

    target_idx = getattr(app, "template_layer_drop_target", None)
    if target_idx is None:
        target_idx = app.template_layer_target_from_y(getattr(event, "y_root", 0))

    app.template_layer_drop_target = None

    if target_idx is None or target_idx == source_idx:
        app.template_build_layers_panel()
        return "break"

    app.template_move_layer_to_index(source_idx, target_idx)
    return "break"


def layer_target_from_y(app: Any, y_root):
    if not hasattr(app, "_template_layer_row_for_field"):
        return None

    best_idx = None
    best_dist = None

    for idx, row in app._template_layer_row_for_field.items():
        try:
            widgets = app.template_layers_body.grid_slaves(row=row, column=0)
            if not widgets:
                continue
            widget = widgets[0]
            center = widget.winfo_rooty() + widget.winfo_height() / 2
            dist = abs(center - y_root)
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_idx = idx
        except Exception:
            continue

    return best_idx


def move_layer_to_index(app: Any, source_idx, target_idx):
    template = app.template_current()
    fields = template.get("fields", [])

    if not (0 <= source_idx < len(fields)) or not (0 <= target_idx < len(fields)):
        return

    if source_idx == target_idx:
        return

    if hasattr(app, "template_push_history"):
        app.template_push_history("drag layer reorder")

    item = fields.pop(source_idx)
    fields.insert(target_idx, item)

    # Update selected indices after list move.
    def remap(old_idx):
        if old_idx == source_idx:
            return target_idx
        if source_idx < target_idx:
            if source_idx < old_idx <= target_idx:
                return old_idx - 1
        else:
            if target_idx <= old_idx < source_idx:
                return old_idx + 1
        return old_idx

    selected = set(getattr(app, "template_selected_fields", set()))
    app.template_selected_fields = {remap(i) for i in selected if 0 <= i < len(fields)}
    if app.template_selected_field is not None:
        app.template_selected_field = remap(app.template_selected_field)

    # Groups use stable field ids, so no group remap is needed.
    save_template(app.template_selected_name, template)
    app.template_draw_canvas()
    app.template_build_layers_panel()
    if hasattr(app, "template_props_body"):
        app.template_build_properties_panel()


def refresh_layers_selection(app: Any):
    """Update only Layers selection styling without rebuilding every row widget."""
    field_buttons = getattr(app, "_template_layer_field_buttons", None)
    group_buttons = getattr(app, "_template_layer_group_buttons", None)
    if field_buttons is None or group_buttons is None:
        app.template_build_layers_panel()
        return

    template = app.template_current()
    fields = template.get("fields", [])
    selected = set(getattr(app, "template_selected_fields", set()))
    if app.template_selected_field is not None:
        selected.add(app.template_selected_field)

    for idx, button in list(field_buttons.items()):
        if not (0 <= idx < len(fields)):
            app.template_build_layers_panel()
            return
        field = fields[idx]
        active = idx in selected
        locked = bool(field.get("locked", False))
        hidden = bool(field.get("hidden", False))
        group_name = app.template_group_name_for_field(idx) if hasattr(app, "template_group_name_for_field") else ""
        name = field.get("name", f"field_{idx+1}")
        if group_name:
            name = f"{name} · {group_name}"
        try:
            button.configure(
                text=("✓ " if active else "") + ("🚫 " if hidden else "") + ("🔒 " if locked else "") + name,
                fg_color=GOLD if active else "#171717",
                text_color="#111111" if active else "#D9C58C",
                hover_color=GOLD_DARK if active else "#2C2C2C",
            )
        except Exception:
            app.template_build_layers_panel()
            return

    selected_group_ids = app.template_selected_group_ids() if hasattr(app, "template_selected_group_ids") else set()
    groups_by_id = {group.get("id"): group for group in template.get("groups", [])}
    for group_id, button in list(group_buttons.items()):
        group = groups_by_id.get(group_id)
        if group is None:
            app.template_build_layers_panel()
            return
        active = group_id in selected_group_ids
        label = ("✓ " if active else "") + "📦 " + group.get("name", "Group")
        try:
            button.configure(
                text=label,
                fg_color=GOLD if active else "#202020",
                text_color="#111111" if active else "#D9C58C",
                hover_color=GOLD_DARK if active else "#303030",
            )
        except Exception:
            app.template_build_layers_panel()
            return


def select_layer(app: Any, idx):
    app.template_set_single_selection(idx)
    app.template_refresh_selection_ui()


def move_layer(app: Any, idx, direction):
    template = app.template_current()
    fields = template.get("fields", [])
    if not (0 <= idx < len(fields)):
        return

    new_idx = idx + int(direction)
    if not (0 <= new_idx < len(fields)):
        return

    if hasattr(app, "template_push_history"):
        app.template_push_history("layer order")

    fields[idx], fields[new_idx] = fields[new_idx], fields[idx]

    selected = set(getattr(app, "template_selected_fields", set()))
    updated = set()
    for s in selected:
        if s == idx:
            updated.add(new_idx)
        elif s == new_idx:
            updated.add(idx)
        else:
            updated.add(s)
    app.template_selected_fields = updated

    if app.template_selected_field == idx:
        app.template_selected_field = new_idx
    elif app.template_selected_field == new_idx:
        app.template_selected_field = idx

    save_template(app.template_selected_name, template)
    app.template_draw_canvas()
    app.template_build_layers_panel()
    if hasattr(app, "template_props_body"):
        app.template_build_properties_panel()
