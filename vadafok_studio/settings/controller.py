"""Settings and persisted application configuration controller.

The application continues to own its Tk variables and widgets. This controller
coordinates the Settings page, project-folder selection, and the existing
configuration persistence without changing runtime behavior.
"""

from __future__ import annotations

import os
from pathlib import Path
from tkinter import filedialog, messagebox

from ..core.config import save_config as persist_config


class SettingsController:
    """Coordinate Settings UI actions for one application instance."""

    def __init__(self, app):
        self.app = app

    def show_settings_page(self):
        """Build and display the existing Settings page."""
        from .page import show_settings_page

        return show_settings_page(self.app)

    def browse_project_folder(self):
        """Select the project folder and persist it immediately."""
        app = self.app
        folder = filedialog.askdirectory(title="VADAFOK Projektordner wählen")
        if folder:
            app.project_folder.set(folder)
            self.save_config()

    def _browse_output_folder(self, variable, title):
        current = variable.get().strip()
        folder = filedialog.askdirectory(title=title, initialdir=current or None)
        if folder:
            variable.set(folder)
            self.save_config()

    def browse_card_output_folder(self):
        self._browse_output_folder(self.app.card_output_folder, "Card Creator – Ausgabeordner wählen")

    def browse_card_batch_output_folder(self):
        self._browse_output_folder(self.app.card_batch_output_folder, "Card Creator – Batch-Ausgabeordner wählen")

    def _open_output_folder(self, variable, label):
        try:
            value = variable.get().strip()
            folder = Path(value).expanduser() if value else Path.cwd() / "exports"
            folder.mkdir(parents=True, exist_ok=True)
            os.startfile(str(folder))
        except Exception as exc:
            messagebox.showerror("Settings", f"{label} konnte nicht geöffnet werden:\n{exc}")

    def open_card_output_folder(self):
        self._open_output_folder(self.app.card_output_folder, "Ausgabeordner")

    def open_card_batch_output_folder(self):
        self._open_output_folder(self.app.card_batch_output_folder, "Batch-Ausgabeordner")

    def save_config(self):
        """Persist the current application settings exactly as before."""
        app = self.app
        app.config_data.update({
            "host": app.host.get(),
            "port": app.port.get(),
            "password": app.password.get(),
            "scene_name": app.scene_name.get(),
            "caption_group": app.caption_group.get(),
            "caption_text": app.caption_text.get(),
            "caption_banner_source": app.caption_banner_source.get(),
            "caption_render_source": app.caption_render_source.get(),
            "scene_card_source": app.scene_card_source.get(),
            "duration": app.duration.get(),
            "project_folder": app.project_folder.get(),
            "card_output_folder": app.card_output_folder.get().strip(),
            "card_batch_output_folder": app.card_batch_output_folder.get().strip(),
            "card_ask_output_location": bool(app.card_ask_output_location.get()),
            "caption_engine": app.caption_engine.get(),
            "caption_font_family": app.caption_font_family.get(),
            "caption_font_size": int(app.caption_font_size.get()),
            "caption_text_color": app.caption_text_color.get(),
            "caption_stroke_color": app.caption_stroke_color.get(),
            "caption_stroke_width": int(app.caption_stroke_width.get()),
            "caption_render_width": int(app.caption_render_width.get()),
            "caption_render_height": int(app.caption_render_height.get()),
            "caption_uppercase": bool(app.caption_uppercase.get()),
            "caption_safe_left": int(app.caption_safe_left.get()),
            "caption_safe_right": int(app.caption_safe_right.get()),
            "caption_safe_top": int(app.caption_safe_top.get()),
            "caption_safe_bottom": int(app.caption_safe_bottom.get()),
            "voice_enabled": bool(app.voice_enabled.get()),
            "voice_trigger_phrase": (
                app.voice_trigger_phrase.get().strip() or "live card"
            ),
            "voice_culture": app.voice_culture.get().strip() or "de-DE",
            "stream_effect_source": (
                app.stream_effect_source.get().strip()
                or "VADAFOK Stream Effect"
            ),
        })
        persist_config(app.config_data)
