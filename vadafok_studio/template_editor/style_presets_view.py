"""Style preset list rendering for the Template Editor."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from ..core import style_engine


def build_style_presets_panel(app: Any) -> None:
    body = getattr(app, "template_styles_body", None)
    if body is None:
        return
    for widget in body.winfo_children():
        widget.destroy()
    styles = style_engine.list_styles()
    if not styles:
        ctk.CTkLabel(
            body, text="Noch keine Styles gespeichert.", text_color="#777777",
            wraplength=170, justify="left",
        ).grid(row=0, column=0, columnspan=2, padx=8, pady=8, sticky="w")
        return
    for row, name in enumerate(styles):
        ctk.CTkButton(
            body, text=name, anchor="w", fg_color="#171717",
            hover_color="#2C2C2C", text_color="#D9C58C",
            command=lambda selected=name: app.template_apply_style_preset(selected),
        ).grid(row=row, column=0, padx=(8, 4), pady=3, sticky="ew")
        ctk.CTkButton(
            body, text="DEL", width=44, fg_color="#5A1F1F",
            hover_color="#7A2A2A",
            command=lambda selected=name: app.template_delete_style_preset(selected),
        ).grid(row=row, column=1, padx=(2, 8), pady=3, sticky="ew")
    body.grid_columnconfigure(0, weight=1)
