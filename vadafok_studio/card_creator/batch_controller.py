"""State-changing Card Creator batch operations."""

from __future__ import annotations

from typing import Any, Callable, Iterable
from tkinter import messagebox


class CardBatchController:
    """Manage the in-memory batch through the existing application host."""

    def __init__(
        self,
        app: Any,
        list_templates: Callable[[], Iterable[str]],
    ) -> None:
        self.app = app
        self._list_templates = list_templates

    def current_item_name(self) -> str:
        output_name = getattr(self.app, "card_output_name", None)
        base = output_name.get().strip() if output_name is not None else ""
        return base or self.app.card_default_output_name()

    def add_current(self) -> None:
        try:
            self.app.card_save_values()
            self.app.card_batch_items.append({
                "template": self.app.card_selected_template.get(),
                "output_name": self.current_item_name(),
                "profile": self.app.card_export_profile.get(),
                "values": dict(self.app.card_values_plain()),
            })
            self.app.card_batch_selected_index = len(self.app.card_batch_items) - 1
            self.app.card_build_batch_panel()
            status = getattr(self.app, "card_render_status", None)
            if status is not None:
                status.configure(
                    text=f"Batch: {len(self.app.card_batch_items)} Karte(n) in der Liste.",
                    text_color="#8FE6A0",
                )
        except Exception as exc:
            messagebox.showerror("Batch Cards", f"Add Current fehlgeschlagen:\n{exc}")

    def duplicate_selected(self) -> None:
        index = self.app.card_batch_selected_index
        if index is None or not (0 <= index < len(self.app.card_batch_items)):
            messagebox.showinfo("Batch Cards", "Bitte zuerst einen Batch-Eintrag auswählen.")
            return
        original = self.app.card_batch_items[index]
        self.app.card_batch_items.insert(index + 1, {
            "template": original.get("template", ""),
            "output_name": str(original.get("output_name", "card")) + "_copy",
            "profile": original.get("profile", "Broadcast PNG"),
            "values": dict(original.get("values", {})),
        })
        self.app.card_batch_selected_index = index + 1
        self.app.card_build_batch_panel()

    def remove_selected(self) -> None:
        index = self.app.card_batch_selected_index
        if index is None or not (0 <= index < len(self.app.card_batch_items)):
            messagebox.showinfo("Batch Cards", "Bitte zuerst einen Batch-Eintrag auswählen.")
            return
        self.app.card_batch_items.pop(index)
        self.app.card_batch_selected_index = None
        self.app.card_build_batch_panel()

    def clear(self) -> None:
        if not self.app.card_batch_items:
            return
        if not messagebox.askyesno("Batch Cards", "Batch-Liste wirklich leeren?"):
            return
        self.app.card_batch_items.clear()
        self.app.card_batch_selected_index = None
        self.app.card_build_batch_panel()

    def select(self, index: int) -> None:
        if not (0 <= index < len(self.app.card_batch_items)):
            return

        self.app.card_batch_selected_index = index
        item = self.app.card_batch_items[index]
        template_name = item.get("template", "")
        if template_name in self._list_templates():
            self.app.card_selected_template.set(template_name)

        self.app.card_output_name.set(
            item.get("output_name", self.app.card_default_output_name())
        )
        self.app.card_export_profile.set(
            item.get("profile", "Broadcast PNG")
        )

        self.app.card_build_form()
        values = self.app.card_creator_values.get(
            self.app.card_selected_template.get(), {}
        )
        item_values = item.get("values", {})
        for key, variable in values.items():
            if hasattr(variable, "set"):
                variable.set(str(item_values.get(key, "")))

        self.app.card_save_values()
        self.app.card_update_preview()
        self.app.card_build_batch_panel()
