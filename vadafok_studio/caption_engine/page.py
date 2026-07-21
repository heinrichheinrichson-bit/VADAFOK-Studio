"""Caption Engine settings page."""

from __future__ import annotations

import customtkinter as ctk

from .controller import CAPTION_PRESETS

PANEL = "#111111"
CARD = "#171717"
GOLD = "#E0AA36"
GOLD_DARK = "#9A6B16"
TEXT = "#F4E7BF"


def _section(parent, title, row, column, columnspan=1):
    frame = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14)
    frame.grid(row=row, column=column, columnspan=columnspan, padx=8, pady=8, sticky="nsew")
    ctk.CTkLabel(frame, text=title, text_color=GOLD, font=ctk.CTkFont(size=16, weight="bold")).pack(
        anchor="w", padx=16, pady=(14, 8),
    )
    return frame


def _entry_row(parent, label, variable, controller, hint=""):
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=5)
    ctk.CTkLabel(row, text=label, width=145, anchor="w", text_color="#BCA870").pack(side="left")
    entry = ctk.CTkEntry(row, textvariable=variable)
    entry.pack(side="left", fill="x", expand=True)
    entry.bind("<KeyRelease>", controller.mark_changed, add="+")
    if hint:
        ctk.CTkLabel(row, text=hint, width=78, anchor="e", text_color="#777777").pack(side="left", padx=(8, 0))
    return entry


def _color_row(parent, label, variable, controller):
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=5)
    ctk.CTkLabel(row, text=label, width=145, anchor="w", text_color="#BCA870").pack(side="left")
    entry = ctk.CTkEntry(row, textvariable=variable)
    entry.pack(side="left", fill="x", expand=True)
    entry.bind("<KeyRelease>", controller.mark_changed, add="+")
    ctk.CTkButton(
        row, text="FARBE…", width=82, fg_color="#3A3A3A",
        command=lambda: controller.choose_color(variable),
    ).pack(side="left", padx=(8, 0))
    palette = ctk.CTkFrame(parent, fg_color="transparent")
    palette.pack(fill="x", padx=(161, 16), pady=(0, 5))
    for index, color in enumerate(controller.color_favorites()):
        button = ctk.CTkButton(
            palette, text=str(index + 1), width=42, height=24,
            fg_color=color, hover_color=color, text_color="#808080",
            command=lambda slot=index: controller.use_favorite_color(
                variable, controller.color_favorites()[slot],
            ),
        )
        button._caption_color_slot = index
        button._caption_color_variable = variable
        button.pack(side="left", padx=(0, 6))
        button.bind(
            "<Button-3>",
            lambda _event, slot=index: controller.store_favorite_color(slot, variable),
        )
        app_buttons = getattr(controller.app, "caption_color_favorite_buttons", None)
        if app_buttons is not None:
            app_buttons.append(button)


