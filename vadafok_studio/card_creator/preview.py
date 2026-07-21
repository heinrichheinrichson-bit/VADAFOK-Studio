"""Card Creator preview coordination."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import customtkinter as ctk
from PIL import Image

from .state import CardCreatorState


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
            image.thumbnail((760, 620), Image.LANCZOS)

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
                label.place(relx=0.5, rely=0.5, anchor="center")
                self.app.card_creator_preview_label = label
            else:
                label.configure(
                    image=self.app.card_creator_preview_image,
                    text="",
                    text_color="#F2E2B6",
                )
        except Exception as exc:
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
