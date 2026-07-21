"""Properties-panel rendering for the Template Editor."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

TEXT = "#F2E2B6"


def build_properties_panel(app: Any) -> None:
    """Build cached property widgets and update their visible state."""
    """Build Properties widgets once and only switch their visible state afterwards."""
    if not hasattr(app, "template_props_body"):
        return

    body = app.template_props_body
    cached_body = getattr(app, "_template_properties_body_ref", None)
    editor = getattr(app, "_template_properties_editor", None)
    empty_label = getattr(app, "_template_properties_empty_label", None)

    cache_valid = cached_body is body and editor is not None and empty_label is not None
    if cache_valid:
        try:
            cache_valid = bool(editor.winfo_exists()) and bool(empty_label.winfo_exists())
        except Exception:
            cache_valid = False

    if not cache_valid:
        for widget in body.winfo_children():
            widget.destroy()

        body.grid_columnconfigure(0, weight=1)
        empty_label = ctk.CTkLabel(
            body,
            text="Kein Feld ausgewählt.",
            text_color="#BCA870",
            wraplength=220,
            justify="left",
        )
        empty_label.grid(row=0, column=0, padx=12, pady=12, sticky="w")

        editor = ctk.CTkFrame(body, fg_color="transparent")
        editor.grid(row=0, column=0, sticky="ew")
        editor.grid_columnconfigure(1, weight=1)

        fields = [
            ("Name", app.template_prop_name),
            ("Font", app.template_prop_font_family),
            ("Size", app.template_prop_font_size),
            ("Text Color", app.template_prop_text_color),
            ("Stroke Color", app.template_prop_stroke_color),
            ("Stroke Width", app.template_prop_stroke_width),
        ]

        app._template_property_entries = {}
        for row, (label, var) in enumerate(fields):
            ctk.CTkLabel(editor, text=label, text_color="#BCA870").grid(
                row=row, column=0, padx=(12, 8), pady=6, sticky="w"
            )
            entry = ctk.CTkEntry(editor, textvariable=var)
            entry.grid(row=row, column=1, padx=(0, 12), pady=6, sticky="ew")
            entry.bind("<KeyRelease>", lambda _event: app.template_apply_selected_properties())
            app._template_property_entries[label] = entry
            if label == "Name":
                app.template_prop_name_entry = entry

        app._template_property_uppercase = ctk.CTkCheckBox(
            editor,
            text="Uppercase",
            variable=app.template_prop_uppercase,
            text_color=TEXT,
            command=app.template_apply_selected_properties,
        )
        app._template_property_uppercase.grid(
            row=len(fields), column=0, columnspan=2, padx=12, pady=8, sticky="w"
        )

        ctk.CTkLabel(
            editor,
            text="Änderungen werden automatisch gespeichert.",
            text_color="#D9C58C",
            wraplength=220,
            justify="left",
        ).grid(
            row=len(fields) + 1,
            column=0,
            columnspan=2,
            padx=12,
            pady=(8, 12),
            sticky="w",
        )

        app._template_properties_body_ref = body
        app._template_properties_editor = editor
        app._template_properties_empty_label = empty_label

    if app.template_selected_field is None:
        editor.grid_remove()
        empty_label.grid()
    else:
        empty_label.grid_remove()
        editor.grid()
