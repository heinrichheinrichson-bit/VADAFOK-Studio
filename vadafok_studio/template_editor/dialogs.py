"""Modal dialogs used by the Template Editor."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"


def ask_template_name(app: Any, title: str, initial_value: str) -> str | None:
    result = {"value": None}
    dialog = ctk.CTkToplevel(app)
    dialog.title(title)
    dialog.geometry("520x210")
    dialog.resizable(False, False)
    dialog.transient(app)
    dialog.grab_set()
    dialog.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(
        dialog, text=title, text_color=GOLD,
        font=ctk.CTkFont(size=22, weight="bold"),
    ).grid(row=0, column=0, padx=24, pady=(24, 8), sticky="w")
    ctk.CTkLabel(
        dialog, text="Neuer Name", text_color="#BCA870",
        font=ctk.CTkFont(size=14),
    ).grid(row=1, column=0, padx=24, pady=(0, 4), sticky="w")
    entry = ctk.CTkEntry(dialog, height=42, font=ctk.CTkFont(size=18))
    entry.grid(row=2, column=0, padx=24, pady=(0, 18), sticky="ew")
    entry.insert(0, initial_value or "")
    entry.focus_set()
    entry.select_range(0, "end")

    def save() -> None:
        value = entry.get().strip()
        if value:
            result["value"] = value
            dialog.destroy()

    def cancel() -> None:
        dialog.destroy()

    buttons = ctk.CTkFrame(dialog, fg_color="transparent")
    buttons.grid(row=3, column=0, padx=24, pady=(0, 24), sticky="ew")
    buttons.grid_columnconfigure((0, 1), weight=1)
    ctk.CTkButton(
        buttons, text="Speichern", height=38, fg_color=GOLD,
        text_color="#111111", hover_color=GOLD_DARK, command=save,
    ).grid(row=0, column=0, padx=(0, 8), sticky="ew")
    ctk.CTkButton(
        buttons, text="Abbrechen", height=38, fg_color="#333333",
        hover_color="#444444", command=cancel,
    ).grid(row=0, column=1, padx=(8, 0), sticky="ew")
    dialog.bind("<Return>", lambda _event: save())
    dialog.bind("<Escape>", lambda _event: cancel())
    dialog.protocol("WM_DELETE_WINDOW", cancel)
    app.wait_window(dialog)
    return result["value"]
