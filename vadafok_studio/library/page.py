"""Library page construction.

The page keeps widget ownership on the application for compatibility with the
existing Library actions, while removing layout code from the app shell.
"""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from ..core.library import ROOT_FOLDERS

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
DARK = "#090909"
PANEL = "#111111"
TEXT = "#F2E2B6"


def show_library_page(app: Any) -> None:
    """Build and display the media Library workspace."""
    app.set_active("Library")
    app.clear_main()
    app.page_title("Library")

    # Opening the page stays cheap. Assets are loaded only after a folder was
    # selected, which also makes large project libraries responsive.
    app.library_items = []
    app.selected_item = None
    app.library_section.set("Folder Overview")

    outer = ctk.CTkFrame(app.main, fg_color=DARK)
    outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    outer.grid_columnconfigure(0, weight=3)
    outer.grid_columnconfigure(1, weight=1)
    outer.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(2, weight=1)

    top = ctk.CTkFrame(left, fg_color="transparent")
    top.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
    top.grid_columnconfigure(4, weight=1)

    ctk.CTkButton(
        top, text="FOLDERS", width=88, fg_color="#333333",
        hover_color="#444444", command=app.show_library_folder_overview,
    ).grid(row=0, column=0, padx=(0, 8))
    ctk.CTkLabel(top, text="Folder", text_color="#BCA870").grid(
        row=0, column=1, padx=(0, 8)
    )
    ctk.CTkOptionMenu(
        top, values=["Folder Overview"] + ROOT_FOLDERS,
        variable=app.library_section, fg_color="#1A1A1A",
        button_color=GOLD_DARK, command=app.library_section_changed,
    ).grid(row=0, column=2, sticky="w")
    ctk.CTkCheckBox(
        top, text="Favorites", variable=app.favorite_filter,
        text_color="#BCA870", command=app.render_library_grid,
    ).grid(row=0, column=3, padx=(18, 8))

    search = ctk.CTkEntry(
        top, textvariable=app.search_text,
        placeholder_text="Suche im geöffneten Ordner...",
    )
    search.grid(row=0, column=4, sticky="ew")
    search.bind("<KeyRelease>", lambda _event: app.render_library_grid())
    ctk.CTkButton(
        top, text="REFRESH FOLDER", fg_color=GOLD, text_color="#111111",
        hover_color=GOLD_DARK, command=app.reload_library,
    ).grid(row=0, column=5, padx=(12, 0))

    if app.library_banner_picker_mode:
        ctk.CTkButton(
            top, text="← BACK TO LIVE CARD", width=150, fg_color="#333333",
            hover_color="#444444", command=app.return_to_live_card_from_library,
        ).grid(row=0, column=6, padx=(8, 0))

    app.library_info = ctk.CTkLabel(
        left, text="", text_color="#D9C58C", anchor="w", justify="left",
    )
    app.library_info.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))
    if app.library_banner_picker_mode:
        app.library_info.configure(
            text=("LIVE CARD BANNER PICKER — Wähle ein Banner und nutze "
                  "SHOW / USE oder USE AS CAPTION BANNER."),
            text_color=GOLD,
        )

    app.library_grid = ctk.CTkScrollableFrame(
        left, fg_color="#0B0B0B", corner_radius=12,
    )
    app.library_grid.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))

    right = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(1, weight=1)
    ctk.CTkLabel(
        right, text="Selection", font=ctk.CTkFont(size=18, weight="bold"),
        text_color=GOLD,
    ).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

    app.selection_preview = ctk.CTkFrame(
        right, fg_color="#050505", corner_radius=12,
        border_color="#3A2A0D", border_width=1,
    )
    app.selection_preview.grid(row=1, column=0, padx=18, pady=8, sticky="nsew")
    app.selection_name = ctk.CTkLabel(
        right, text="Noch nichts ausgewählt", text_color=TEXT,
        wraplength=300, justify="left",
    )
    app.selection_name.grid(row=2, column=0, padx=18, pady=(8, 4), sticky="w")
    app.selection_meta = ctk.CTkLabel(
        right,
        text=("Banner auswählen und SHOW / USE drücken."
              if app.library_banner_picker_mode
              else "Wähle links zuerst einen Ordner."),
        text_color="#BCA870", wraplength=300, justify="left",
    )
    app.selection_meta.grid(row=3, column=0, padx=18, pady=(0, 12), sticky="w")
    ctk.CTkLabel(
        right, text="Actions", font=ctk.CTkFont(size=16, weight="bold"),
        text_color=GOLD,
    ).grid(row=4, column=0, padx=18, pady=(6, 4), sticky="w")

    actions = [
        ("SHOW / USE", app.default_selected_action, GOLD),
        ("USE AS CAPTION BANNER", app.use_selected_as_caption_banner, "#4A3913"),
        ("SHOW AS SCENE CARD", app.show_selected_scene_card, "#333333"),
        ("TOGGLE FAVORITE ⭐", app.toggle_selected_favorite, "#333333"),
        ("EDIT TAGS", app.edit_selected_tags, "#333333"),
        ("OPEN FOLDER", app.open_selected_folder, "#222222"),
        ("COPY PATH", app.copy_selected_path, "#222222"),
    ]
    for row, (text, command, color) in enumerate(actions, start=5):
        ctk.CTkButton(
            right, text=text, fg_color=color,
            text_color="#111111" if color == GOLD else TEXT,
            hover_color=GOLD_DARK if color in {GOLD, "#4A3913"} else "#444444",
            command=command,
        ).grid(row=row, column=0, padx=18, pady=4, sticky="ew")

    app.render_library_folder_overview()
