"""Quick Card library actions and transient editing state."""

from __future__ import annotations

from typing import Any
from tkinter import messagebox, simpledialog

from ..core import text_library_engine
from .tree_view import set_category_collapsed


class QuickCardsController:
    def __init__(self, app: Any) -> None:
        self.app = app

    def categories(self) -> list[str]:
        try:
            categories = sorted(text_library_engine.load_library())
            return categories or ["Chat"]
        except Exception:
            return ["Chat"]

    def refresh_tree(self) -> None:
        if hasattr(self.app, "quick_cards_tree"):
            self.app.quick_cards_build_tree()
        else:
            self.app.show_quick_cards()

    def refresh_category_menu(self) -> None:
        categories = sorted(self.app.text_library_data) or ["Chat"]
        target = self.app.quick_cards_target_category.get()
        if target not in categories:
            self.app.quick_cards_target_category.set(categories[0])
        menu = getattr(self.app, "quick_cards_category_menu", None)
        if menu is not None:
            menu.configure(values=categories)

    def toggle_category(self, category: str) -> None:
        if category in self.app.quick_cards_collapsed:
            self.app.quick_cards_collapsed.remove(category)
        else:
            self.app.quick_cards_collapsed.add(category)
        if not set_category_collapsed(
            self.app, category, category in self.app.quick_cards_collapsed,
        ):
            self.refresh_tree()

    def use_text(self, text: str) -> None:
        self.app.live_card_pending_text = str(text or "").strip()
        self.app.show_live_card()
        self.app.after(80, self.app.live_card_apply_pending_text)
        self.app.after(120, self.app.update_render_preview)

    def add_category(self) -> None:
        category = self.app.text_library_new_category.get().strip()
        if not category:
            messagebox.showinfo("Quick Cards", "Please enter a category name.")
            return
        self.app.text_library_data = text_library_engine.add_category(category)
        self.app.text_library_new_category.set("")
        self.app.quick_cards_target_category.set(category)
        self.app.quick_cards_collapsed.discard(category)
        self.refresh_category_menu()
        self.refresh_tree()

    def rename_category(self, category: str) -> None:
        new_name = simpledialog.askstring(
            "Quick Cards", "New category name:", initialvalue=category,
        )
        new_name = str(new_name or "").strip()
        if not new_name:
            return
        self.app.text_library_data = text_library_engine.rename_category(
            category, new_name,
        )
        if category in self.app.quick_cards_collapsed:
            self.app.quick_cards_collapsed.remove(category)
            self.app.quick_cards_collapsed.add(new_name)
        self.app.quick_cards_target_category.set(new_name)
        self.refresh_category_menu()
        self.refresh_tree()

    def delete_category(self, category: str) -> None:
        if not messagebox.askyesno(
            "Quick Cards",
            f"Delete category '{category}'?\nAll texts inside will be removed.",
        ):
            return
        self.app.text_library_data = text_library_engine.delete_category(category)
        self.app.quick_cards_collapsed.discard(category)
        self.refresh_category_menu()
        self.refresh_tree()

    def add_text(self) -> None:
        text = self.app.text_library_new_text.get().strip()
        if not text:
            messagebox.showinfo("Quick Cards", "Please enter a text first.")
            return
        category = self.app.quick_cards_target_category.get()
        self.app.text_library_data = text_library_engine.add_text(category, text)
        self.app.text_library_new_text.set("")
        self.app.live_card_pending_text = text
        self.refresh_tree()

    def save_live_text(self) -> None:
        text = self.app.live_card_get_message_text()
        if not text:
            messagebox.showinfo("Quick Cards", "No Live Card text found.")
            return
        categories = self.categories()
        if self.app.quick_cards_target_category.get() not in categories:
            target = "Chat" if "Chat" in categories else categories[0]
            self.app.quick_cards_target_category.set(target)
        category = self.app.quick_cards_target_category.get()
        self.app.text_library_data = text_library_engine.add_text(category, text)
        messagebox.showinfo("Quick Cards", f"Text saved.\nCategory: {category}")
        self.refresh_tree()

    def start_text_edit(self, category: str, text: str) -> None:
        self.app.quick_cards_editing_category = category
        self.app.quick_cards_editing_text = text
        self.app.quick_cards_edit_text_var.set(text)
        self.refresh_tree()

    def commit_text_edit(self, category: str, text: str) -> None:
        new_text = self.app.quick_cards_edit_text_var.get().strip()
        if not new_text:
            messagebox.showinfo("Quick Cards", "Text cannot be empty.")
            return
        self.app.text_library_data = text_library_engine.edit_text(
            category, text, new_text,
        )
        self._clear_editing()
        self.refresh_tree()

    def cancel_text_edit(self) -> None:
        self._clear_editing()
        self.refresh_tree()

    def delete_text(self, category: str, text: str) -> None:
        if not messagebox.askyesno("Quick Cards", "Delete this text?"):
            return
        self.app.text_library_data = text_library_engine.delete_text(category, text)
        self.refresh_tree()

    def _clear_editing(self) -> None:
        self.app.quick_cards_editing_category = None
        self.app.quick_cards_editing_text = None
        self.app.quick_cards_edit_text_var.set("")
