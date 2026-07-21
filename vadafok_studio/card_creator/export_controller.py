"""Card Creator export path selection and output-directory handling."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from tkinter import filedialog
from tkinter import messagebox


class CardExportController:
    def __init__(
        self,
        app: Any,
        export_engine: Any,
        default_export_dir: Path,
        open_folder,
    ) -> None:
        self.app = app
        self._export_engine = export_engine
        self._default_export_dir = Path(default_export_dir)
        self._open_folder = open_folder

    def output_directory(self, batch: bool = False) -> Path:
        variable = (
            self.app.card_batch_output_folder
            if batch
            else self.app.card_output_folder
        )
        value = variable.get().strip() if hasattr(variable, "get") else ""
        folder = Path(value).expanduser() if value else self._default_export_dir
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def output_path(self, final: bool = False, output_dir=None) -> Path:
        output_name = getattr(self.app, "card_output_name", None)
        base = output_name.get().strip() if output_name is not None else ""
        if not base:
            base = self.app.card_default_output_name()
        profile_var = getattr(self.app, "card_export_profile", None)
        profile = profile_var.get() if profile_var is not None else "Broadcast PNG"
        target_dir = (
            Path(output_dir)
            if output_dir is not None
            else self.output_directory() if final else self._default_export_dir
        )
        target_dir.mkdir(parents=True, exist_ok=True)
        return self._export_engine.export_path(
            target_dir, base, profile, final=final
        )

    def choose_final_output_path(self):
        default_path = self.output_path(final=True)
        if not self.app.card_ask_output_location.get():
            return default_path
        selected = filedialog.asksaveasfilename(
            title="Card Creator – Karte speichern",
            initialdir=str(default_path.parent),
            initialfile=default_path.name,
            defaultextension=default_path.suffix,
            filetypes=[
                ("Bilddatei", f"*{default_path.suffix}"),
                ("Alle Dateien", "*.*"),
            ],
        )
        return Path(selected) if selected else None

    def choose_batch_output_directory(self):
        default_dir = self.output_directory(batch=True)
        if not self.app.card_ask_output_location.get():
            return default_dir
        selected = filedialog.askdirectory(
            title="Card Creator – Batch-Ausgabeordner wählen",
            initialdir=str(default_dir),
        )
        return Path(selected) if selected else None

    def open_export_folder(self) -> None:
        try:
            self._open_folder(str(self.output_directory()))
        except Exception as exc:
            messagebox.showerror(
                "Card Creator",
                f"Export-Ordner konnte nicht geöffnet werden:\n{exc}",
            )

    def copy_last_path(self) -> None:
        if not self.app.card_creator_last_render:
            messagebox.showinfo(
                "Card Creator", "Noch keine finale Karte gerendert."
            )
            return
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append(str(self.app.card_creator_last_render))
            messagebox.showinfo(
                "Card Creator", "Pfad wurde in die Zwischenablage kopiert."
            )
        except Exception as exc:
            messagebox.showerror("Card Creator", str(exc))
