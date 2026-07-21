"""Rendered Live Card preview presentation."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk
from PIL import Image


def _load_preview_image(path: Any, bounds: tuple[int, int] = (520, 300)) -> Image.Image:
    """Load a detached preview image without locking the rendered PNG."""
    with Image.open(path) as source:
        image = source.convert("RGBA")
    image.thumbnail(bounds)
    return image


def schedule_render_preview(app: Any, delay: int = 140) -> None:
    """Debounce typing so rapid key presses trigger only one render."""
    job = getattr(app, "live_preview_update_job", None)
    if job is not None:
        try:
            app.after_cancel(job)
        except Exception:
            pass
    app.live_preview_update_job = app.after(delay, app.update_render_preview)


def update_render_preview(app: Any) -> None:
    app.live_preview_update_job = None
    if not hasattr(app, "preview_frame") or not hasattr(app, "message_box"):
        return
    text = app.message_box.get("1.0", "end").strip() or "..."
    try:
        preview_path = app.render_smart_caption(text)
        try:
            bounds = (
                max(160, min(760, app.preview_frame.winfo_width() - 24)),
                max(120, min(520, app.preview_frame.winfo_height() - 24)),
            )
        except Exception:
            bounds = (520, 300)
        image = _load_preview_image(preview_path, bounds)
        app.live_preview_image = ctk.CTkImage(
            light_image=image, dark_image=image, size=image.size,
        )
        label = getattr(app, "live_preview_label", None)
        if label is None or not label.winfo_exists():
            label = ctk.CTkLabel(app.preview_frame, text="")
            label.place(relx=0.5, rely=0.5, anchor="center")
            app.live_preview_label = label
        label.configure(image=app.live_preview_image, text="")
        _update_ready_status(app)
    except Exception as error:
        label = getattr(app, "live_preview_label", None)
        if label is None or not label.winfo_exists():
            label = ctk.CTkLabel(app.preview_frame, text="")
            label.place(relx=0.5, rely=0.5, anchor="center")
            app.live_preview_label = label
        label.configure(
            image=None,
            text=f"Preview konnte nicht gerendert werden:\n{error}",
            text_color="#D86A6A", wraplength=360, justify="center",
        )
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
