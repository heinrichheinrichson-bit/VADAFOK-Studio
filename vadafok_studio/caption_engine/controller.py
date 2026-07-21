"""Controller for the Caption Engine settings workspace."""

from __future__ import annotations

from tkinter import TclError, colorchooser, messagebox


DEFAULT_COLOR_FAVORITES = ["#FFFFFF", "#000000", "#E0AA36", "#D94A36"]

CAPTION_PRESETS = {
    "Standard": {
        "font_size": 160, "stroke_width": 3, "render_width": 1600,
        "render_height": 260, "safe_left": 12, "safe_right": 12,
        "safe_top": 24, "safe_bottom": 24,
    },
    "Untertitel": {
        "font_size": 96, "stroke_width": 4, "render_width": 1600,
        "render_height": 220, "safe_left": 8, "safe_right": 8,
        "safe_top": 18, "safe_bottom": 18,
    },
    "Breites Banner": {
        "font_size": 140, "stroke_width": 3, "render_width": 1920,
        "render_height": 300, "safe_left": 10, "safe_right": 10,
        "safe_top": 20, "safe_bottom": 20,
    },
}


class CaptionEngineController:
    def __init__(self, app):
        self.app = app
        self._snapshot = None
        self._preview_job = None
        self.dirty = False

    def show_page(self):
        from .page import show_caption_engine_page

        self._snapshot = self.values()
        self.dirty = False
        return show_caption_engine_page(self.app, self)

    def values(self):
        app = self.app
        return {
            "engine": app.caption_engine.get(),
            "font_family": app.caption_font_family.get(),
            "font_size": app.caption_font_size.get(),
            "text_color": app.caption_text_color.get(),
            "stroke_color": app.caption_stroke_color.get(),
            "stroke_width": app.caption_stroke_width.get(),
            "render_width": app.caption_render_width.get(),
            "render_height": app.caption_render_height.get(),
            "uppercase": bool(app.caption_uppercase.get()),
            "safe_left": app.caption_safe_left.get(),
            "safe_right": app.caption_safe_right.get(),
            "safe_top": app.caption_safe_top.get(),
            "safe_bottom": app.caption_safe_bottom.get(),
        }

    def color_favorites(self):
        raw = self.app.config_data.get("caption_color_favorites", [])
        result = []
        for index in range(4):
            color = raw[index] if index < len(raw) else DEFAULT_COLOR_FAVORITES[index]
            result.append(self.normalize_color(color) or DEFAULT_COLOR_FAVORITES[index])
        self.app.config_data["caption_color_favorites"] = result
        return result

    @staticmethod
    def normalize_color(value):
        value = str(value or "").strip().upper()
        if not value.startswith("#"):
            value = f"#{value}"
        if len(value) != 7:
            return None
        try:
            int(value[1:], 16)
        except ValueError:
            return None
        return value

    def choose_color(self, variable):
        initial = self.normalize_color(variable.get()) or "#FFFFFF"
        _rgb, selected = colorchooser.askcolor(color=initial, title="Farbe auswählen")
        if selected:
            variable.set(selected.upper())
            self.mark_changed()

    def use_favorite_color(self, variable, color):
        variable.set(color)
        self.mark_changed()

    def store_favorite_color(self, index, variable):
        color = self.normalize_color(variable.get())
        if color is None:
            messagebox.showwarning("Caption Engine", "Bitte zuerst einen gültigen Hex-Farbwert eingeben.")
            return False
        favorites = self.color_favorites()
        favorites[index] = color
        self.app.config_data["caption_color_favorites"] = favorites
        self.refresh_color_favorites()
        self.mark_changed()
        return True

    def refresh_color_favorites(self):
        favorites = self.color_favorites()
        for button in getattr(self.app, "caption_color_favorite_buttons", []):
            index = button._caption_color_slot
            color = favorites[index]
            variable = button._caption_color_variable
            button.configure(
                fg_color=color, hover_color=color, text=str(index + 1),
                command=lambda var=variable, slot=index: self.use_favorite_color(
                    var, self.color_favorites()[slot],
                ),
            )

    def apply_preset(self, name):
        preset = CAPTION_PRESETS.get(name)
        if not preset:
            return
        app = self.app
        for key, value in preset.items():
            getattr(app, f"caption_{key}").set(value)
        self.mark_changed()

    def validate(self, show_message=True):
        app = self.app
        errors = []
        text_color = self.normalize_color(app.caption_text_color.get())
        stroke_color = self.normalize_color(app.caption_stroke_color.get())
        if text_color is None:
            errors.append("Textfarbe muss ein Hex-Wert wie #FFFFFF sein.")
        if stroke_color is None:
            errors.append("Konturfarbe muss ein Hex-Wert wie #000000 sein.")
        try:
            numbers = {
                "Schriftgröße": (int(app.caption_font_size.get()), 8, 500),
                "Konturstärke": (int(app.caption_stroke_width.get()), 0, 30),
                "Render-Breite": (int(app.caption_render_width.get()), 320, 7680),
                "Render-Höhe": (int(app.caption_render_height.get()), 80, 2160),
                "Sicherheitsabstand links": (int(app.caption_safe_left.get()), 0, 45),
                "Sicherheitsabstand rechts": (int(app.caption_safe_right.get()), 0, 45),
                "Sicherheitsabstand oben": (int(app.caption_safe_top.get()), 0, 45),
                "Sicherheitsabstand unten": (int(app.caption_safe_bottom.get()), 0, 45),
            }
            for label, (value, minimum, maximum) in numbers.items():
                if not minimum <= value <= maximum:
                    errors.append(f"{label}: erlaubt sind {minimum} bis {maximum}.")
        except (TypeError, ValueError, TclError):
            errors.append("Alle Größen und Abstände müssen ganze Zahlen sein.")
        if not str(app.caption_font_family.get()).strip():
            errors.append("Bitte eine Schriftfamilie eintragen.")
        if errors and show_message:
            messagebox.showwarning("Caption Engine – Eingaben prüfen", "\n".join(errors))
        if not errors:
            app.caption_text_color.set(text_color)
            app.caption_stroke_color.set(stroke_color)
        return not errors

    def save(self):
        if not self.validate():
            return False
        self.app.save_config()
        self._snapshot = self.values()
        self.dirty = False
        self._set_status("✓ Einstellungen gespeichert", "#8FE6A0")
        return True

    def reset_changes(self):
        if not self._snapshot:
            return
        app = self.app
        for key, value in self._snapshot.items():
            getattr(app, f"caption_{key}").set(value)
        self.dirty = False
        self._set_status("Änderungen zurückgesetzt", "#BCA870")
        self.schedule_preview()

    def mark_changed(self, *_args):
        self.dirty = True
        self._set_status("● Nicht gespeicherte Änderungen", "#E0B86A")
        self.schedule_preview()

    def confirm_close(self):
        """Offer save/discard/cancel when the application closes with edits."""
        if not self.dirty:
            return True
        answer = messagebox.askyesnocancel(
            "Caption Engine",
            "Die Caption-Engine-Einstellungen wurden noch nicht gespeichert.\n\nJetzt speichern?",
        )
        if answer is None:
            return False
        if answer:
            return self.save()
        return True

    def schedule_preview(self, *_args):
        if self._preview_job is not None:
            try:
                self.app.after_cancel(self._preview_job)
            except Exception:
                pass
        self._preview_job = self.app.after(220, self.update_preview)

    def update_preview(self):
        self._preview_job = None
        if not self.validate(show_message=False):
            self._set_preview_error("Vorschau wartet auf gültige Eingaben")
            return
        try:
            from PIL import Image
            import customtkinter as ctk
            from ..core.caption_renderer import render_caption_png
            from ..core.config import EXPORT_DIR

            text = self.app.caption_preview_text.get().strip() or "DEINE CAPTION"
            app = self.app
            path = EXPORT_DIR / "caption_engine_preview.png"
            render_caption_png(
                text=text,
                output_path=path,
                width=int(app.caption_render_width.get()),
                height=int(app.caption_render_height.get()),
                font_family=app.caption_font_family.get(),
                font_size=int(app.caption_font_size.get()),
                text_color=app.caption_text_color.get(),
                stroke_color=app.caption_stroke_color.get(),
                stroke_width=int(app.caption_stroke_width.get()),
                uppercase=bool(app.caption_uppercase.get()),
                banner_path=app.config_data.get("selected_banner_path", ""),
                safe_left=int(app.caption_safe_left.get()),
                safe_right=int(app.caption_safe_right.get()),
                safe_top=int(app.caption_safe_top.get()),
                safe_bottom=int(app.caption_safe_bottom.get()),
                png_compress_level=app.config_data.get("caption_png_compress_level", 1),
            )
            with Image.open(path) as source:
                image = source.convert("RGBA")
            image.thumbnail((760, 350))
            self.app.caption_engine_preview_image = ctk.CTkImage(
                light_image=image, dark_image=image, size=image.size,
            )
            self.app.caption_engine_preview_label.configure(
                image=self.app.caption_engine_preview_image, text="",
            )
        except Exception as error:
            self._set_preview_error(f"Vorschau nicht verfügbar:\n{error}")

    def _set_preview_error(self, text):
        label = getattr(self.app, "caption_engine_preview_label", None)
        if label is not None:
            label.configure(image=None, text=text, text_color="#D86A6A")

    def _set_status(self, text, color):
        label = getattr(self.app, "caption_engine_status_label", None)
        if label is not None:
            label.configure(text=text, text_color=color)
