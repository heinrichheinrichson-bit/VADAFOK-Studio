"""Quick Cards page construction."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from ..core import text_library_engine

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
DARK = "#090909"
PANEL = "#111111"


def show_quick_cards_page(app: Any) -> None:
    app.set_active("Quick Cards")
    app.clear_main()
    app.page_title("Schnelltexte")
    app.text_library_data = text_library_engine.load_library()

    outer = ctk.CTkFrame(app.main, fg_color=DARK)
    outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    outer.grid_columnconfigure(0, weight=2)
    outer.grid_columnconfigure(1, weight=1)
    outer.grid_rowconfigure(0, weight=1)

    app.quick_cards_tree = ctk.CTkScrollableFrame(
        outer, fg_color=PANEL, corner_radius=18,
    )
    app.quick_cards_tree.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    app.quick_cards_tree.grid_columnconfigure(0, weight=1)

    manager = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    manager.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
    manager.grid_columnconfigure(0, weight=1)

    categories = sorted(app.text_library_data) or ["Chat"]
    if app.quick_cards_target_category.get() not in categories:
        app.quick_cards_target_category.set(categories[0])

    ctk.CTkLabel(
        manager, text="Schnelltexte verwalten", text_color=GOLD,
        font=ctk.CTkFont(size=18, weight="bold"),
    ).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
    ctk.CTkLabel(manager, text="Zielkategorie", text_color="#BCA870").grid(
        row=1, column=0, padx=18, pady=(8, 4), sticky="w",
    )
    app.quick_cards_category_menu = ctk.CTkOptionMenu(
        manager, values=categories, variable=app.quick_cards_target_category,
        fg_color="#333333", button_color="#444444",
        button_hover_color="#555555",
    )
    app.quick_cards_category_menu.grid(
        row=2, column=0, padx=18, pady=(0, 12), sticky="ew",
    )

    ctk.CTkLabel(manager, text="Neue Kategorie", text_color="#BCA870").grid(
        row=3, column=0, padx=18, pady=(8, 4), sticky="w",
    )
    category_entry = ctk.CTkEntry(
        manager, textvariable=app.text_library_new_category,
    )
    category_entry.grid(row=4, column=0, padx=18, pady=(0, 8), sticky="ew")
    category_entry.bind("<Return>", lambda _event: app.quick_cards_add_category())
    ctk.CTkButton(
        manager, text="+ KATEGORIE HINZUFÃœGEN", fg_color="#333333",
        hover_color="#444444", command=app.quick_cards_add_category,
    ).grid(row=5, column=0, padx=18, pady=(0, 12), sticky="ew")

    ctk.CTkLabel(manager, text="Neuer Text", text_color="#BCA870").grid(
        row=6, column=0, padx=18, pady=(8, 4), sticky="w",
    )
    text_entry = ctk.CTkEntry(
        manager, textvariable=app.text_library_new_text,
    )
    text_entry.grid(row=7, column=0, padx=18, pady=(0, 8), sticky="ew")
    text_entry.bind("<Return>", lambda _event: app.quick_cards_add_text())

    buttons = (
        ("+ TEXT SPEICHERN", app.quick_cards_add_text, GOLD, "#111111"),
        ("LIVE-KARTEN-TEXT SPEICHERN", app.quick_cards_save_live_text, "#333333", None),
        ("LIVE-KARTE Ã–FFNEN", app.show_live_card, "#333333", None),
    )
    for row, (label, command, color, text_color) in enumerate(buttons, start=8):
        options = {"text_color": text_color} if text_color else {}
        ctk.CTkButton(
            manager, text=label, fg_color=color,
            hover_color=GOLD_DARK if color == GOLD else "#444444",
            command=command, **options,
        ).grid(row=row, column=0, padx=18, pady=(0, 8), sticky="ew")

    ctk.CTkLabel(
        manager,
        text=("Ein Klick auf einen Text links Ã¼bergibt ihn direkt an die Live-Karte.\n"
              "Neue Texte werden in der gewÃ¤hlten Zielkategorie gespeichert."),
        text_color="#777777", justify="left", wraplength=300,
    ).grid(row=11, column=0, padx=18, pady=(8, 18), sticky="w")
    app.quick_cards_build_tree()
