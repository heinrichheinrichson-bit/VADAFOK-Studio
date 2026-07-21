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

            previous_style = self._style_engine.extract_style(fields[target_index])
            self._style_engine.apply_style(fields[target_index], style)
            self._save_template(template_name, template)
            self.app.card_creator_state.style_undo_stack.append({
                "template": template_name,
                "field": field_name,
                "style": previous_style,
            })
            if getattr(self.app, "template_selected_name", None) == template_name:
                self.app.template_working_data = None
            style_variables = getattr(self.app, "card_style_variables", {})
            if field_name in style_variables:
                style_variables[field_name].set("Select Style")
            self.app.card_update_preview()
            messagebox.showinfo(
                "Card Creator Styles",
                f"Style '{style_name}' wurde auf '{field_name}' angewendet.",
            )
        except Exception as exc:
            messagebox.showerror("Card Creator Styles", str(exc))

    def undo_field_style(self, field_name: str) -> None:
        template_name = self.app.card_selected_template.get()
        stack = self.app.card_creator_state.style_undo_stack
        history_index = next(
            (
                index for index in range(len(stack) - 1, -1, -1)
                if stack[index].get("template") == template_name
                and stack[index].get("field") == field_name
            ),
            None,
        )
        if history_index is None:
            messagebox.showinfo(
                "Card Creator Styles",
                f"Für '{field_name}' gibt es noch keine Stiländerung zum Rückgängigmachen.",
            )
            return

        entry = stack[history_index]
        template = self._load_template(template_name)
        target = next(
            (field for field in template.get("fields", []) if field.get("name") == field_name),
            None,
        )
        if target is None:
            messagebox.showwarning(
                "Card Creator Styles", f"Feld nicht gefunden: {field_name}"
            )
            return

        try:
            self._style_engine.restore_style(target, entry.get("style", {}))
            self._save_template(template_name, template)
            stack.pop(history_index)
            if getattr(self.app, "template_selected_name", None) == template_name:
                self.app.template_working_data = None
            self.app.card_update_preview()
        except Exception as exc:
            messagebox.showerror("Card Creator Styles", str(exc))

    def open_template_editor(self) -> None:
        self.app.template_selected_name = self.app.card_selected_template.get()
        self.app.show_template_editor_page()
