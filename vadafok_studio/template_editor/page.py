"""Template Editor page construction."""

from __future__ import annotations

from typing import Any
import tkinter as tk

import customtkinter as ctk

from ..core.template_store import create_template, get_default_template, list_templates

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
DARK = "#090909"
PANEL = "#111111"


def show_template_editor_page(app: Any) -> None:
    """Build and display the Template Editor workspace."""
    app.library_template_background_picker_mode = False
    app.set_active("Template Editor")
    app.clear_main()
    app.page_title("Template Editor")

    if not list_templates():
        create_template("Default Stream Plan")
    if app.template_selected_name not in list_templates():
        default_name = get_default_template()
        app.template_selected_name = default_name if default_name in list_templates() else list_templates()[0]

    outer = ctk.CTkFrame(app.main, fg_color=DARK)
    outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_columnconfigure(1, weight=4)
    outer.grid_columnconfigure(2, weight=1)
    outer.grid_columnconfigure(3, weight=1)
    outer.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
    left.grid_rowconfigure(2, weight=1)

    ctk.CTkLabel(left, text="Templates", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
    template_actions = ctk.CTkFrame(left, fg_color="transparent")
    template_actions.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="ew")
    template_actions.grid_columnconfigure(0, weight=1)
    template_actions.grid_columnconfigure(1, weight=1)

    ctk.CTkButton(template_actions, text="+ NEW", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=app.template_create_default).grid(row=0, column=0, padx=(0, 4), pady=3, sticky="ew")
    ctk.CTkButton(template_actions, text="RENAME", fg_color="#333333", hover_color="#444444", command=app.template_rename_current).grid(row=0, column=1, padx=(4, 0), pady=3, sticky="ew")
    ctk.CTkButton(template_actions, text="DUPLICATE", fg_color="#333333", hover_color="#444444", command=app.template_duplicate_current).grid(row=1, column=0, padx=(0, 4), pady=3, sticky="ew")
    ctk.CTkButton(template_actions, text="DEFAULT", fg_color="#333333", hover_color="#444444", command=app.template_set_current_default).grid(row=1, column=1, padx=(4, 0), pady=3, sticky="ew")
    ctk.CTkButton(template_actions, text="DELETE", fg_color="#5A1F1F", hover_color="#7A2A2A", command=app.template_delete_current).grid(row=2, column=0, columnspan=2, padx=0, pady=3, sticky="ew")

    template_list = ctk.CTkScrollableFrame(left, fg_color="#0B0B0B", corner_radius=12)
    template_list.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))

    default_template_name = get_default_template()
    app.template_list_buttons = {}
    for name in sorted(list_templates()):
        prefix = "✓ " if name == app.template_selected_name else ""
        if name == default_template_name:
            prefix += "★ "
        button = ctk.CTkButton(
            template_list,
            text=prefix + name,
            anchor="w",
            fg_color="#171717",
            hover_color="#2C2C2C",
            command=lambda n=name: app.template_select(n)
        )
        button.pack(fill="x", padx=8, pady=4)
        app.template_list_buttons[name] = button

    right = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(1, weight=1)

    header = ctk.CTkFrame(right, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
    header.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(header, text="Multi-Field Layout", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w")
    app.template_status_label = ctk.CTkLabel(header, text=app.template_selected_name, text_color="#BCA870", anchor="e")
    app.template_status_label.grid(row=0, column=1, sticky="e")

    app.template_canvas_frame = ctk.CTkFrame(right, fg_color="#050505", corner_radius=14, border_color="#3A2A0D", border_width=1)
    app.template_canvas_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
    app.template_canvas_frame.grid_columnconfigure(0, weight=1)
    app.template_canvas_frame.grid_rowconfigure(0, weight=1)

    app.template_canvas = tk.Canvas(app.template_canvas_frame, bg="#050505", highlightthickness=0, cursor="crosshair")
    app.template_canvas.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
    app.template_canvas.bind("<ButtonPress-1>", app.template_mouse_down)
    app.template_canvas.bind("<B1-Motion>", app.template_mouse_drag)
    app.template_canvas.bind("<ButtonRelease-1>", app.template_mouse_up)
    app.template_canvas.bind("<Motion>", app.template_mouse_motion)
    app.template_canvas.bind("<Control-MouseWheel>", app.template_mouse_wheel_zoom)
    app.template_canvas.bind("<Control-Button-4>", app.template_mouse_wheel_zoom)
    app.template_canvas.bind("<Control-Button-5>", app.template_mouse_wheel_zoom)
    app.template_canvas.bind("<KeyPress>", app.template_key_down)
    app.template_canvas.bind("<KeyPress>", app.template_keyboard_handler, add="+")
    app.template_canvas.bind("<KeyRelease>", app.template_key_up)
    app.bind("<KeyPress>", app.template_key_down)
    app.bind("<KeyPress>", app.template_keyboard_handler, add="+")
    app.bind("<KeyRelease>", app.template_key_up)
    app.template_canvas.bind("<ButtonPress-2>", app.template_pan_start_drag)
    app.template_canvas.bind("<B2-Motion>", app.template_pan_drag)
    app.template_canvas.bind("<ButtonRelease-2>", app.template_pan_end_drag)
    app.template_canvas.bind("<Shift-ButtonPress-1>", app.template_pan_start_drag)
    app.template_canvas.bind("<Shift-B1-Motion>", app.template_pan_drag)
    app.template_canvas.bind("<Shift-ButtonRelease-1>", app.template_pan_end_drag)

    controls = ctk.CTkFrame(right, fg_color="transparent")
    controls.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
    controls.grid_columnconfigure((0,1,2,3,4), weight=1)
    app.template_action_buttons = {}

    ctk.CTkButton(controls, text="+ ADD FIELD", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=app.template_add_field).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
    app.template_action_buttons["copy"] = ctk.CTkButton(controls, text="COPY FIELD", fg_color="#333333", hover_color="#444444", command=app.template_copy_field)
    app.template_action_buttons["copy"].grid(row=0, column=1, padx=4, pady=4, sticky="ew")
    app.template_action_buttons["delete"] = ctk.CTkButton(controls, text="DELETE FIELD", fg_color="#333333", hover_color="#444444", command=app.template_delete_field)
    app.template_action_buttons["delete"].grid(row=0, column=2, padx=4, pady=4, sticky="ew")
    ctk.CTkButton(controls, text="SAVE TEMPLATE", fg_color="#333333", hover_color="#444444", command=app.template_save).grid(row=0, column=3, padx=4, pady=4, sticky="ew")
    ctk.CTkButton(controls, text="RESET DEFAULT", fg_color="#333333", hover_color="#444444", command=app.template_reset_default).grid(row=0, column=4, padx=4, pady=4, sticky="ew")
    ctk.CTkButton(
        controls,
        text="SET BACKGROUND FROM LIBRARY",
        fg_color="#333333",
        hover_color="#444444",
        command=app.template_set_background_from_selected
    ).grid(row=1, column=0, padx=4, pady=4, sticky="ew")
    ctk.CTkButton(
        controls,
        text="BACKGROUND AUS DATEI",
        fg_color="#333333",
        hover_color="#444444",
        command=app.template_choose_background_file
    ).grid(row=1, column=1, padx=4, pady=4, sticky="ew")
    ctk.CTkButton(
        controls,
        text="CLEAR BACKGROUND",
        fg_color="#333333",
        hover_color="#444444",
        command=app.template_clear_background
    ).grid(row=1, column=2, columnspan=2, padx=4, pady=4, sticky="ew")


    layers = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    layers.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
    layers.grid_columnconfigure(0, weight=1)
    layers.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(
        layers,
        text="LAYERS",
        text_color=GOLD,
        font=ctk.CTkFont(size=18, weight="bold")
    ).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

    app.template_layers_body = ctk.CTkScrollableFrame(layers, fg_color="#0B0B0B", corner_radius=12)
    app.template_layers_body.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

    props = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    props.grid(row=0, column=3, sticky="nsew", padx=(12, 0))
    props.grid_columnconfigure(0, weight=1)
    props.grid_rowconfigure(1, weight=2)
    props.grid_rowconfigure(3, weight=1)

    ctk.CTkLabel(
        props,
        text="Properties",
        text_color=GOLD,
        font=ctk.CTkFont(size=18, weight="bold")
    ).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

    app.template_props_body = ctk.CTkFrame(props, fg_color="#0B0B0B", corner_radius=12)
    app.template_props_body.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 10))
    app.template_props_body.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        props,
        text="Style Presets",
        text_color=GOLD,
        font=ctk.CTkFont(size=16, weight="bold")
    ).grid(row=2, column=0, padx=18, pady=(0, 6), sticky="w")

    style_box = ctk.CTkFrame(props, fg_color="#0B0B0B", corner_radius=12)
    style_box.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 18))
    style_box.grid_columnconfigure(0, weight=1)
    style_box.grid_rowconfigure(1, weight=1)

    ctk.CTkButton(
        style_box,
        text="+ SAVE STYLE",
        fg_color=GOLD,
        text_color="#111111",
        hover_color=GOLD_DARK,
        command=app.template_save_style_preset
    ).grid(row=0, column=0, padx=10, pady=(10, 8), sticky="ew")

    app.template_styles_body = ctk.CTkScrollableFrame(style_box, fg_color="#080808", corner_radius=10)
    app.template_styles_body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    app.template_build_properties_panel()
    app.template_ensure_field_ids()


    zoom_bar = ctk.CTkFrame(controls, fg_color="transparent")
    zoom_bar.grid(row=2, column=0, columnspan=5, padx=4, pady=(8, 0), sticky="ew")
    zoom_bar.grid_columnconfigure(1, weight=1)
    ctk.CTkButton(zoom_bar, text="ZOOM -", fg_color="#333333", hover_color="#444444", command=app.template_zoom_out).grid(row=0, column=0, padx=(0, 4), sticky="ew")
    ctk.CTkLabel(zoom_bar, textvariable=app.template_zoom_label_var, text_color=GOLD, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1, padx=4, sticky="ew")
    ctk.CTkButton(zoom_bar, text="ZOOM +", fg_color="#333333", hover_color="#444444", command=app.template_zoom_in).grid(row=0, column=2, padx=4, sticky="ew")
    ctk.CTkButton(zoom_bar, text="100%", fg_color="#333333", hover_color="#444444", command=app.template_zoom_reset).grid(row=0, column=3, padx=4, sticky="ew")
    ctk.CTkButton(zoom_bar, text="PAN RESET", fg_color="#333333", hover_color="#444444", command=app.template_pan_reset).grid(row=0, column=4, padx=(4, 0), sticky="ew")

    smart_bar = ctk.CTkFrame(controls, fg_color="transparent")
    smart_bar.grid(row=3, column=0, columnspan=5, padx=4, pady=(6, 0), sticky="ew")
    smart_bar.grid_columnconfigure(2, weight=1)

    ctk.CTkCheckBox(
        smart_bar,
        text="SMART GUIDES",
        variable=app.template_smart_guides_enabled,
        command=app.template_smart_guides_changed,
        text_color="#BCA870",
        fg_color=GOLD,
        hover_color=GOLD_DARK
    ).grid(row=0, column=0, padx=(0, 12), sticky="w")

    ctk.CTkCheckBox(
        smart_bar,
        text="SMART SNAP",
        variable=app.template_smart_snap_enabled,
        command=app.template_smart_guides_changed,
        text_color="#BCA870",
        fg_color=GOLD,
        hover_color=GOLD_DARK
    ).grid(row=0, column=1, padx=(0, 12), sticky="w")

    app.template_selection_summary_label = ctk.CTkLabel(
        smart_bar, text="Keine Felder ausgewählt", text_color="#8F8058",
        anchor="e",
    )
    app.template_selection_summary_label.grid(row=0, column=2, sticky="e")

    align_bar = ctk.CTkFrame(controls, fg_color="transparent")
    align_bar.grid(row=4, column=0, columnspan=5, padx=4, pady=(6, 0), sticky="ew")
    align_bar.grid_columnconfigure((0,1,2,3,4,5), weight=1)

    app.template_action_buttons["align"] = []
    for column, (text, mode) in enumerate((("ALIGN LEFT", "left"), ("CENTER", "center"), ("ALIGN RIGHT", "right"), ("ALIGN TOP", "top"), ("MIDDLE", "middle"), ("ALIGN BOTTOM", "bottom"))):
        button = ctk.CTkButton(align_bar, text=text, fg_color="#333333", hover_color="#444444", command=lambda selected=mode: app.template_align_selected(selected))
        button.grid(row=0, column=column, padx=2, pady=2, sticky="ew")
        app.template_action_buttons["align"].append(button)

    distribute_bar = ctk.CTkFrame(controls, fg_color="transparent")
    distribute_bar.grid(row=5, column=0, columnspan=5, padx=4, pady=(2, 0), sticky="ew")
    distribute_bar.grid_columnconfigure((0,1), weight=1)
    app.template_action_buttons["distribute"] = []
    for column, (text, axis) in enumerate((("DISTRIBUTE H", "horizontal"), ("DISTRIBUTE V", "vertical"))):
        button = ctk.CTkButton(distribute_bar, text=text, fg_color="#333333", hover_color="#444444", command=lambda selected=axis: app.template_distribute_selected(selected))
        button.grid(row=0, column=column, padx=2, pady=2, sticky="ew")
        app.template_action_buttons["distribute"].append(button)

    equal_bar = ctk.CTkFrame(controls, fg_color="transparent")
    equal_bar.grid(row=6, column=0, columnspan=5, padx=4, pady=(2, 0), sticky="ew")
    equal_bar.grid_columnconfigure((0,1), weight=1)
    app.template_action_buttons["equal_spacing"] = []
    for column, (text, axis) in enumerate((("EQUAL SPACE H", "horizontal"), ("EQUAL SPACE V", "vertical"))):
        button = ctk.CTkButton(equal_bar, text=text, fg_color="#333333", hover_color="#444444", command=lambda selected=axis: app.template_equal_spacing_selected(selected))
        button.grid(row=0, column=column, padx=2, pady=2, sticky="ew")
        app.template_action_buttons["equal_spacing"].append(button)

    history_bar = ctk.CTkFrame(controls, fg_color="transparent")
    history_bar.grid(row=7, column=0, columnspan=5, padx=4, pady=(2, 0), sticky="ew")
    history_bar.grid_columnconfigure((0,1), weight=1)
    app.template_action_buttons["undo"] = ctk.CTkButton(history_bar, text="UNDO", fg_color="#333333", hover_color="#444444", command=app.template_undo)
    app.template_action_buttons["undo"].grid(row=0, column=0, padx=2, pady=2, sticky="ew")
    app.template_action_buttons["redo"] = ctk.CTkButton(history_bar, text="REDO", fg_color="#333333", hover_color="#444444", command=app.template_redo)
    app.template_action_buttons["redo"].grid(row=0, column=1, padx=2, pady=2, sticky="ew")

    group_bar = ctk.CTkFrame(controls, fg_color="transparent")
    group_bar.grid(row=8, column=0, columnspan=5, padx=4, pady=(2, 0), sticky="ew")
    group_bar.grid_columnconfigure((0,1), weight=1)
    app.template_action_buttons["group"] = ctk.CTkButton(group_bar, text="GROUP SELECTED", fg_color="#333333", hover_color="#444444", command=app.template_create_group)
    app.template_action_buttons["group"].grid(row=0, column=0, padx=2, pady=2, sticky="ew")
    app.template_action_buttons["ungroup"] = ctk.CTkButton(group_bar, text="UNGROUP", fg_color="#333333", hover_color="#444444", command=app.template_ungroup_selected)
    app.template_action_buttons["ungroup"].grid(row=0, column=1, padx=2, pady=2, sticky="ew")

    app.template_draw_canvas()
    app.template_build_style_presets_panel()
    app.template_build_layers_panel()
    app.template_refresh_toolbar_state()
