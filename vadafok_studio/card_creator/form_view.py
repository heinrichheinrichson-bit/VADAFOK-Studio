"""Dynamic Card Creator form rendering."""

from __future__ import annotations

import customtkinter as ctk

from ..core import style_engine


def build_card_form(app) -> None:
    """Rebuild the selected template's editable field form."""
    for widget in app.card_form_frame.winfo_children():
        widget.destroy()

    fields = app.card_template().get("fields", [])
    template_name = app.card_selected_template.get()
    app.card_creator_values.setdefault(template_name, {})
    values = app.card_creator_values[template_name]

    if not fields:
        ctk.CTkLabel(
            app.card_form_frame,
            text="Dieses Template hat keine Felder.",
            text_color="#BCA870",
        ).grid(row=0, column=0, padx=12, pady=12, sticky="w")
        return

    style_options = ["Select Style"] + style_engine.list_styles()
    saved = app.card_saved_values.get(template_name, {})

    for row, field in enumerate(fields):
        name = field.get("name", f"field_{row + 1}")
        if name not in values or not hasattr(values.get(name), "get"):
            values[name] = ctk.StringVar(value=str(saved.get(name, "")))

        field_box = ctk.CTkFrame(
            app.card_form_frame,
            fg_color="#111111",
            corner_radius=10,
        )
        field_box.grid(row=row, column=0, padx=10, pady=(8, 4), sticky="ew")
        field_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            field_box,
            text=name.replace("_", " ").title(),
            text_color="#BCA870",
        ).grid(row=0, column=0, padx=10, pady=(8, 2), sticky="w")

        entry = ctk.CTkEntry(field_box, textvariable=values[name])
        entry.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")
        if not getattr(values[name], "_vadafok_card_preview_trace", None):
            trace_id = values[name].trace_add("write", app.card_preview_changed)
            values[name]._vadafok_card_preview_trace = trace_id

        style_row = ctk.CTkFrame(field_box, fg_color="transparent")
        style_row.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        style_row.grid_columnconfigure(0, weight=1)

        style_variable = ctk.StringVar(value="Select Style")
        style_menu = ctk.CTkOptionMenu(
            style_row,
            values=style_options,
            variable=style_variable,
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555",
            command=lambda selected, field_name=name: app.card_apply_style_to_field(
                field_name, selected
            ),
        )
        style_menu.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(
            style_row,
            text="EDIT",
            width=54,
            fg_color="#333333",
            hover_color="#444444",
            command=app.card_open_template_editor_for_styles,
        ).grid(row=0, column=1, sticky="e")
