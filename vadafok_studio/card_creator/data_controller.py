"""Card Creator form-value history and editing actions."""

from __future__ import annotations

from typing import Any, Callable
from tkinter import messagebox

from .state import CardCreatorState


class CardDataController:
    def __init__(
        self,
        app: Any,
        state: CardCreatorState,
        persist_values: Callable[[dict], None],
    ) -> None:
        self.app = app
        self.state = state
        self._persist_values = persist_values

    def values_plain(self) -> dict[str, str]:
        values = self.app.card_creator_values.get(
            self.app.card_selected_template.get(), {}
        )
        return {
            key: variable.get() if hasattr(variable, "get") else str(variable)
            for key, variable in values.items()
        }

    def save_values(self) -> None:
        self.app.card_values_save_job = None
        template_name = self.app.card_selected_template.get()
        self.app.card_saved_values[template_name] = self.values_plain()
        self._persist_values(self.app.card_saved_values)

    def current_snapshot(self) -> dict[str, str]:
        return dict(self.values_plain())

    def apply_snapshot(self, snapshot: dict[str, str]) -> None:
        values = self.app.card_creator_values.get(
            self.app.card_selected_template.get(), {}
        )
        for key, value in snapshot.items():
            if key in values and hasattr(values[key], "set"):
                values[key].set(value)
        for key, variable in values.items():
            if key not in snapshot and hasattr(variable, "set"):
                variable.set("")
        self.save_values()
        self.app.card_update_preview()

    def push_history(self) -> None:
        snapshot = self.current_snapshot()
        if self.state.data_undo_stack and self.state.data_undo_stack[-1] == snapshot:
            return
        self.state.data_undo_stack.append(snapshot)
        if len(self.state.data_undo_stack) > self.state.history_limit:
            self.state.data_undo_stack.pop(0)
        self.state.data_redo_stack.clear()

    def clear_values(self) -> None:
        self.push_history()
        values = self.app.card_creator_values.get(
            self.app.card_selected_template.get(), {}
        )
        for variable in values.values():
            if hasattr(variable, "set"):
                variable.set("")
        self.save_values()
        self.app.card_update_preview()

    def undo(self) -> None:
        if not self.state.data_undo_stack:
            messagebox.showinfo("Card Creator", "Nichts zum Rückgängig machen.")
            return
        current = self.current_snapshot()
        previous = self.state.data_undo_stack.pop()
        self.state.data_redo_stack.append(current)
        self.apply_snapshot(previous)

    def redo(self) -> None:
        if not self.state.data_redo_stack:
            messagebox.showinfo("Card Creator", "Nichts zum Wiederherstellen.")
            return
        current = self.current_snapshot()
        next_snapshot = self.state.data_redo_stack.pop()
        self.state.data_undo_stack.append(current)
        self.apply_snapshot(next_snapshot)
