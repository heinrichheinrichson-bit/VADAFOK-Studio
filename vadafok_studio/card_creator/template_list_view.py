"""Template-list and recent-template rendering for Card Creator."""

from __future__ import annotations

import customtkinter as ctk

from ..core.recent_templates import load_recent_templates
from ..core.template_store import list_templates

GOLD = "#D6A43A"


def build_all_template_buttons(app) -> None:
    frame = getattr(app, "card_all_templates_frame", None)
    if frame is None:
        return
    try:
        if not frame.winfo_exists():
            return
    except Exception:
        return

    for child in frame.winfo_children():
        child.destroy()

    app.card_template_buttons = {}
    for name in sorted(list_templates()):
        prefix = "✓ " if name == app.card_selected_template.get() else ""
        button = ctk.CTkButton(
            frame,
            text=prefix + name,
            anchor="w",
            fg_color="#171717",
            hover_color="#2C2C2C",
            command=lambda selected=name: app.card_creator_controller.select_template(
                selected
            ),
        )
        button.pack(fill="x", padx=8, pady=4)
        app.card_template_buttons[name] = button


def refresh_all_templates(app) -> None:
    buttons = getattr(app, "card_template_buttons", {})
    available_names = sorted(list_templates())
    if set(buttons) != set(available_names):
        build_all_template_buttons(app)
        return

    selected = app.card_selected_template.get()
    for name, button in buttons.items():
        try:
            prefix = "✓ " if name == selected else ""
            button.configure(text=prefix + name)
        except Exception:
            build_all_template_buttons(app)
            return


def refresh_recent_templates(app) -> None:
    frame = getattr(app, "card_recent_templates_frame", None)
    if frame is None:
        return
    try:
        if not frame.winfo_exists():
            return
    except Exception:
        return

    for child in frame.winfo_children():
        child.destroy()

    recent_names = load_recent_templates(list_templates())
    app.card_recent_templates = recent_names
    if not recent_names:
        frame.pack_forget()
        return

    frame.pack(fill="x", padx=0, pady=0, before=app.card_all_templates_label)
    ctk.CTkLabel(
        frame,
        text="RECENT TEMPLATES",
        text_color=GOLD,
        anchor="w",
        font=ctk.CTkFont(size=12, weight="bold"),
    ).pack(fill="x", padx=8, pady=(8, 3))

    for recent_name in recent_names:
        recent_row = ctk.CTkFrame(frame, fg_color="transparent")
        recent_row.pack(fill="x", padx=8, pady=3)
        recent_row.grid_columnconfigure(0, weight=1)
        prefix = "✓ " if recent_name == app.card_selected_template.get() else "↶ "

        ctk.CTkButton(
            recent_row,
            text=prefix + recent_name,
            anchor="w",
            fg_color="#3A2A0D",
            hover_color="#5A4318",
            command=lambda selected=recent_name: app.card_creator_controller.select_template(
                selected
            ),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ctk.CTkButton(
            recent_row,
            text="✕",
            width=28,
            fg_color="#5A2424",
            hover_color="#7A3030",
            command=lambda selected=recent_name: app.card_creator_controller.remove_recent(
                selected
            ),
        ).grid(row=0, column=1)
