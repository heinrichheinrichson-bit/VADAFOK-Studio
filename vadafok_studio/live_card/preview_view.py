"""Rendered Live Card preview presentation."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk
from PIL import Image


def _load_preview_image(path: Any) -> Image.Image:
    """Load a detached preview image without locking the rendered PNG."""
    with Image.open(path) as source:
        image = source.convert("RGBA")
    image.thumbnail((520, 300))
    return image


def update_render_preview(app: Any) -> None:
    if not hasattr(app, "preview_frame") or not hasattr(app, "message_box"):
        return
    for widget in app.preview_frame.winfo_children():
        widget.destroy()
    text = app.message_box.get("1.0", "end").strip() or "..."
    try:
        preview_path = app.render_smart_caption(text)
        image = _load_preview_image(preview_path)
        app.live_preview_image = ctk.CTkImage(
            light_image=image, dark_image=image, size=image.size,
        )
        ctk.CTkLabel(
            app.preview_frame, image=app.live_preview_image, text="",
        ).place(relx=0.5, rely=0.5, anchor="center")
        _update_ready_status(app)
    except Exception as error:
        ctk.CTkLabel(
            app.preview_frame,
            text=f"Preview konnte nicht gerendert werden:\n{error}",
            text_color="#D86A6A", wraplength=360, justify="center",
        ).place(relx=0.5, rely=0.5, anchor="center")
        if hasattr(app, "render_status_label"):
            app.render_status_label.configure(
                text="🔴 Preview error", text_color="#D86A6A",
            )


def _update_ready_status(app: Any) -> None:
    if not hasattr(app, "render_status_label"):
        return
    banner_name = app.live_card_current_banner_name()
    app.render_status_label.configure(
        text=(f"🟢 Preview ready\nEngine: {app.caption_engine.get()}\n"
              f"Banner: {banner_name}"),
        text_color="#8FE6A0",
    )
    if hasattr(app, "live_card_banner_name_label"):
        app.live_card_banner_name_label.configure(text=banner_name)
