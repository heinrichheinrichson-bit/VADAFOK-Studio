"""Card Creator page construction.

This module owns the existing Card Creator layout while the application object
continues to provide its established state and callbacks. No behavior is
changed by this extraction.
"""

import customtkinter as ctk

from ..core import export_engine
from ..core.config import save_config
from ..core.template_store import (
    create_template,
    get_default_template,
    list_templates,
)
from .workspace_view import CardWorkspaceAccordion

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
DARK = "#090909"
PANEL = "#111111"


def build_batch_panel(app):
    """Render the current Card Creator batch list."""
    if not hasattr(app, "card_batch_body"):
        return

    for widget in app.card_batch_body.winfo_children():
        widget.destroy()

    state = app.card_creator_state
    if not state.batch_items:
        ctk.CTkLabel(
            app.card_batch_body,
            text="Noch keine Batch-Karten.\nKlicke + ADD CURRENT.",
            text_color="#777777",
            wraplength=240,
            justify="left",
        ).grid(row=0, column=0, padx=8, pady=8, sticky="w")
        return

    for row, item in enumerate(state.batch_items):
        active = row == state.batch_selected_index
        title = f"{row + 1}. {item.get('output_name', 'card')}"
        subtitle = f"{item.get('template', '')} · {item.get('profile', '')}"

        row_box = ctk.CTkFrame(
            app.card_batch_body,
            fg_color=GOLD if active else "#171717",
            corner_radius=8,
        )
        row_box.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
        row_box.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            row_box,
            text=title,
            text_color="#111111" if active else "#D9C58C",
            anchor="w",
        )
        title_label.grid(row=0, column=0, padx=10, pady=(6, 0), sticky="ew")

        subtitle_label = ctk.CTkLabel(
            row_box,
            text=subtitle,
            text_color="#333333" if active else "#777777",
            anchor="w",
        )
        subtitle_label.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="ew")

        for widget in (row_box, title_label, subtitle_label):
            widget.bind(
                "<Button-1>",
                lambda _event, index=row: app.card_batch_select(index),
            )

    app.card_batch_body.grid_columnconfigure(0, weight=1)


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
    preview_actions.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
    ctk.CTkButton(preview_actions, text="UPDATE PREVIEW", fg_color="#333333", hover_color="#444444", command=app.card_update_preview).grid(row=0, column=0, padx=(0, 4), sticky="ew")
    ctk.CTkButton(preview_actions, text="OPEN EXPORTS", fg_color="#333333", hover_color="#444444", command=app.card_open_export_folder).grid(row=0, column=1, padx=4, sticky="ew")
    ctk.CTkButton(preview_actions, text="REFRESH STYLES", fg_color="#333333", hover_color="#444444", command=app.card_build_form).grid(row=0, column=2, padx=4, sticky="ew")
    ctk.CTkButton(preview_actions, text="COPY LAST PATH", fg_color="#333333", hover_color="#444444", command=app.card_copy_last_path).grid(row=0, column=3, padx=(4, 0), sticky="ew")

    focus_state = {"active": False, "resize_job": None, "last_size": None}

    def set_preview_focus():
        focus_state["active"] = not focus_state["active"]
        if focus_state["active"]:
            left.grid_remove()
            form.grid_remove()
            outer.grid_columnconfigure(0, weight=0)
            outer.grid_columnconfigure(1, weight=1)
            outer.grid_columnconfigure(2, weight=0)
            focus_button.configure(text="SHOW SIDEBARS")
        else:
            left.grid()
            form.grid()
            outer.grid_columnconfigure(0, weight=1)
            outer.grid_columnconfigure(1, weight=4)
            outer.grid_columnconfigure(2, weight=2)
            focus_button.configure(text="FOCUS PREVIEW")
        app.after_idle(app.card_update_preview)

    focus_button = ctk.CTkButton(
        preview_actions,
        text="FOCUS PREVIEW",
        fg_color="#333333",
        hover_color="#444444",
        command=set_preview_focus,
    )
    focus_button.grid(row=0, column=4, padx=(8, 0), sticky="ew")

    app.card_preview_frame = ctk.CTkFrame(preview, fg_color="#050505", corner_radius=14, border_color="#3A2A0D", border_width=1)
    app.card_preview_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))

    def preview_resized(event):
        size = (event.width, event.height)
        if size == focus_state["last_size"] or min(size) < 120:
            return
        focus_state["last_size"] = size
        if focus_state["resize_job"] is not None:
            try:
                app.after_cancel(focus_state["resize_job"])
            except Exception:
                pass

        def refresh_after_resize():
            focus_state["resize_job"] = None
            app.card_update_preview()

        focus_state["resize_job"] = app.after(140, refresh_after_resize)

    app.card_preview_frame.bind("<Configure>", preview_resized, add="+")

    form = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    form.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
    form.grid_columnconfigure(0, weight=1)
    form.grid_rowconfigure(0, weight=1)

    def remember_workspace_section(section_key):
        app.config_data["card_workspace_section"] = section_key
        save_config(app.config_data)

    workspace = CardWorkspaceAccordion(
        form,
        active_key=app.config_data.get("card_workspace_section", "card_data"),
        on_change=remember_workspace_section,
    )
    workspace.frame.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
    app.card_workspace_accordion = workspace

    card_pane = workspace.add_section("card_data", "Card Data")
    card_pane.grid_columnconfigure(0, weight=1)
    card_pane.grid_rowconfigure(0, weight=1)

    app.card_form_frame = ctk.CTkScrollableFrame(
        card_pane, fg_color="#080808", corner_radius=10
    )
    app.card_form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    app.card_form_frame.grid_columnconfigure(0, weight=1)

    batch_box = workspace.add_section("batch_cards", "Batch Cards")
    batch_box.grid_columnconfigure(0, weight=1)
    batch_box.grid_rowconfigure(2, weight=1)

    batch_actions = ctk.CTkFrame(batch_box, fg_color="transparent")
    batch_actions.grid(row=0, column=0, padx=10, pady=(8, 6), sticky="ew")
    batch_actions.grid_columnconfigure((0, 1), weight=1)
    ctk.CTkButton(batch_actions, text="+ ADD CURRENT", fg_color="#333333", hover_color="#444444", command=app.card_batch_add_current).grid(row=0, column=0, padx=(0, 4), pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="RENDER BATCH", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=app.card_render_batch).grid(row=0, column=1, padx=(4, 0), pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="IMPORT CSV/XLSX", fg_color="#333333", hover_color="#444444", command=app.card_import_batch_file).grid(row=1, column=0, columnspan=2, padx=0, pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="SAVE PROJECT", fg_color="#333333", hover_color="#444444", command=app.card_save_batch_project).grid(row=2, column=0, padx=(0, 4), pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="LOAD PROJECT", fg_color="#333333", hover_color="#444444", command=app.card_load_batch_project).grid(row=2, column=1, padx=(4, 0), pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="DUPLICATE", fg_color="#333333", hover_color="#444444", command=app.card_batch_duplicate_selected).grid(row=3, column=0, padx=(0, 4), pady=2, sticky="ew")
    ctk.CTkButton(batch_actions, text="REMOVE", fg_color="#5A1F1F", hover_color="#7A2A2A", command=app.card_batch_remove_selected).grid(row=3, column=1, padx=(4, 0), pady=2, sticky="ew")

    app.card_batch_body = ctk.CTkScrollableFrame(
        batch_box, fg_color="#080808", corner_radius=10
    )
    app.card_batch_body.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

    output_pane = workspace.add_section("output", "Output")
    output_pane.grid_columnconfigure(0, weight=1)
    output_pane.grid_rowconfigure(0, weight=1)
    output_scroll = ctk.CTkScrollableFrame(
        output_pane, fg_color="#080808", corner_radius=10
    )
    output_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    output_scroll.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(output_scroll, text="Output Name", text_color="#BCA870").grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")
    ctk.CTkEntry(output_scroll, textvariable=app.card_output_name).grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")

    ctk.CTkLabel(output_scroll, text="Export Profile", text_color="#BCA870").grid(row=2, column=0, padx=10, pady=(2, 2), sticky="w")
    ctk.CTkOptionMenu(
        output_scroll, values=export_engine.list_export_profiles(),
        variable=app.card_export_profile, fg_color="#333333",
        button_color="#444444", button_hover_color="#555555",
        command=lambda _v: app.card_update_preview()
    ).grid(row=3, column=0, padx=10, pady=(0, 8), sticky="ew")

    app.card_export_profile_info = ctk.CTkLabel(
        output_scroll, text="", text_color="#777777",
        wraplength=240, justify="left"
    )
    app.card_export_profile_info.grid(row=4, column=0, padx=10, pady=(0, 8), sticky="w")

    ctk.CTkCheckBox(
        output_scroll, text="Auto Preview", variable=app.card_auto_preview,
        text_color="#BCA870", fg_color=GOLD, hover_color=GOLD_DARK
    ).grid(row=5, column=0, padx=10, pady=(0, 10), sticky="w")

    buttons = ctk.CTkFrame(output_scroll, fg_color="transparent")
    buttons.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 10))
    buttons.grid_columnconfigure((0, 1), weight=1)
    ctk.CTkButton(buttons, text="CLEAR FIELDS", fg_color="#333333", hover_color="#444444", command=app.card_clear_values).grid(row=0, column=0, padx=(0, 4), pady=4, sticky="ew")
    ctk.CTkButton(buttons, text="RENDER CARD", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=app.card_render_final).grid(row=0, column=1, padx=(4, 0), pady=4, sticky="ew")
    ctk.CTkButton(buttons, text="UNDO DATA", fg_color="#333333", hover_color="#444444", command=app.card_undo_data).grid(row=1, column=0, padx=(0, 4), pady=4, sticky="ew")
    ctk.CTkButton(buttons, text="REDO DATA", fg_color="#333333", hover_color="#444444", command=app.card_redo_data).grid(row=1, column=1, padx=(4, 0), pady=4, sticky="ew")

    app.card_render_status = ctk.CTkLabel(
        buttons, text="Noch nicht gerendert.", text_color="#BCA870",
        wraplength=260, justify="left"
    )
    app.card_render_status.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky="w")

    app.card_build_form()
    app.card_build_batch_panel()
    app.card_update_preview()
