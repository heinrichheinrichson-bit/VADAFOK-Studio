"""General actions for the currently selected Library asset."""

from __future__ import annotations

import os
from typing import Any
from tkinter import messagebox, simpledialog

from ..core.config import save_asset_meta


def toggle_favorite(app: Any) -> None:
    item = getattr(app, "selected_item", None)
    if item is None:
        messagebox.showwarning("Library", "Bitte zuerst ein Asset auswählen.")
        return
    key = app.item_key(item)
    favorites = app.asset_meta.setdefault("favorites", [])
    if key in favorites:
        favorites.remove(key)
    else:
        favorites.append(key)
    save_asset_meta(app.asset_meta)
    app.select_library_item(item)


def edit_tags(app: Any) -> None:
    item = getattr(app, "selected_item", None)
    if item is None:
        messagebox.showwarning("Library", "Bitte zuerst ein Asset auswählen.")
        return
    key = app.item_key(item)
    tags_by_asset = app.asset_meta.setdefault("tags", {})
    current = ", ".join(tags_by_asset.get(key, []))
    result = simpledialog.askstring(
        "Tags", "Tags mit Komma trennen:", initialvalue=current,
    )
    if result is None:
        return
    # Preserve entry order while preventing duplicate tags such as
    # "ending, Ending" from cluttering the Library display.
    tags: list[str] = []
    seen: set[str] = set()
    for raw_tag in result.split(","):
        tag = raw_tag.strip()
        normalized = tag.casefold()
        if tag and normalized not in seen:
            tags.append(tag)
            seen.add(normalized)
    tags_by_asset[key] = tags
    save_asset_meta(app.asset_meta)
    app.select_library_item(item)


def open_selected_folder(app: Any) -> None:
    item = getattr(app, "selected_item", None)
    if item is not None:
        os.startfile(item.path.parent)


def open_selected_file(app: Any) -> None:
    item = getattr(app, "selected_item", None)
    if item is not None:
        os.startfile(item.path)


def copy_selected_path(app: Any) -> None:
    item = getattr(app, "selected_item", None)
    if item is None:
        return
    app.clipboard_clear()
    app.clipboard_append(str(item.path))
    messagebox.showinfo("Copy Path", "Pfad kopiert.")
