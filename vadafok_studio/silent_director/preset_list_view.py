"""Preset-list rendering for the Silent Director page."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk


GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
TEXT = "#F2E2B6"


def render_filtered_presets(app: Any, *_args: Any) -> None:
    """Incrementally synchronize visible preset rows."""
    preset_list = getattr(app, "silent_director_preset_list_frame", None)
    if preset_list is None:
        return

    filtered = app.silent_director_filtered_presets()
    query = str(app.silent_director_search_var.get() or "").strip()
    widgets = getattr(app, "silent_director_preset_row_widgets", {}) or {}
    visible_names = [str(item.get("name", "Untitled")) for item in filtered]

    for name in list(widgets):
        if name not in visible_names:
            widgets.pop(name)["row"].destroy()

    for child in list(preset_list.winfo_children()):
        if getattr(child, "_silent_director_hint", False):
            child.destroy()

    if not filtered:
        message = "No matching presets." if query else "No presets yet."
        hint = ctk.CTkLabel(preset_list, text=message, text_color="#777777")
        hint._silent_director_hint = True
        hint.grid(
            row=0, column=0, padx=10, pady=(12, 4), sticky="w"
        )
        if query:
            clear = ctk.CTkButton(
                preset_list,
                text="CLEAR SEARCH",
                width=120,
                fg_color="#333333",
                hover_color="#444444",
                command=app.silent_director_clear_search,
            )
            clear._silent_director_hint = True
            clear.grid(row=1, column=0, padx=10, pady=(4, 12), sticky="w")
        app.silent_director_preset_row_widgets = widgets
        return

    for idx, preset in enumerate(filtered):
        name = str(preset.get("name", "Untitled"))
        if name not in widgets:
            widgets[name] = _render_preset_row(app, preset_list, preset, idx)
        _update_preset_row(app, widgets[name], preset, idx)
    app.silent_director_preset_row_widgets = widgets


def _render_preset_row(app: Any, preset_list: Any, preset: dict, row_index: int) -> dict:
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

    icon = ctk.CTkLabel(
        row,
        text=app.silent_director_preset_icon(preset),
        width=44,
        height=34,
        fg_color=GOLD if is_favorite else "#242424",
        text_color="#111111" if is_favorite else "#D9C58C",
        corner_radius=9,
        font=ctk.CTkFont(size=10, weight="bold"),
    )
    icon.grid(row=0, column=1, rowspan=2, padx=(2, 2), pady=6)
    favorite = ctk.CTkButton(
        row,
        text="★" if is_favorite else "☆",
        width=38,
        fg_color="transparent",
        hover_color="#2C2C2C",
        text_color=GOLD if is_favorite else "#777777",
        command=lambda p=preset: app.silent_director_toggle_favorite(p),
    )
    favorite.grid(row=0, column=0, rowspan=2, padx=(6, 2), pady=6)
    name_button = ctk.CTkButton(
        row,
        text=name,
        anchor="w",
        fg_color="transparent",
        hover_color="#2C2C2C",
        text_color=GOLD if selected or is_favorite else TEXT,
        command=lambda n=name: app.silent_director_select_preset(n),
    )
    name_button.grid(row=0, column=2, sticky="ew", padx=6, pady=(5, 0))
    stats = ctk.CTkLabel(
        row,
        text=app.silent_director_preset_stats_text(preset),
        text_color="#888888",
        anchor="w",
        font=ctk.CTkFont(size=11),
    )
    stats.grid(row=1, column=2, sticky="ew", padx=14, pady=(0, 6))

    controls = ctk.CTkFrame(row, fg_color="transparent")
    controls.grid(row=0, column=3, rowspan=2, padx=(4, 8), pady=6)
    run = ctk.CTkButton(
        controls,
        text="RUN",
        width=58,
        fg_color=GOLD,
        text_color="#111111",
        hover_color=GOLD_DARK,
        command=lambda p=preset: app.silent_director_run_preset(p),
    )
    run.grid(row=0, column=0, padx=2, pady=2)
    duplicate = ctk.CTkButton(
        controls,
        text="DUP",
        width=48,
        fg_color="#2D4B3A",
        text_color="#D9F6E2",
        hover_color="#3B624C",
        command=lambda p=preset: app.silent_director_duplicate_preset(p),
    )
    duplicate.grid(row=1, column=0, padx=2, pady=2)
    return {
        "row": row, "icon": icon, "favorite": favorite,
        "name": name_button, "stats": stats, "run": run, "duplicate": duplicate,
        "state": {
            "name": name, "selected": selected, "favorite": is_favorite,
            "icon": app.silent_director_preset_icon(preset),
            "stats": app.silent_director_preset_stats_text(preset),
            "content": repr(preset), "row": row_index,
        },
    }


def _update_preset_row(app: Any, widgets: dict, preset: dict, row_index: int) -> None:
    name = str(preset.get("name", "Untitled"))
    selected = name == app.silent_director_selected.get()
    favorite = bool(preset.get("favorite", False))
    icon = app.silent_director_preset_icon(preset)
    stats = app.silent_director_preset_stats_text(preset)
    content = repr(preset)
    old = widgets.get("state", {})
    if old.get("row") != row_index:
        widgets["row"].grid(row=row_index, column=0, padx=6, pady=4, sticky="ew")
    if old.get("selected") != selected or old.get("favorite") != favorite:
        widgets["row"].configure(
            fg_color="#241F12" if favorite else ("#171717" if selected else "transparent"),
            border_color=GOLD if favorite else "#171717",
            border_width=1 if favorite else 0,
        )
        widgets["name"].configure(
            text_color=GOLD if selected or favorite else TEXT,
        )
    if old.get("favorite") != favorite or old.get("icon") != icon:
        widgets["icon"].configure(
            text=icon, fg_color=GOLD if favorite else "#242424",
            text_color="#111111" if favorite else "#D9C58C",
        )
        widgets["favorite"].configure(
            text="★" if favorite else "☆", text_color=GOLD if favorite else "#777777",
        )
    if old.get("name") != name:
        widgets["name"].configure(text=name)
    if old.get("stats") != stats:
        widgets["stats"].configure(text=stats)
    if old.get("content") != content:
        widgets["favorite"].configure(
            command=lambda item=preset: app.silent_director_toggle_favorite(item),
        )
        widgets["name"].configure(
            command=lambda value=name: app.silent_director_select_preset(value),
        )
        widgets["run"].configure(
            command=lambda item=preset: app.silent_director_run_preset(item),
        )
        widgets["duplicate"].configure(
            command=lambda item=preset: app.silent_director_duplicate_preset(item),
        )
    widgets["state"] = {
        "name": name, "selected": selected, "favorite": favorite,
        "icon": icon, "stats": stats, "content": content, "row": row_index,
    }