def show_caption_engine_page(app, controller):
    app.set_active("Caption Engine")
    app.clear_main()
    app.page_title("Caption Engine")

    root = ctk.CTkFrame(app.main, fg_color=PANEL, corner_radius=18)
    root.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)

    toolbar = ctk.CTkFrame(root, fg_color="transparent")
    toolbar.grid(row=0, column=0, columnspan=2, padx=16, pady=(14, 4), sticky="ew")
    ctk.CTkLabel(toolbar, text="Preset", text_color="#BCA870").pack(side="left")
    ctk.CTkOptionMenu(
        toolbar, values=list(CAPTION_PRESETS), command=controller.apply_preset,
        fg_color="#333333", button_color=GOLD_DARK,
    ).pack(side="left", padx=8)
    app.caption_engine_status_label = ctk.CTkLabel(toolbar, text="Keine Änderungen", text_color="#777777")
    app.caption_engine_status_label.pack(side="right")

    left = ctk.CTkFrame(root, fg_color="transparent")
    left.grid(row=1, column=0, padx=(8, 4), pady=4, sticky="nsew")
    left.grid_columnconfigure(0, weight=1)
    right = ctk.CTkFrame(root, fg_color="transparent")
    right.grid(row=1, column=1, padx=(4, 8), pady=4, sticky="nsew")
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(0, weight=1)

    typography = _section(left, "Schrift & Farben", 0, 0)
    app.caption_color_favorite_buttons = []
    engine_row = ctk.CTkFrame(typography, fg_color="transparent")
    engine_row.pack(fill="x", padx=16, pady=5)
    ctk.CTkLabel(engine_row, text="Engine", width=145, anchor="w", text_color="#BCA870").pack(side="left")
    ctk.CTkOptionMenu(
        engine_row, values=["smart_png", "obs_text"], variable=app.caption_engine,
        command=controller.mark_changed,
    ).pack(side="left", fill="x", expand=True)
    _entry_row(typography, "Schriftfamilie", app.caption_font_family, controller)
    _entry_row(typography, "Schriftgröße", app.caption_font_size, controller, "8–500")
    _color_row(typography, "Textfarbe (Hex)", app.caption_text_color, controller)
    _color_row(typography, "Konturfarbe (Hex)", app.caption_stroke_color, controller)
    _entry_row(typography, "Konturstärke", app.caption_stroke_width, controller, "0–30")
    ctk.CTkCheckBox(
        typography, text="Großbuchstaben", variable=app.caption_uppercase,
        command=controller.mark_changed, text_color=TEXT,
    ).pack(anchor="w", padx=16, pady=(8, 14))

    ctk.CTkLabel(
        typography,
        text="Farbfavorit: klicken zum Anwenden · Rechtsklick speichert den aktuellen Hex-Wert im Slot",
        text_color="#8E8264", wraplength=620, justify="left",
    ).pack(anchor="w", padx=16, pady=(0, 12))

    output = _section(left, "Ausgabe & Sicherheitsbereich", 1, 0)
    _entry_row(output, "Render-Breite", app.caption_render_width, controller, "320–7680")
    _entry_row(output, "Render-Höhe", app.caption_render_height, controller, "80–2160")
    _entry_row(output, "Abstand links", app.caption_safe_left, controller, "0–45 %")
    _entry_row(output, "Abstand rechts", app.caption_safe_right, controller, "0–45 %")
    _entry_row(output, "Abstand oben", app.caption_safe_top, controller, "0–45 %")
    _entry_row(output, "Abstand unten", app.caption_safe_bottom, controller, "0–45 %")

    preview = _section(right, "Live-Vorschau", 0, 0)
    app.caption_preview_text = ctk.StringVar(value="DEINE CAPTION")
    preview_entry = ctk.CTkEntry(preview, textvariable=app.caption_preview_text, placeholder_text="Vorschautext")
    preview_entry.pack(fill="x", padx=16, pady=(0, 10))
    preview_entry.bind("<KeyRelease>", controller.schedule_preview, add="+")
    canvas = ctk.CTkFrame(preview, fg_color="#020202", corner_radius=12, border_width=1, border_color="#3A2A0D")
    canvas.pack(fill="both", expand=True, padx=16, pady=(0, 14))
    app.caption_engine_preview_label = ctk.CTkLabel(canvas, text="Vorschau wird erstellt…", text_color="#777777")
    app.caption_engine_preview_label.place(relx=0.5, rely=0.5, anchor="center")

    info = _section(right, "Hinweis", 1, 0)
    ctk.CTkLabel(
        info,
        text=("smart_png rendert Banner und Text als fertige PNG. OBS benötigt dafür "
              "die Bildquelle ‘VADAFOK Caption Render’. Hex-Farbcodes bleiben jederzeit direkt editierbar."),
        text_color="#D9C58C", wraplength=700, justify="left",
    ).pack(anchor="w", padx=16, pady=(0, 14))

    actions = ctk.CTkFrame(root, fg_color="transparent")
    actions.grid(row=2, column=0, columnspan=2, padx=16, pady=(4, 16), sticky="ew")
    ctk.CTkButton(
        actions, text="ÄNDERUNGEN ZURÜCKSETZEN", fg_color="#3A3A3A",
        command=controller.reset_changes,
    ).pack(side="left")
    ctk.CTkButton(
        actions, text="EINSTELLUNGEN SPEICHERN", fg_color=GOLD,
        text_color="#111111", hover_color=GOLD_DARK, command=controller.save,
    ).pack(side="right")
    controller.schedule_preview()
