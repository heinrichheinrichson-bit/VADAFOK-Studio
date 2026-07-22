"""Banner profile editor page construction.

This module owns the page layout while the application object continues to
provide the existing editor state and callbacks. The separation is deliberately
behavior-preserving and keeps navigation in ``app.py`` lightweight.
"""

import tkinter as tk

import customtkinter as ctk

from ..core.banner_profiles import has_profile
from ..core.library import scan_library

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
DARK = "#090909"
PANEL = "#111111"
TEXT = "#F2E2B6"


def show_banner_profiles_page(app):
    """Build and display the existing Banner Editor page for *app*."""
    app.set_active("Banner Editor")
    app.clear_main()
    app.page_title("Banner Editor")

    app.library_items = scan_library(app.project_folder.get())
    banners = [
        item
        for item in app.library_items
        if item.section == "Banners" and item.kind == "image"
    ]

    outer = ctk.CTkFrame(app.main, fg_color=DARK)
    outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_columnconfigure(1, weight=4)
    outer.grid_columnconfigure(2, weight=1)
    outer.grid_columnconfigure(3, weight=1)
    outer.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    left.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(
        left,
        text="Banner",
        text_color=GOLD,
        font=ctk.CTkFont(size=18, weight="bold"),
    ).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
    banner_list = ctk.CTkScrollableFrame(
        left,
        fg_color="#0B0B0B",
        corner_radius=12,
    )
    banner_list.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

    if not banners:
        ctk.CTkLabel(
            banner_list,
            text="Keine Banner gefunden.",
            text_color="#BCA870",
        ).pack(anchor="w", padx=12, pady=12)
    else:
        for item in banners:
            status = "✓ " if has_profile(app.banner_profiles, item.relative) else "⚠ "
            ctk.CTkButton(
                banner_list,
                text=status + item.name,
                anchor="w",
                height=38,
                fg_color="#171717",
                hover_color="#2C2C2C",
                command=lambda it=item: app.editor_select_banner(it),
            ).pack(fill="x", padx=8, pady=4)

    right = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(1, weight=1)

    header = ctk.CTkFrame(right, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
    header.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        header,
        text="Textbereich mit der Maus setzen",
        text_color=GOLD,
        font=ctk.CTkFont(size=18, weight="bold"),
    ).grid(row=0, column=0, sticky="w")
    app.editor_status_label = ctk.CTkLabel(
        header,
        text="Noch kein Banner ausgewählt",
        text_color="#BCA870",
        anchor="e",
    )
    app.editor_status_label.grid(row=0, column=1, sticky="e")

    app.editor_preview_frame = ctk.CTkFrame(
        right,
        fg_color="#050505",
        corner_radius=14,
        border_color="#3A2A0D",
        border_width=1,
    )
    app.editor_preview_frame.grid(
        row=1,
        column=0,
        sticky="nsew",
        padx=18,
        pady=(0, 12),
    )
    app.editor_preview_frame.grid_columnconfigure(0, weight=1)
    app.editor_preview_frame.grid_rowconfigure(0, weight=1)

    app.editor_canvas = tk.Canvas(
        app.editor_preview_frame,
        bg="#050505",
        highlightthickness=0,
        cursor="crosshair",
    )
    app.editor_canvas.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
    app.editor_canvas.bind("<ButtonPress-1>", app.editor_mouse_down)
    app.editor_canvas.bind("<B1-Motion>", app.editor_mouse_drag)
    app.editor_canvas.bind("<ButtonRelease-1>", app.editor_mouse_up)
    app.editor_canvas.bind("<Motion>", app.editor_mouse_motion)

    controls = ctk.CTkScrollableFrame(
        right,
        fg_color="#0B0B0B",
        corner_radius=12,
    )
    controls.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
    controls.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(controls, text="Beispieltext", text_color="#BCA870").grid(
        row=0,
        column=0,
        padx=(0, 8),
        pady=4,
        sticky="w",
    )
    sample_entry = ctk.CTkEntry(controls, textvariable=app.editor_sample_text)
    sample_entry.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="ew")
    sample_entry.bind("<KeyRelease>", lambda _event: app.editor_update_overlay())

    ctk.CTkLabel(controls, text="Schriftart", text_color="#BCA870").grid(
        row=1,
        column=0,
        padx=(12, 8),
        pady=4,
        sticky="w",
    )
    font_entry = ctk.CTkEntry(controls, textvariable=app.editor_font_family)
    font_entry.grid(row=1, column=1, padx=(0, 8), pady=4, sticky="ew")
    font_entry.bind("<KeyRelease>", lambda _event: app.editor_apply_profile_values())

    ctk.CTkLabel(controls, text="GrÃ¶ÃŸe", text_color="#BCA870").grid(
        row=1,
        column=2,
        padx=(12, 8),
        pady=4,
        sticky="w",
    )
    size_entry = ctk.CTkEntry(controls, textvariable=app.editor_font_size)
    size_entry.grid(row=1, column=3, padx=(0, 8), pady=4, sticky="ew")
    size_entry.bind("<KeyRelease>", lambda _event: app.editor_apply_profile_values())

    ctk.CTkLabel(controls, text="Textfarbe", text_color="#BCA870").grid(
        row=2,
        column=0,
        padx=(12, 8),
        pady=4,
        sticky="w",
    )
    text_color_entry = ctk.CTkEntry(controls, textvariable=app.editor_text_color)
    text_color_entry.grid(row=2, column=1, padx=(0, 8), pady=4, sticky="ew")
    text_color_entry.bind(
        "<KeyRelease>",
        lambda _event: app.editor_apply_profile_values(),
    )

    ctk.CTkLabel(controls, text="Konturfarbe", text_color="#BCA870").grid(
        row=2,
        column=2,
        padx=(12, 8),
        pady=4,
        sticky="w",
    )
    stroke_color_entry = ctk.CTkEntry(
        controls,
        textvariable=app.editor_stroke_color,
    )
    stroke_color_entry.grid(row=2, column=3, padx=(0, 8), pady=4, sticky="ew")
    stroke_color_entry.bind(
        "<KeyRelease>",
        lambda _event: app.editor_apply_profile_values(),
    )

    ctk.CTkLabel(controls, text="KonturstÃ¤rke", text_color="#BCA870").grid(
        row=3,
        column=0,
        padx=(12, 8),
        pady=4,
        sticky="w",
    )
    stroke_width_entry = ctk.CTkEntry(
        controls,
        textvariable=app.editor_stroke_width,
    )
    stroke_width_entry.grid(row=3, column=1, padx=(0, 8), pady=4, sticky="ew")
    stroke_width_entry.bind(
        "<KeyRelease>",
        lambda _event: app.editor_apply_profile_values(),
    )

    ctk.CTkCheckBox(
        controls,
        text="GroÃŸbuchstaben",
        variable=app.editor_uppercase,
        text_color=TEXT,
        command=app.editor_apply_profile_values,
    ).grid(row=3, column=2, padx=(12, 8), pady=4, sticky="w")

    ctk.CTkButton(
        controls,
        text="PROFIL SPEICHERN",
        fg_color=GOLD,
        text_color="#111111",
        hover_color=GOLD_DARK,
        command=app.editor_save_profile,
    ).grid(row=4, column=0, columnspan=2, padx=4, pady=8, sticky="ew")
    ctk.CTkButton(
        controls,
        text="BEREICH ZURÃœCKSETZEN",
        fg_color="#333333",
        hover_color="#444444",
        command=app.editor_reset_area,
    ).grid(row=4, column=2, padx=4, pady=8, sticky="ew")
    ctk.CTkButton(
        controls,
        text="STIL ZURÃœCKSETZEN",
        fg_color="#333333",
        hover_color="#444444",
        command=app.editor_reset_style,
    ).grid(row=4, column=3, padx=4, pady=8, sticky="ew")

    ctk.CTkLabel(
        right,
        text=(
            "Phase C: Ziehe den goldenen Rahmen direkt im Banner. Ziehen in "
            "der Mitte verschiebt, Ziehen an den Ecken/Kanten verändert die Größe."
        ),
        text_color="#D9C58C",
        wraplength=820,
        justify="left",
    ).grid(row=3, column=0, sticky="w", padx=18, pady=(0, 18))

    if app.editor_selected_banner is None and banners:
        app.editor_select_banner(banners[0])
    elif app.editor_selected_banner is not None:
        app.editor_draw_canvas()
