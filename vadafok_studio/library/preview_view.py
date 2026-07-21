"""Thumbnail and selection-preview rendering for Library assets."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk
from PIL import Image

GOLD = "#D6A43A"


def _load_thumbnail(path: Any, maximum_size: tuple[int, int]) -> Image.Image:
    """Load a detached RGBA thumbnail without keeping the source file open."""
    with Image.open(path) as source:
        image = source.convert("RGBA")
    image.thumbnail(maximum_size)
    return image


def make_thumbnail_label(app: Any, parent: Any, path: Any) -> Any:
    """Create a visual thumbnail or a media-type placeholder."""
    try:
        if path.suffix.casefold() in {".png", ".jpg", ".jpeg", ".webp"}:
            image = _load_thumbnail(path, (220, 124))
            thumbnail = ctk.CTkImage(
                light_image=image, dark_image=image, size=image.size,
            )
            app.thumbnail_refs.append(thumbnail)
            return ctk.CTkLabel(parent, image=thumbnail, text="")
        return ctk.CTkLabel(
            parent, text="♪ SOUND", text_color=GOLD, width=220, height=124,
            fg_color="#050505", corner_radius=8,
        )
    except Exception:
        return ctk.CTkLabel(
            parent, text="[kann nicht geladen werden]", text_color="#D86A6A",
            width=220, height=124,
        )


def select_library_item(app: Any, item: Any) -> None:
    """Select an asset and update the detail preview."""
    app.selected_item = item
    app.preview_refs = []
    preview_frame = getattr(app, "selection_preview", None)
    if preview_frame is not None:
        for widget in preview_frame.winfo_children():
            widget.destroy()

    try:
        if item.kind == "image":
            image = _load_thumbnail(item.path, (320, 280))
            preview = ctk.CTkImage(
                light_image=image, dark_image=image, size=image.size,
            )
            app.preview_refs.append(preview)
            ctk.CTkLabel(preview_frame, image=preview, text="").place(
                relx=0.5, rely=0.5, anchor="center",
            )
        else:
            ctk.CTkLabel(
                preview_frame, text="♪ SOUND", text_color=GOLD,
                font=ctk.CTkFont(size=28, weight="bold"),
            ).place(relx=0.5, rely=0.5, anchor="center")
    except Exception:
        ctk.CTkLabel(
            preview_frame, text="Asset kann nicht geladen werden",
            text_color="#D86A6A",
        ).place(relx=0.5, rely=0.5, anchor="center")

    favorite = "⭐ " if app.item_is_favorite(item) else ""
    app.selection_name.configure(text=favorite + item.name)
    tags = ", ".join(app.item_tags(item)) or "keine"
    app.selection_meta.configure(
        text=(f"{item.section} / {item.category}\n{item.relative}\n"
              f"Tags: {tags}\nTyp: {item.kind}")
    )
    app.render_library_grid()
