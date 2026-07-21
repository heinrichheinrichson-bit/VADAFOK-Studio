"""State-changing Card Creator batch operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterable
from tkinter import filedialog, messagebox

from .state import CardCreatorState


class CardBatchController:
    """Manage the in-memory batch through the existing application host."""

    def __init__(
        self,
        app: Any,
        state: CardCreatorState,
        list_templates: Callable[[], Iterable[str]],
        batch_engine: Any,
    ) -> None:
        self.app = app
        self.state = state
        self._list_templates = list_templates
        self._batch_engine = batch_engine

    def current_item_name(self) -> str:
        output_name = getattr(self.app, "card_output_name", None)
        base = output_name.get().strip() if output_name is not None else ""
        return base or self.app.card_default_output_name()

    def add_current(self) -> None:
        try:
            self.app.card_save_values()
            self.state.batch_items.append({
                "template": self.app.card_selected_template.get(),
                "output_name": self.current_item_name(),
                "profile": self.app.card_export_profile.get(),
                "values": dict(self.app.card_values_plain()),
            })
            self.state.batch_selected_index = len(self.state.batch_items) - 1
            self.app.card_build_batch_panel()
            status = getattr(self.app, "card_render_status", None)
            if status is not None:
                status.configure(
                    text=f"Batch: {len(self.state.batch_items)} Karte(n) in der Liste.",
                    text_color="#8FE6A0",
                )
        except Exception as exc:
            messagebox.showerror("Batch Cards", f"Add Current fehlgeschlagen:\n{exc}")

    def duplicate_selected(self) -> None:
        index = self.state.batch_selected_index
        if index is None or not (0 <= index < len(self.state.batch_items)):
            messagebox.showinfo("Batch Cards", "Bitte zuerst einen Batch-Eintrag auswählen.")
            return
        original = self.state.batch_items[index]
        self.state.batch_items.insert(index + 1, {
            "template": original.get("template", ""),
            "output_name": str(original.get("output_name", "card")) + "_copy",
            "profile": original.get("profile", "Broadcast PNG"),
            "values": dict(original.get("values", {})),
        })
        self.state.batch_selected_index = index + 1
        self.app.card_build_batch_panel()

    def remove_selected(self) -> None:
        index = self.state.batch_selected_index
        if index is None or not (0 <= index < len(self.state.batch_items)):
            messagebox.showinfo("Batch Cards", "Bitte zuerst einen Batch-Eintrag auswählen.")
            return
        self.state.batch_items.pop(index)
        self.state.batch_selected_index = None
        self.app.card_build_batch_panel()

    def clear(self) -> None:
        if not self.state.batch_items:
            return
        if not messagebox.askyesno("Batch Cards", "Batch-Liste wirklich leeren?"):
            return
        self.state.batch_items.clear()
        self.state.batch_selected_index = None
        self.app.card_build_batch_panel()

    def select(self, index: int) -> None:
        if not (0 <= index < len(self.state.batch_items)):
            return

        self.state.batch_selected_index = index
        item = self.state.batch_items[index]
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

    def save_project(self) -> None:
        try:
            if not self.state.batch_items:
                messagebox.showinfo("Batch Project", "Die Batch-Liste ist leer.")
                return

            path = filedialog.asksaveasfilename(
                title="Batch Project speichern",
                initialdir=str(self._batch_engine.batch_projects_dir()),
                initialfile="new_batch_project.vbatch",
                defaultextension=".vbatch",
                filetypes=[
                    ("VADAFOK Batch Project", "*.vbatch"),
                    ("JSON", "*.json"),
                    ("Alle Dateien", "*.*"),
                ],
            )
            if not path:
                self._set_status("SAVE PROJECT abgebrochen.", "#BCA870")
                return

            saved_path = self._batch_engine.save_batch_project_file(
                path, self.state.batch_items
            )
            self._set_status("Batch Project gespeichert.", "#8FE6A0")
            messagebox.showinfo(
                "Batch Project", f"Batch Project gespeichert:\n{saved_path}"
            )
        except Exception as exc:
            messagebox.showerror(
                "Batch Project", f"SAVE PROJECT Fehler:\n{exc}"
            )

    def load_project(self) -> None:
        try:
            path = filedialog.askopenfilename(
                title="Batch Project laden",
                initialdir=str(self._batch_engine.batch_projects_dir()),
                filetypes=[
                    ("VADAFOK Batch Project", "*.vbatch"),
                    ("JSON", "*.json"),
                    ("Alle Dateien", "*.*"),
                ],
            )
            if not path:
                self._set_status("LOAD PROJECT abgebrochen.", "#BCA870")
                return

            items = self._batch_engine.load_batch_project_file(path)
            self.state.batch_items = items
            self.state.batch_selected_index = 0 if items else None
            self.app.card_build_batch_panel()
            if items:
                self.select(0)
            else:
                self.app.card_update_preview()

            self._set_status(
                f"Batch Project geladen: {len(items)} Karte(n)", "#8FE6A0"
            )
            messagebox.showinfo(
                "Batch Project",
                f"Batch Project geladen:\n{len(items)} Karte(n)",
            )
        except Exception as exc:
            messagebox.showerror(
                "Batch Project", f"LOAD PROJECT Fehler:\n{exc}"
            )

    def import_file(self) -> None:
        selected_path = filedialog.askopenfilename(
            title="CSV oder Excel-Datei importieren",
            filetypes=[
                ("CSV / Excel", "*.csv *.xlsx"),
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if not selected_path:
            return

        try:
            import_path = Path(selected_path)
            rows = self._batch_engine.read_table(import_path)
            if not rows:
                messagebox.showinfo(
                    "Batch Import", "Die Datei enthält keine Datensätze."
                )
                return

            fields = self.app.card_template().get("fields", [])
            items = self._batch_engine.rows_to_batch_items(
                rows,
                self.app.card_selected_template.get(),
                fields,
                self.current_item_name(),
                self.app.card_export_profile.get(),
            )
            matched = [item for item in items if item.get("values")]
            if not matched:
                field_names = ", ".join(
                    field.get("name", "")
                    for field in fields
                    if field.get("name")
                )
                messagebox.showwarning(
                    "Batch Import",
                    "Keine passenden Spalten gefunden.\n\n"
                    f"Datei: {import_path.name}\n"
                    f"Template-Felder: {field_names}\n\n"
                    "Tipp: Die Spaltennamen müssen zu den Feldnamen im "
                    "Template passen, z.B. date, game, time, feature.",
                )
                return

            self.state.batch_items.extend(matched)
            self.state.batch_selected_index = (
                len(self.state.batch_items) - len(matched)
            )
            self.app.card_build_batch_panel()
            self._set_status(
                f"Batch Import: {len(matched)} Karte(n) hinzugefügt.",
                "#8FE6A0",
            )
            messagebox.showinfo(
                "Batch Import",
                f"{len(matched)} Batch-Karte(n) importiert.\n\n"
                f"Datei:\n{import_path}",
            )
        except Exception as exc:
            messagebox.showerror(
                "Batch Import", f"Import fehlgeschlagen:\n{exc}"
            )

    def render(self) -> None:
        if not self.state.batch_items:
            messagebox.showinfo("Batch Cards", "Batch-Liste ist leer.")
            return

        output_directory = self.app.card_choose_batch_output_directory()
        if output_directory is None:
            return

        rendered = []
        old_template = self.app.card_selected_template.get()
        old_output = self.app.card_output_name.get()
        old_profile = self.app.card_export_profile.get()
        old_values = self.app.card_values_plain()

        try:
            for item in self.state.batch_items:
                template_name = item.get("template", "")
                if template_name not in self._list_templates():
                    continue

                self.app.card_selected_template.set(template_name)
                self.app.card_output_name.set(
                    item.get("output_name", self.app.card_default_output_name())
                )
                self.app.card_export_profile.set(
                    item.get("profile", "Broadcast PNG")
                )
                self.app.card_creator_values.setdefault(template_name, {})
                self.app.card_build_form()
                values = self.app.card_creator_values.get(template_name, {})
                item_values = item.get("values", {})
                for key, variable in values.items():
                    if hasattr(variable, "set"):
                        variable.set(str(item_values.get(key, "")))

                output = self.app.card_render_to_file(
                    final=True, output_dir=output_directory
                )
                rendered.append(str(output))

            self._set_status(
                f"Batch gerendert: {len(rendered)} Datei(en)", "#8FE6A0"
            )
            messagebox.showinfo(
                "Batch Cards",
                f"Batch gerendert:\n{len(rendered)} Datei(en)",
            )
        except Exception as exc:
            messagebox.showerror("Batch Cards", str(exc))
        finally:
            if old_template in self._list_templates():
                self.app.card_selected_template.set(old_template)
            self.app.card_output_name.set(old_output)
            self.app.card_export_profile.set(old_profile)
            self.app.card_build_form()
            values = self.app.card_creator_values.get(
                self.app.card_selected_template.get(), {}
            )
            for key, variable in values.items():
                if hasattr(variable, "set"):
                    variable.set(str(old_values.get(key, "")))
            self.app.card_save_values()
            self.app.card_update_preview()
            self.app.card_build_batch_panel()

    def _set_status(self, text: str, color: str) -> None:
        status = getattr(self.app, "card_render_status", None)
        if status is not None:
            status.configure(text=text, text_color=color)
