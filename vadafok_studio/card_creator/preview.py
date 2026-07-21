"""Card Creator preview coordination."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import customtkinter as ctk
from PIL import Image

from .state import CardCreatorState


def preview_bounds(frame: Any) -> tuple[int, int]:
    """Return safe, capped image bounds for the currently visible preview."""
    try:
        width = int(frame.winfo_width()) - 28
        height = int(frame.winfo_height()) - 28
    except (TypeError, ValueError):
        return 760, 620
    if width < 120 or height < 120:
        return 760, 620
    return min(width, 1200), min(height, 960)


class CardPreviewController:
    def __init__(
        self,
        app: Any,
        export_engine: Any,
        render_image,
        state: CardCreatorState | None = None,
    ) -> None:
        self.app = app
        self.state = state or app.card_creator_state
        self._export_engine = export_engine
        self._render_image = render_image

    def changed(self, *_args) -> None:
        """Debounce persistence and live-preview work after value changes."""
        if self.app.card_values_save_job is not None:
            try:
                self.app.after_cancel(self.app.card_values_save_job)
            except Exception:
                pass
        self.app.card_values_save_job = self.app.after(
            350, self.app.card_save_values
        )

        auto_preview = getattr(self.app, "card_auto_preview", None)
        if auto_preview is not None and not auto_preview.get():
            return

        if self.app.card_preview_update_job is not None:
            try:
                self.app.after_cancel(self.app.card_preview_update_job)
            except Exception:
                pass
        self.app.card_preview_update_job = self.app.after(
            25, self.app.card_update_preview
        )

    def update(self) -> None:
        """Refresh the on-screen preview entirely in memory."""
        self.app.card_preview_update_job = None
        if not hasattr(self.app, "card_preview_frame"):
            return
        try:
            background_path = self.app.card_background_path()
            if not background_path:
                raise FileNotFoundError(
                    "Kein Background gefunden für Template: "
                    f"{self.app.card_selected_template.get()}"
                )

            background_file = Path(background_path)
            cache_key = (
                str(background_file),
                background_file.stat().st_mtime_ns,
            )
            if (
                self.state.preview_background_key != cache_key
                or self.state.preview_background_cache is None
            ):
                with Image.open(background_file) as source:
                    self.state.preview_background_cache = source.convert("RGBA")
                self.state.preview_background_key = cache_key

            image = self._render_image(
                self.app.card_template(),
                self.app.card_values_plain(),
                background_image=self.state.preview_background_cache,
            )
            original_size = image.size
            profile_name = self.app.card_export_profile.get()
            image = self._export_engine.apply_export_profile(
                image, profile_name
            )
            self.state.preview_source_image = image.copy()

            if hasattr(self.app, "card_preview_info"):
                self.app.card_preview_info.configure(
                    text=f"{self.app.card_selected_template.get()} | "
                    f"{original_size[0]}×{original_size[1]} | {profile_name}"
                )

            if hasattr(self.app, "card_export_profile_info"):
                profile = self._export_engine.get_export_profile(profile_name)
                size = profile.get("size")
                size_text = (
                    "Originalgröße" if not size else f"{size[0]}×{size[1]}"
                )
                self.app.card_export_profile_info.configure(
                    text=f"{profile.get('format', 'PNG')} | {size_text}"
                )

            self._display_preview()
        except Exception as exc:
            self.state.preview_source_image = None
            label = self.app.card_creator_preview_label
            if label is None or not label.winfo_exists():
                label = ctk.CTkLabel(self.app.card_preview_frame, text="")
                label.place(relx=0.5, rely=0.5, anchor="center")
                self.app.card_creator_preview_label = label
            label.configure(
                image=None,
                text=f"Preview Fehler:\n{exc}",
                text_color="#D86A6A",
                wraplength=420,
                justify="center",
            )

    def zoom_by(self, amount: float) -> None:
        """Change only the on-screen scale; never the rendered export."""
        self.state.preview_zoom = max(
            0.5, min(2.5, round(self.state.preview_zoom + amount, 2))
        )
        self._display_preview()

    def fit(self) -> None:
        self.state.preview_zoom = 1.0
        self.state.preview_pan_x = 0
        self.state.preview_pan_y = 0
        self._display_preview()

    def _display_preview(self) -> None:
        source = self.state.preview_source_image
        if source is None or not hasattr(self.app, "card_preview_frame"):
            return

        fitted = source.copy()
        fitted.thumbnail(preview_bounds(self.app.card_preview_frame), Image.LANCZOS)
        zoom = self.state.preview_zoom
        display_size = (
            max(1, round(fitted.width * zoom)),
            max(1, round(fitted.height * zoom)),
        )
        image = fitted if display_size == fitted.size else fitted.resize(
            display_size, Image.LANCZOS
        )
        self.state.preview_display_size = display_size
        self._clamp_pan()

        self.app.card_creator_preview_image = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size,
        )
        label = self.app.card_creator_preview_label
        if label is None or not label.winfo_exists():
            label = ctk.CTkLabel(
                self.app.card_preview_frame,
                image=self.app.card_creator_preview_image,
                text="",
            )
            label.bind("<ButtonPress-1>", self._start_pan, add="+")
            label.bind("<B1-Motion>", self._drag_pan, add="+")
            label.bind("<MouseWheel>", self._mousewheel_zoom, add="+")
            label.bind("<Double-Button-1>", lambda _event: self.fit(), add="+")
            self.app.card_creator_preview_label = label
        else:
            label.configure(
                image=self.app.card_creator_preview_image,
                text="",
                text_color="#F2E2B6",
            )
        label.place(
            relx=0.5,
            rely=0.5,
            x=self.state.preview_pan_x,
            y=self.state.preview_pan_y,
            anchor="center",
        )
        zoom_label = getattr(self.app, "card_preview_zoom_label", None)
        if zoom_label is not None:
            zoom_label.configure(text=f"{round(zoom * 100)}%")

    def _start_pan(self, event) -> None:
        self.state.preview_drag_origin = (
            event.x_root,
            event.y_root,
            self.state.preview_pan_x,
            self.state.preview_pan_y,
        )

    def _drag_pan(self, event) -> None:
        origin = self.state.preview_drag_origin
        if origin is None:
            return
        self.state.preview_pan_x = origin[2] + event.x_root - origin[0]
        self.state.preview_pan_y = origin[3] + event.y_root - origin[1]
        self._clamp_pan()
        self.app.card_creator_preview_label.place_configure(
            x=self.state.preview_pan_x,
            y=self.state.preview_pan_y,
        )

    def _mousewheel_zoom(self, event) -> str:
        self.zoom_by(0.1 if event.delta > 0 else -0.1)
        return "break"

    def _clamp_pan(self) -> None:
        frame_width, frame_height = preview_bounds(self.app.card_preview_frame)
        image_width, image_height = self.state.preview_display_size
        limit_x = max(0, (image_width - frame_width) // 2)
        limit_y = max(0, (image_height - frame_height) // 2)
        self.state.preview_pan_x = max(-limit_x, min(limit_x, self.state.preview_pan_x))
        self.state.preview_pan_y = max(-limit_y, min(limit_y, self.state.preview_pan_y))
