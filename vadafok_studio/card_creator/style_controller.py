"""Card Creator field-style actions."""

from __future__ import annotations

from typing import Any
from tkinter import messagebox


class CardStyleController:
    def __init__(self, app: Any, style_engine: Any, load_template, save_template) -> None:
        self.app = app
        self._style_engine = style_engine
        self._load_template = load_template
        self._save_template = save_template

    def field_index_by_name(self, field_name: str):
        for index, field in enumerate(self.app.card_template().get("fields", [])):
            if field.get("name") == field_name:
                return index
        return None

    def apply_to_field(self, field_name: str, style_name: str) -> None:
        if not style_name or style_name == "Select Style":
            return

        template_name = self.app.card_selected_template.get()
        template = self._load_template(template_name)
        fields = template.get("fields", [])
        target_index = next(
            (
                index
                for index, field in enumerate(fields)
                if field.get("name") == field_name
            ),
            None,
        )
        if target_index is None:
            messagebox.showwarning(
                "Card Creator Styles", f"Feld nicht gefunden: {field_name}"
            )
            return

        try:
            style = self._style_engine.load_style(style_name)
            if not style:
                messagebox.showwarning(
                    "Card Creator Styles",
                    "Style ist leer oder konnte nicht geladen werden.",
                )
                return

            self._style_engine.apply_style(fields[target_index], style)
            self._save_template(template_name, template)
            if getattr(self.app, "template_selected_name", None) == template_name:
                self.app.template_working_data = None
            self.app.card_update_preview()
            messagebox.showinfo(
                "Card Creator Styles",
                f"Style '{style_name}' wurde auf '{field_name}' angewendet.",
            )
        except Exception as exc:
            messagebox.showerror("Card Creator Styles", str(exc))

    def open_template_editor(self) -> None:
        self.app.template_selected_name = self.app.card_selected_template.get()
        self.app.show_template_editor_page()
