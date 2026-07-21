"""Layer-panel rendering for the Template Editor."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"


def build_layers_panel(app: Any) -> None:
    """Rebuild group and field rows in the Template Editor layer panel."""
    if not hasattr(app, "template_layers_body"):
        return

    for w in app.template_layers_body.winfo_children():
        w.destroy()

    template = app.template_current()
    try:
        app.template_clean_groups()
    except Exception:
        pass

    app._template_layer_row_for_group = {}
    app._template_layer_row_for_field = {}
    app._template_layer_group_buttons = {}
    app._template_layer_field_buttons = {}

    fields = template.get("fields", [])
    selected = set(getattr(app, "template_selected_fields", set()))
    if app.template_selected_field is not None:
        selected.add(app.template_selected_field)

    row = 0

    if not fields:
        ctk.CTkLabel(
            app.template_layers_body,
            text="Keine Felder",
            text_color="#777777",
            wraplength=160,
            justify="left"
        ).grid(row=0, column=0, columnspan=5, padx=8, pady=8, sticky="w")
        return

    # Group headers first.
    groups = template.get("groups", [])
    selected_group_ids = app.template_selected_group_ids() if hasattr(app, "template_selected_group_ids") else set()

    for group in groups:
        group_id = group.get("id")
        app._template_layer_row_for_group[group_id] = row

        active_group = group_id in selected_group_ids
        group_hidden = bool(group.get("hidden", False))
        group_locked = bool(group.get("locked", False))
        collapsed = app.template_group_is_collapsed(group_id)
        label = ("✓ " if active_group else "") + "📦 " + group.get("name", "Group")

        ctk.CTkButton(
            app.template_layers_body,
            text="▶" if collapsed else "▼",
            width=38,
            fg_color="#333333",
            hover_color="#444444",
            command=lambda gid=group_id: app.template_toggle_group_collapsed(gid)
        ).grid(row=row, column=0, padx=(8, 2), pady=(6, 3), sticky="ew")

        group_btn = ctk.CTkButton(
            app.template_layers_body,
            text=label,
            fg_color=GOLD if active_group else "#202020",
            text_color="#111111" if active_group else "#D9C58C",
            hover_color=GOLD_DARK if active_group else "#303030",
            anchor="w",
            command=lambda gid=group_id: app.template_select_group(gid)
        )
        group_btn.grid(row=row, column=1, padx=(2, 4), pady=(6, 3), sticky="ew")
        app._template_layer_group_buttons[group_id] = group_btn

        ctk.CTkButton(
            app.template_layers_body,
            text="✎",
            width=32,
            fg_color="#333333",
            hover_color="#444444",
            command=lambda gid=group_id: app.template_rename_group(gid)
        ).grid(row=row, column=2, padx=2, pady=(6, 3), sticky="ew")

        ctk.CTkButton(
            app.template_layers_body,
            text="👁" if not group_hidden else "🚫",
            width=40,
            height=32,
            fg_color="#333333" if not group_hidden else "#5A1F1F",
            hover_color="#444444" if not group_hidden else "#7A2A2A",
            command=lambda gid=group_id: app.template_toggle_group_hidden(gid)
        ).grid(row=row, column=3, padx=2, pady=(6, 3), sticky="ew")

        ctk.CTkButton(
            app.template_layers_body,
            text="🔒" if group_locked else "○",
            width=40,
            height=32,
            fg_color="#5A1F1F" if group_locked else "#333333",
            hover_color="#7A2A2A" if group_locked else "#444444",
            command=lambda gid=group_id: app.template_toggle_group_lock(gid)
        ).grid(row=row, column=4, padx=(2, 8), pady=(6, 3), sticky="ew")

        row += 1

    # Fields. Hide fields from layer list only when their group is collapsed.
    for idx in reversed(range(len(fields))):
        field = fields[idx]
        if app.template_field_is_in_collapsed_group(idx):
            continue

        app._template_layer_row_for_field[idx] = row

        active = idx in selected
        locked = bool(field.get("locked", False))
        hidden = bool(field.get("hidden", False))
        group_name = app.template_group_name_for_field(idx) if hasattr(app, "template_group_name_for_field") else ""

        name = field.get("name", f"field_{idx+1}")
        if group_name:
            name = f"{name} · {group_name}"

        row_frame = ctk.CTkFrame(app.template_layers_body, fg_color="transparent")
        row_frame.grid(row=row, column=0, columnspan=5, padx=8, pady=3, sticky="ew")
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, minsize=44)
        row_frame.grid_columnconfigure(2, minsize=44)
        row_frame.grid_columnconfigure(3, minsize=40)
        row_frame.grid_columnconfigure(4, minsize=40)

        btn = ctk.CTkButton(
            row_frame,
            text=("✓ " if active else "") + ("🚫 " if hidden else "") + ("🔒 " if locked else "") + name,
            fg_color=GOLD if active else "#171717",
            text_color="#111111" if active else "#D9C58C",
            hover_color=GOLD_DARK if active else "#2C2C2C",
            anchor="w",
            command=lambda i=idx: app.template_select_layer(i)
        )
        pad_left = 16 if group_name else 0
        btn.grid(row=0, column=0, padx=(pad_left, 4), pady=0, sticky="ew")
        app._template_layer_field_buttons[idx] = btn
        try:
            btn.bind("<Double-Button-1>", lambda _e, i=idx: app.template_start_inline_rename_field(i))
            btn.bind("<ButtonPress-1>", lambda e, i=idx: app.template_layer_drag_start(e, i), add="+")
            btn.bind("<B1-Motion>", app.template_layer_drag_motion, add="+")
            btn.bind("<ButtonRelease-1>", app.template_layer_drag_end, add="+")
        except Exception:
            pass

        ctk.CTkButton(
            row_frame,
            text="↑",
            width=44,
            height=32,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#333333",
            hover_color="#444444",
            command=lambda i=idx: app.template_move_layer(i, 1)
        ).grid(row=0, column=1, padx=2, pady=0, sticky="ew")

        ctk.CTkButton(
            row_frame,
            text="↓",
            width=44,
            height=32,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#333333",
            hover_color="#444444",
            command=lambda i=idx: app.template_move_layer(i, -1)
        ).grid(row=0, column=2, padx=2, pady=0, sticky="ew")

        ctk.CTkButton(
            row_frame,
            text="👁" if not hidden else "🚫",
            width=40,
            height=32,
            fg_color="#333333" if not hidden else "#5A1F1F",
            hover_color="#444444" if not hidden else "#7A2A2A",
            command=lambda i=idx: app.template_toggle_field_hidden(i)
        ).grid(row=0, column=3, padx=2, pady=0, sticky="ew")

        ctk.CTkButton(
            row_frame,
            text="🔒" if locked else "○",
            width=40,
            height=32,
            fg_color="#5A1F1F" if locked else "#333333",
            hover_color="#7A2A2A" if locked else "#444444",
            command=lambda i=idx: app.template_toggle_field_lock(i)
        ).grid(row=0, column=4, padx=(2, 0), pady=0, sticky="ew")

        row += 1

    app.template_layers_body.grid_columnconfigure(0, weight=1)
