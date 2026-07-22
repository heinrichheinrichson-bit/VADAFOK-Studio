"""Folder overview and asset-grid rendering for the Library page."""

from __future__ import annotations

from typing import Any, Iterable

import customtkinter as ctk

from ..core.banner_profiles import has_profile
from ..core.library import ROOT_FOLDERS, library_section_exists

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
TEXT = "#F2E2B6"

SECTION_BADGES = {
    "Library": "LIB", "Live Cards": "LIVE", "Scene Cards": "SCN",
    "Banners": "BNR", "Templates": "TPL", "Fonts": "FNT",
    "Sounds": "SND", "Projects": "PRJ",
}


def filter_library_items(
    items: Iterable[Any], query: str, favorites_only: bool,
    is_favorite: Any, tags_for: Any,
) -> list[Any]:
    """Return items matching the active filters, preserving source order."""
    result = list(items)
    if favorites_only:
        result = [item for item in result if is_favorite(item)]
    query = str(query or "").strip().casefold()
    if not query:
        return result
    return [
        item for item in result
        if query in item.name.casefold()
        or query in item.category.casefold()
        or query in item.relative.casefold()
        or any(query in tag.casefold() for tag in tags_for(item))
    ]


def render_folder_overview(app: Any) -> None:
    """Render folder choices without scanning or decoding thumbnails."""
    if not hasattr(app, "library_grid"):
        return
    for widget in app.library_grid.winfo_children():
        widget.destroy()
    app.thumbnail_refs = []
    app.library_asset_cards = {}
    project_folder = app.project_folder.get()
    app.library_info.configure(
        text=f"Projektordner: {project_folder or '(nicht gesetzt)'}    Bitte zuerst einen Ordner auswählen."
    )

    intro = ctk.CTkFrame(
        app.library_grid, fg_color="#111111", corner_radius=12,
        border_color="#3A2A0D", border_width=1,
    )
    intro.grid(row=0, column=0, columnspan=3, padx=12, pady=(12, 6), sticky="ew")
    intro.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(
        intro, text="Medienordner", text_color=GOLD,
        font=ctk.CTkFont(size=20, weight="bold"),
    ).grid(row=0, column=0, padx=16, pady=(14, 3), sticky="w")
    ctk.CTkLabel(
        intro,
        text=("Wähle zuerst einen Ordner. Erst danach lädt VADAFOK "
              "die Dateien und Vorschaubilder dieses Ordners."),
        text_color="#BCA870", wraplength=760, justify="left",
    ).grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")

    columns = 3
    for index, section in enumerate(ROOT_FOLDERS):
        row, column = divmod(index, columns)
        available = library_section_exists(project_folder, section)
        card = ctk.CTkFrame(
            app.library_grid, fg_color="#171717" if available else "#101010",
            corner_radius=12, border_color=GOLD if available else "#252525",
            border_width=1,
        )
        card.grid(row=row + 1, column=column, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text=SECTION_BADGES.get(section, "DIR"), width=54, height=38,
            fg_color=GOLD if available else "#333333",
            text_color="#111111" if available else "#777777", corner_radius=9,
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=0, column=0, padx=14, pady=(14, 6))
        ctk.CTkLabel(
            card, text=section, text_color=TEXT if available else "#777777",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=1, column=0, padx=14, pady=(0, 3))
        ctk.CTkLabel(
            card, text="Ordner öffnen" if available else "Nicht gefunden",
            text_color="#BCA870" if available else "#666666",
            font=ctk.CTkFont(size=11),
        ).grid(row=2, column=0, padx=14, pady=(0, 8))
        ctk.CTkButton(
                card, text="ÖFFNEN", height=34,
            fg_color=GOLD if available else "#333333",
            text_color="#111111" if available else "#777777",
            hover_color=GOLD_DARK if available else "#333333",
            state="normal" if available else "disabled",
            command=lambda selected=section: app.open_library_section(selected),
        ).grid(row=3, column=0, padx=14, pady=(0, 14), sticky="ew")
    for column in range(columns):
        app.library_grid.grid_columnconfigure(column, weight=1)


def render_asset_grid(app: Any) -> None:
    """Render filtered assets from the currently loaded folder."""
    if not hasattr(app, "library_grid"):
        return
    section = str(app.library_section.get() or "").strip()
    if section in {"", "All", "Folder Overview"}:
        render_folder_overview(app)
        return
    for widget in app.library_grid.winfo_children():
        widget.destroy()
    app.thumbnail_refs = []
    app.library_asset_cards = {}
    items = filter_library_items(
        app.library_items, app.search_text.get(), app.favorite_filter.get(),
        app.item_is_favorite, app.item_tags,
    )
    app.library_info.configure(
        text=(f"Ordner: {section}    Treffer: {len(items)}    "
              f"Dateien im Ordner: {len(app.library_items)}")
    )
    if not items:
        ctk.CTkLabel(
            app.library_grid,
            text="Keine Treffer in diesem Ordner. Prüfe Suche, Favoritenfilter oder Projektordner.",
            text_color="#BCA870",
        ).grid(row=0, column=0, padx=18, pady=18, sticky="w")
        return

    columns = 4
    for index, item in enumerate(items):
        row, column = divmod(index, columns)
        selected = app.selected_item and app.item_key(app.selected_item) == app.item_key(item)
        card = ctk.CTkFrame(
            app.library_grid, fg_color="#151515", corner_radius=10,
            border_color=GOLD if selected else "#151515", border_width=2,
        )
        card.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        app.library_asset_cards[app.item_key(item)] = card
        favorite = app.item_is_favorite(item)
        profile = item.section == "Banners" and has_profile(
            app.banner_profiles, app.item_key(item)
        )
        ctk.CTkLabel(
            card, text=("⭐ " if favorite else "") + item.section + (" ✓" if profile else ""),
            text_color=GOLD if favorite else "#BCA870", font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=10, pady=(8, 0))
        image_label = app.make_thumb_label(card, item.path)
        image_label.pack(padx=10, pady=(6, 6))
        name_label = ctk.CTkLabel(
            card, text=item.name, text_color=TEXT, wraplength=210, justify="center",
        )
        name_label.pack(padx=10, pady=(0, 2))
        for widget in (card, image_label, name_label):
            widget.bind("<Button-1>", lambda _event, asset=item: app.select_library_item(asset))
            widget.bind("<Double-Button-1>", lambda _event, asset=item: app.library_item_double_click(asset))
        ctk.CTkLabel(
            card, text=item.category, text_color="#BCA870", wraplength=210,
            justify="center", font=ctk.CTkFont(size=12),
        ).pack(padx=10, pady=(0, 4))
        ctk.CTkLabel(
            card, text=", ".join(app.item_tags(item)[:4]), text_color="#8F8058",
            wraplength=210, justify="center", font=ctk.CTkFont(size=11),
        ).pack(padx=10, pady=(0, 10))
    for column in range(columns):
        app.library_grid.grid_columnconfigure(column, weight=1)
