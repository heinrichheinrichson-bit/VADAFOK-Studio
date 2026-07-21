"""Sound favorites editor window.

This module owns the compact editor UI while the main application keeps the
sound-selection and persistence workflows it coordinates.
"""

from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

from ..core.config import save_config
from ..core.window_icon import apply_window_icon
from ..services.sound_effect_selection import portable_effect_path

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
TEXT = "#F2E2B6"


def open_sound_favorites_editor_window(app):
    """Open the four-slot sound favorites editor for *app*."""
    favorites = [dict(item) for item in app._ensure_sound_favorites()]
    dialog = ctk.CTkToplevel(app)
    apply_window_icon(dialog, app)
    dialog.title("Sound-Favoriten bearbeiten")
    dialog.geometry("680x430")
    dialog.minsize(620, 390)
    dialog.transient(app)
    dialog.grab_set()
    dialog.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        dialog,
        text="4 Sound-Favoriten",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=TEXT,
    ).grid(row=0, column=0, padx=20, pady=(18, 4), sticky="w")
    ctk.CTkLabel(
        dialog,
        text="Die Dateien müssen im Sounds-Ordner des aktuellen Projekts liegen.",
        text_color="#BCA870",
    ).grid(row=1, column=0, padx=20, pady=(0, 12), sticky="w")

    rows = []
    for index, favorite in enumerate(favorites):
        row = ctk.CTkFrame(dialog, fg_color="#111111", corner_radius=10)
        row.grid(row=index + 2, column=0, padx=20, pady=5, sticky="ew")
        row.grid_columnconfigure(1, weight=1)
        name_var = ctk.StringVar(value=favorite.get("name", f"Favorit {index + 1}"))
        file_var = ctk.StringVar(value=favorite.get("file", ""))
        ctk.CTkLabel(row, text=f"{index + 1}", width=28, text_color=GOLD).grid(
            row=0, column=0, rowspan=2, padx=(10, 4), pady=8
        )
        ctk.CTkEntry(
            row,
            textvariable=name_var,
            placeholder_text=f"Favorit {index + 1}",
        ).grid(row=0, column=1, padx=5, pady=(8, 3), sticky="ew")
        ctk.CTkEntry(row, textvariable=file_var, state="readonly").grid(
            row=1, column=1, padx=5, pady=(3, 8), sticky="ew"
        )

        def browse(slot=index, target=file_var):
            project = str(app.project_folder.get() or "").strip()
            if not project:
                messagebox.showwarning(
                    "Sound-Favoriten",
                    "Bitte zuerst unter Settings einen Projektordner auswählen.",
                    parent=dialog,
                )
                return
            service = app._sync_sound_service_project()
            sounds_dir = service.sounds_dir
            if sounds_dir is None or not sounds_dir.is_dir():
                messagebox.showwarning(
                    "Sound-Favoriten",
                    f"Der Sound-Ordner wurde nicht gefunden:\n\n{Path(project) / 'Sounds'}",
                    parent=dialog,
                )
                return
            selected = filedialog.askopenfilename(
                title=f"Sound-Favorit {slot + 1} auswählen",
                initialdir=str(sounds_dir),
                filetypes=[("WAV Audio", "*.wav"), ("Alle Dateien", "*.*")],
                parent=dialog,
            )
            if selected:
                relative = portable_effect_path(service, selected)
                if relative is None:
                    messagebox.showerror(
                        "Sound-Favoriten",
                        "Bitte eine WAV-Datei innerhalb des Projektordners Sounds auswählen.",
                        parent=dialog,
                    )
                    return
                target.set(relative)

        ctk.CTkButton(
            row,
            text="DURCHSUCHEN",
            width=115,
            command=browse,
            fg_color="#333333",
            hover_color="#444444",
        ).grid(row=0, column=2, rowspan=2, padx=(5, 10), pady=8)
        rows.append((name_var, file_var))

    actions = ctk.CTkFrame(dialog, fg_color="transparent")
    actions.grid(row=6, column=0, padx=20, pady=(14, 18), sticky="ew")
    actions.grid_columnconfigure((0, 1), weight=1)

    def save_and_close():
        app.config_data["sound_favorites"] = [
            {
                "name": (name_var.get().strip() or f"Favorit {index + 1}"),
                "file": file_var.get().strip(),
            }
            for index, (name_var, file_var) in enumerate(rows)
        ]
        save_config(app.config_data)
        app.refresh_sound_favorite_buttons()
        dialog.destroy()

    ctk.CTkButton(
        actions,
        text="ABBRECHEN",
        command=dialog.destroy,
        fg_color="#333333",
        hover_color="#444444",
    ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
    ctk.CTkButton(
        actions,
        text="SPEICHERN",
        command=save_and_close,
        fg_color=GOLD,
        hover_color=GOLD_DARK,
        text_color="#111111",
    ).grid(row=0, column=1, padx=(5, 0), sticky="ew")

    return dialog
