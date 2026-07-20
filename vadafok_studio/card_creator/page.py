"""Card Creator page construction.

This module owns the existing Card Creator layout while the application object
continues to provide its established state and callbacks. No behavior is
changed by this extraction.
"""

import customtkinter as ctk

from ..core import export_engine
from ..core.template_store import (
    create_template,
    get_default_template,
    list_templates,
)

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
DARK = "#090909"
PANEL = "#111111"


def show_card_creator_page(app):
    """Build and display the existing Card Creator page for *app*."""
    app.set_active("Card Creator")
    app.clear_main()
    app.page_title("Card Creator")

    names = list_templates()
    if not names:
        create_template("Default Stream Plan")
        names = list_templates()

    if not app.card_selected_template.get() or app.card_selected_template.get() not in names:
        default_name = get_default_template()
        app.card_selected_template.set(default_name if default_name in names else sorted(names)[0])

    if not app.card_output_name.get():
        app.card_output_name.set(app.card_default_output_name())

    outer = ctk.CTkFrame(app.main, fg_color=DARK)
    outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_columnconfigure(1, weight=4)
    outer.grid_columnconfigure(2, weight=2)
    outer.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    left.grid_rowconfigure(1, weight=1)
    ctk.CTkLabel(left, text="Templates", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

    tlist = ctk.CTkScrollableFrame(left, fg_color="#0B0B0B", corner_radius=12)
    tlist.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
    app.card_recent_templates_frame = ctk.CTkFrame(
        tlist,
        fg_color="transparent",
    )

    app.card_all_templates_label = ctk.CTkLabel(
        tlist,
        text="ALL TEMPLATES",
        text_color="#BCA870",
        anchor="w",
        font=ctk.CTkFont(size=11, weight="bold"),
    )
    app.card_all_templates_label.pack(
        fill="x", padx=8, pady=(8, 3)
    )

    app.card_refresh_recent_templates()

    app.card_all_templates_frame = ctk.CTkFrame(
        tlist,
        fg_color="transparent",
    )
    app.card_all_templates_frame.pack(fill="x", padx=0, pady=0)
    app.card_template_buttons = {}
    app.card_build_all_template_buttons()

    preview = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    preview.grid(row=0, column=1, sticky="nsew", padx=12)
    preview.grid_columnconfigure(0, weight=1)
    preview.grid_rowconfigure(2, weight=1)

    header = ctk.CTkFrame(preview, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
    header.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(header, text="Preview", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w")
    app.card_preview_info = ctk.CTkLabel(header, text="", text_color="#8FE6A0", anchor="e")
    app.card_preview_info.grid(row=0, column=1, sticky="e")

    preview_actions = ctk.CTkFrame(preview, fg_color="transparent")
    preview_actions.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))
    preview_actions.grid_columnconfigure((0, 1, 2, 3), weight=1)
    ctk.CTkButton(preview_actions, text="UPDATE PREVIEW", fg_color="#333333", hover_color="#444444", command=app.card_update_preview).grid(row=0, column=0, padx=(0, 4), sticky="ew")
    ctk.CTkButton(preview_actions, text="OPEN EXPORTS", fg_color="#333333", hover_color="#444444", command=app.card_open_export_folder).grid(row=0, column=1, padx=4, sticky="ew")
    ctk.CTkButton(preview_actions, text="REFRESH STYLES", fg_color="#333333", hover_color="#444444", command=app.card_build_form).grid(row=0, column=2, padx=4, sticky="ew")
    ctk.CTkButton(preview_actions, text="COPY LAST PATH", fg_color="#333333", hover_color="#444444", command=app.card_copy_last_path).grid(row=0, column=3, padx=(4, 0), sticky="ew")

    app.card_preview_frame = ctk.CTkFrame(preview, fg_color="#050505", corner_radius=14, border_color="#3A2A0D", border_width=1)
    app.card_preview_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))

    form = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    form.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
    form.grid_columnconfigure(0, weight=1)
    form.grid_rowconfigure(1, weight=3)
    form.grid_rowconfigure(2, weight=2)

    ctk.CTkLabel(form, text="Card Data", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

    app.card_form_frame = ctk.CTkScrollableFrame(form, fg_color="#0B0B0B", corner_radius=12)
    app.card_form_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
    app.card_form_frame.grid_columnconfigure(0, weight=1)

    batch_box = ctk.CTkFrame(form, fg_color="#0B0B0B", corner_radius=12)
    batch_box.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 12))
    batch_box.grid_columnconfigure(0, weight=1)
    batch_box.grid_rowconfigure(2, weight=1)

    ctk.CTkLabel(
        batch_box,
        text="Batch Cards",
        text_color=GOLD,
        font=ctk.CTkFont(size=16, weight="bold")
    ).grid(row=0, column=0, padx=10, pady=(10, 6), sticky="w")

    batch_actions = ctk.CTkFrame(batch_box, fg_color="transparent")
    batch_actions.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="ew")
    batch_actions.grid_columnconfigure((0, 1), weight=1)
    ctk.CTkButton(batch_actions, text="+ ADD CURRENT", fg_color="#333333", hover_color="#444444", command=app.card_batch_add_current).grid(row=0, column=0, padx=(0, 4), pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="RENDER BATCH", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=app.card_render_batch).grid(row=0, column=1, padx=(4, 0), pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="IMPORT CSV/XLSX", fg_color="#333333", hover_color="#444444", command=app.card_import_batch_file).grid(row=1, column=0, columnspan=2, padx=0, pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="SAVE PROJECT", fg_color="#333333", hover_color="#444444", command=app.card_save_batch_project).grid(row=2, column=0, padx=(0, 4), pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="LOAD PROJECT", fg_color="#333333", hover_color="#444444", command=app.card_load_batch_project).grid(row=2, column=1, padx=(4, 0), pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="DUPLICATE", fg_color="#333333", hover_color="#444444", command=app.card_batch_duplicate_selected).grid(row=3, column=0, padx=(0, 4), pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="REMOVE", fg_color="#5A1F1F", hover_color="#7A2A2A", command=app.card_batch_remove_selected).grid(row=3, column=1, padx=(4, 0), pady=2, sticky="ew")

    app.card_batch_body = ctk.CTkScrollableFrame(batch_box, fg_color="#080808", corner_radius=10, height=190)
    app.card_batch_body.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    export_box = ctk.CTkFrame(form, fg_color="#0B0B0B", corner_radius=12)
    export_box.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 12))
    export_box.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(export_box, text="Output Name", text_color="#BCA870").grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")
    ctk.CTkEntry(export_box, textvariable=app.card_output_name).grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")

    ctk.CTkLabel(export_box, text="Export Profile", text_color="#BCA870").grid(row=2, column=0, padx=10, pady=(2, 2), sticky="w")
    ctk.CTkOptionMenu(
        export_box,
        values=export_engine.list_export_profiles(),
        variable=app.card_export_profile,
        fg_color="#333333",
        button_color="#444444",
        button_hover_color="#555555",
        command=lambda _v: app.card_update_preview()
    ).grid(row=3, column=0, padx=10, pady=(0, 8), sticky="ew")

    app.card_export_profile_info = ctk.CTkLabel(export_box, text="", text_color="#777777", wraplength=240, justify="left")
    app.card_export_profile_info.grid(row=4, column=0, padx=10, pady=(0, 8), sticky="w")

    ctk.CTkCheckBox(
        export_box,
        text="Auto Preview",
        variable=app.card_auto_preview,
        text_color="#BCA870",
        fg_color=GOLD,
        hover_color=GOLD_DARK
    ).grid(row=5, column=0, padx=10, pady=(0, 10), sticky="w")

    buttons = ctk.CTkFrame(form, fg_color="transparent")
    buttons.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 18))
    buttons.grid_columnconfigure((0, 1), weight=1)
    ctk.CTkButton(buttons, text="CLEAR FIELDS", fg_color="#333333", hover_color="#444444", command=app.card_clear_values).grid(row=0, column=0, padx=(0, 4), pady=4, sticky="ew")
    ctk.CTkButton(buttons, text="RENDER CARD", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=app.card_render_final).grid(row=0, column=1, padx=(4, 0), pady=4, sticky="ew")

    ctk.CTkButton(buttons, text="UNDO DATA", fg_color="#333333", hover_color="#444444", command=app.card_undo_data).grid(row=1, column=0, padx=(0, 4), pady=4, sticky="ew")
    ctk.CTkButton(buttons, text="REDO DATA", fg_color="#333333", hover_color="#444444", command=app.card_redo_data).grid(row=1, column=1, padx=(4, 0), pady=4, sticky="ew")

    app.card_render_status = ctk.CTkLabel(buttons, text="Noch nicht gerendert.", text_color="#BCA870", wraplength=260, justify="left")
    app.card_render_status.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky="w")

    app.card_build_form()
    app.card_build_batch_panel()
    app.card_update_preview()
