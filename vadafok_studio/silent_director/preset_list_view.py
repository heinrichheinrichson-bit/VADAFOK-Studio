"""Preset-list rendering for the Silent Director page."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk


GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
TEXT = "#F2E2B6"


def render_filtered_presets(app: Any, *_args: Any) -> None:
    """Rebuild the visible preset rows from the app's current filter state."""
    preset_list = getattr(app, "silent_director_preset_list_frame", None)
    if preset_list is None:
        return

    for child in preset_list.winfo_children():
        child.destroy()

    filtered = app.silent_director_filtered_presets()
    query = str(app.silent_director_search_var.get() or "").strip()

    if not filtered:
        message = "No matching presets." if query else "No presets yet."
        ctk.CTkLabel(preset_list, text=message, text_color="#777777").grid(
            row=0, column=0, padx=10, pady=(12, 4), sticky="w"
        )
        if query:
            ctk.CTkButton(
                preset_list,
                text="CLEAR SEARCH",
                width=120,
                fg_color="#333333",
                hover_color="#444444",
                command=app.silent_director_clear_search,
            ).grid(row=1, column=0, padx=10, pady=(4, 12), sticky="w")
        return

    row_offset = 0
    if query:
        ctk.CTkLabel(
            preset_list,
            text=f"{len(filtered)} Treffer",
            text_color="#777777",
            font=ctk.CTkFont(size=11),
        ).grid(row=0, column=0, padx=10, pady=(8, 2), sticky="w")
        row_offset = 1

    for idx, preset in enumerate(filtered):
        _render_preset_row(app, preset_list, preset, idx + row_offset)


def _render_preset_row(app: Any, preset_list: Any, preset: dict, row_index: int) -> None:
    name = preset.get("name", "Untitled")
    selected = name == app.silent_director_selected.get()
    is_favorite = bool(preset.get("favorite", False))
    row = ctk.CTkFrame(
        preset_list,
        fg_color="#241F12" if is_favorite else ("#171717" if selected else "transparent"),
        corner_radius=8,
        border_color=GOLD if is_favorite else "#171717",
        border_width=1 if is_favorite else 0,
    )
    row.grid(row=row_index, column=0, padx=6, pady=4, sticky="ew")
    row.grid_columnconfigure(2, weight=1)

    ctk.CTkLabel(
        row,
        text=app.silent_director_preset_icon(preset),
        width=44,
        height=34,
        fg_color=GOLD if is_favorite else "#242424",
        text_color="#111111" if is_favorite else "#D9C58C",
        corner_radius=9,
        font=ctk.CTkFont(size=10, weight="bold"),
    ).grid(row=0, column=1, rowspan=2, padx=(2, 2), pady=6)
    ctk.CTkButton(
        row,
        text="★" if is_favorite else "☆",
        width=38,
        fg_color="transparent",
        hover_color="#2C2C2C",
        text_color=GOLD if is_favorite else "#777777",
        command=lambda p=preset: app.silent_director_toggle_favorite(p),
    ).grid(row=0, column=0, rowspan=2, padx=(6, 2), pady=6)
    ctk.CTkButton(
        row,
        text=name,
        anchor="w",
        fg_color="transparent",
        hover_color="#2C2C2C",
        text_color=GOLD if selected or is_favorite else TEXT,
        command=lambda n=name: app.silent_director_select_preset(n),
    ).grid(row=0, column=2, sticky="ew", padx=6, pady=(5, 0))
    ctk.CTkLabel(
        row,
        text=app.silent_director_preset_stats_text(preset),
        text_color="#888888",
        anchor="w",
        font=ctk.CTkFont(size=11),
    ).grid(row=1, column=2, sticky="ew", padx=14, pady=(0, 6))

    controls = ctk.CTkFrame(row, fg_color="transparent")
    controls.grid(row=0, column=3, rowspan=2, padx=(4, 8), pady=6)
    ctk.CTkButton(
        controls,
        text="RUN",
        width=58,
        fg_color=GOLD,
        text_color="#111111",
        hover_color=GOLD_DARK,
        command=lambda p=preset: app.silent_director_run_preset(p),
    ).grid(row=0, column=0, padx=2, pady=2)
    ctk.CTkButton(
        controls,
        text="DUP",
        width=48,
        fg_color="#2D4B3A",
        text_color="#D9F6E2",
        hover_color="#3B624C",
        command=lambda p=preset: app.silent_director_duplicate_preset(p),
    ).grid(row=1, column=0, padx=2, pady=2)
