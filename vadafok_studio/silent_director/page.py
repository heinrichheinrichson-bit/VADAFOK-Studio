"""Silent Director page construction."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk


GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
DARK = "#090909"
PANEL = "#111111"
TEXT = "#F2E2B6"


def refresh_selected_editor(app: Any) -> bool:
    """Update the selected preset editor without rebuilding the whole page."""
    preset = app.silent_director_get_selected_preset()
    if not preset:
        return False
    app.silent_director_load_editor(preset)
    try:
        app.silent_director_banner_textbox.delete("1.0", "end")
        app.silent_director_banner_textbox.insert("1.0", preset.get("banner_text", ""))
    except Exception:
        pass
    actions, seconds = app.silent_director_preset_stats(preset)
    for attr, value in (
        ("silent_director_preset_name_label", preset.get("name", "Untitled")),
        ("silent_director_action_count_label", str(actions)),
        ("silent_director_duration_label", app.silent_director_format_duration(seconds)),
    ):
        try:
            getattr(app, attr).configure(text=value)
        except Exception:
            pass
    app.silent_director_render_actions_list()
    app.silent_director_render_filtered_presets()
    return True


def show_silent_director_page(app: Any) -> None:
    """Build and display the Silent Director workspace."""
    app.set_active("Silent Director")
    app.clear_main()
    app.page_title("Silent Director")

    app.silent_director_reload()

    outer = ctk.CTkFrame(app.main, fg_color=DARK)
    outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    outer.grid_columnconfigure(0, weight=2)
    outer.grid_columnconfigure(1, weight=3)
    outer.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    left.grid_columnconfigure(0, weight=1)
    left.grid_rowconfigure(3, weight=1)

    ctk.CTkLabel(left, text="Director Presets", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

    search_bar = ctk.CTkFrame(left, fg_color="#0B0B0B", corner_radius=12)
    search_bar.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))
    search_bar.grid_columnconfigure(0, weight=1)

    search_entry = ctk.CTkEntry(
        search_bar,
        textvariable=app.silent_director_search_var,
        placeholder_text="Preset suchen..."
    )
    search_entry.grid(row=0, column=0, padx=(10, 6), pady=10, sticky="ew")
    search_entry.bind(
        "<KeyRelease>",
        app.silent_director_render_filtered_presets
    )

    ctk.CTkButton(
        search_bar,
        text="X",
        width=38,
        fg_color="#333333",
        hover_color="#444444",
        command=app.silent_director_clear_search
    ).grid(row=0, column=1, padx=(0, 4), pady=10)

    ctk.CTkButton(
        search_bar,
        text="★ FAVORITES",
        width=108,
        fg_color=GOLD if app.silent_director_favorites_only.get() else "#333333",
        text_color="#111111" if app.silent_director_favorites_only.get() else "#D9C58C",
        hover_color=GOLD_DARK,
        command=app.silent_director_toggle_favorites_filter
    ).grid(row=0, column=2, padx=(0, 10), pady=10)

    create = ctk.CTkFrame(left, fg_color="#0B0B0B", corner_radius=12)
    create.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 10))
    create.grid_columnconfigure(0, weight=1)
    ctk.CTkEntry(create, textvariable=app.silent_director_new_name, placeholder_text="New preset name").grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    ctk.CTkButton(create, text="ADD", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=app.silent_director_create_preset).grid(row=0, column=1, padx=(0, 10), pady=10)

    preset_list = ctk.CTkScrollableFrame(left, fg_color="#0B0B0B", corner_radius=12)
    preset_list.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 18))
    preset_list.grid_columnconfigure(0, weight=1)
    app.silent_director_preset_list_frame = preset_list
    app.silent_director_render_filtered_presets()

    right = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(3, weight=1)

    preset = app.silent_director_get_selected_preset()
    if not preset:
        ctk.CTkLabel(right, text="No preset selected.", text_color="#777777").grid(row=0, column=0, padx=18, pady=18, sticky="w")
        return

    app.silent_director_load_editor(preset)

    ctk.CTkLabel(
        right,
        text="Action Editor",
        text_color=GOLD,
        font=ctk.CTkFont(size=22, weight="bold")
    ).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

    stats_actions, stats_seconds = app.silent_director_preset_stats(preset)

    stats_bar = ctk.CTkFrame(
        right,
        fg_color="#111111",
        corner_radius=12,
        border_color="#2A2110",
        border_width=1
    )
    stats_bar.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
    stats_bar.grid_columnconfigure(1, weight=1)
    stats_bar.grid_columnconfigure(3, weight=1)

    app.silent_director_preset_name_label = ctk.CTkLabel(
        stats_bar,
        text="PRESET",
        text_color="#777777",
        font=ctk.CTkFont(size=11, weight="bold")
    ).grid(row=0, column=0, padx=(12, 6), pady=(9, 2), sticky="w")

    ctk.CTkLabel(
        stats_bar,
        text=str(preset.get("name", "Untitled")),
        text_color=TEXT,
        font=ctk.CTkFont(size=14, weight="bold")
    )
    app.silent_director_preset_name_label.grid(row=1, column=0, padx=(12, 16), pady=(0, 10), sticky="w")

    app.silent_director_action_count_label = ctk.CTkLabel(
        stats_bar,
        text="ACTIONS",
        text_color="#777777",
        font=ctk.CTkFont(size=11, weight="bold")
    ).grid(row=0, column=1, padx=6, pady=(9, 2), sticky="w")

    ctk.CTkLabel(
        stats_bar,
        text=str(stats_actions),
        text_color=GOLD,
        font=ctk.CTkFont(size=16, weight="bold")
    )
    app.silent_director_action_count_label.grid(row=1, column=1, padx=6, pady=(0, 10), sticky="w")

    app.silent_director_duration_label = ctk.CTkLabel(
        stats_bar,
        text="GESAMTDAUER",
        text_color="#777777",
        font=ctk.CTkFont(size=11, weight="bold")
    ).grid(row=0, column=2, padx=6, pady=(9, 2), sticky="w")

    ctk.CTkLabel(
        stats_bar,
        text=app.silent_director_format_duration(stats_seconds),
        text_color="#6EA6E8",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    app.silent_director_duration_label.grid(row=1, column=2, padx=6, pady=(0, 10), sticky="w")

    ctk.CTkLabel(
        stats_bar,
        text="Berechnet aus WAIT-Actions",
        text_color="#666666",
        font=ctk.CTkFont(size=10)
    ).grid(row=1, column=3, padx=(12, 12), pady=(0, 10), sticky="e")

    monitor = ctk.CTkFrame(right, fg_color="#0B0B0B", corner_radius=12)
    monitor.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))
    monitor.grid_columnconfigure(1, weight=1)

    status = app.director_status_var.get() if hasattr(app, "director_status_var") else "READY"
    status_color = "#8FE6A0" if status in ("READY", "FINISHED") else ("#F0C06A" if status in ("RUNNING", "WAITING", "STOPPING") else ("#F08A8A" if status == "ERROR" else "#888888"))

    ctk.CTkLabel(monitor, text="Director Monitor", text_color=GOLD, font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="w")
    ctk.CTkLabel(monitor, text="Status", text_color="#888888").grid(row=1, column=0, padx=12, pady=3, sticky="w")
    app.director_status_label = ctk.CTkLabel(monitor, textvariable=app.director_status_var, text_color=status_color, font=ctk.CTkFont(size=14, weight="bold"))
    app.director_status_label.grid(row=1, column=1, padx=12, pady=3, sticky="w")
    ctk.CTkLabel(monitor, text="Current Action", text_color="#888888").grid(row=2, column=0, padx=12, pady=3, sticky="w")
    ctk.CTkLabel(monitor, textvariable=app.director_current_action_var, text_color=TEXT, wraplength=650, justify="left").grid(row=2, column=1, padx=12, pady=3, sticky="w")
    ctk.CTkLabel(monitor, text="Progress", text_color="#888888").grid(row=3, column=0, padx=12, pady=(3, 10), sticky="w")
    ctk.CTkLabel(monitor, textvariable=app.director_progress_var, text_color="#BCA870").grid(row=3, column=1, padx=12, pady=(3, 10), sticky="w")
    try:
        progress_bar = ctk.CTkProgressBar(monitor, variable=app.director_progress_percent_var, height=12)
        progress_bar.grid(row=6, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 12))
    except Exception:
        pass

    editor = ctk.CTkScrollableFrame(right, fg_color="#0B0B0B", corner_radius=12)
    editor.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 12))
    editor.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(editor, text="Name", text_color="#888888").grid(row=0, column=0, padx=12, pady=(14, 6), sticky="w")
    ctk.CTkEntry(editor, textvariable=app.silent_director_editor_name).grid(row=0, column=1, padx=12, pady=(14, 6), sticky="ew")

    ctk.CTkLabel(
        editor,
        text="Preset Icon",
        text_color="#888888"
    ).grid(row=1, column=0, padx=12, pady=6, sticky="w")

    ctk.CTkOptionMenu(
        editor,
        values=app.silent_director_icon_options(),
        variable=app.silent_director_editor_icon,
        fg_color="#333333",
        button_color="#444444",
        button_hover_color="#555555"
    ).grid(row=1, column=1, padx=12, pady=6, sticky="ew")

    ctk.CTkLabel(
        editor,
        text="AUTO chooses an icon from the preset name.",
        text_color="#666666",
        font=ctk.CTkFont(size=10)
    ).grid(row=2, column=1, padx=12, pady=(0, 4), sticky="w")

    legacy = ctk.CTkFrame(editor, fg_color="#111111", corner_radius=12)
    legacy.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 10))
    legacy.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(
        legacy, text="Legacy-Kompatibilität", text_color="#BCA870",
        font=ctk.CTkFont(size=13, weight="bold"),
    ).grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="w")
    ctk.CTkLabel(
        legacy,
        text="Nur für ältere Presets ohne Action-Liste. Neue Abläufe unten als Actions anlegen.",
        text_color="#666666", font=ctk.CTkFont(size=10),
    ).grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 6), sticky="w")
    ctk.CTkLabel(legacy, text="Legacy Scene", text_color="#888888").grid(row=2, column=0, padx=12, pady=6, sticky="w")
    scene_values = app.silent_director_scene_values()
    ctk.CTkOptionMenu(legacy, values=scene_values, variable=app.silent_director_editor_scene, fg_color="#333333", button_color="#444444", button_hover_color="#555555").grid(row=2, column=1, padx=12, pady=6, sticky="ew")

    ctk.CTkLabel(legacy, text="Legacy Banner", text_color="#888888").grid(row=3, column=0, padx=12, pady=6, sticky="nw")
    app.silent_director_banner_textbox = ctk.CTkTextbox(legacy, height=70, fg_color="#050505", border_color="#6A4A12", border_width=1)
    app.silent_director_banner_textbox.grid(row=3, column=1, padx=12, pady=6, sticky="ew")
    app.silent_director_banner_textbox.insert("1.0", preset.get("banner_text", ""))

    ctk.CTkCheckBox(legacy, text="Show legacy banner", variable=app.silent_director_editor_show_banner, fg_color=GOLD, hover_color=GOLD_DARK).grid(row=4, column=1, padx=12, pady=(4, 12), sticky="w")

    # Action list
    ctk.CTkLabel(
        editor,
        text="Actions",
        text_color=GOLD,
        font=ctk.CTkFont(size=18, weight="bold")
    ).grid(row=4, column=0, columnspan=2, padx=12, pady=(18, 8), sticky="w")

    app.silent_director_actions_frame = ctk.CTkFrame(
        editor,
        fg_color="transparent"
    )
    app.silent_director_actions_frame.grid(
        row=5, column=0, columnspan=2,
        sticky="ew", padx=12, pady=(0, 6)
    )
    app.silent_director_actions_frame.grid_columnconfigure(0, weight=1)
    app.silent_director_render_actions_list()

    action_row_start = 6

    # Add / Edit action panel
    add_box = ctk.CTkFrame(editor, fg_color="#111111", corner_radius=12)
    add_box.grid(row=action_row_start + 1, column=0, columnspan=2, sticky="ew", padx=12, pady=(16, 12))
    add_box.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        add_box, text="Add / Edit Action", text_color=GOLD,
        font=ctk.CTkFont(size=16, weight="bold")
    ).grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 6), sticky="w")

    ctk.CTkLabel(
        add_box,
        text="DUP erstellt direkt darunter eine bearbeitbare Kopie.",
        text_color="#777777",
        font=ctk.CTkFont(size=11)
    ).grid(row=0, column=1, padx=12, pady=(12, 6), sticky="e")

    ctk.CTkLabel(add_box, text="Type", text_color="#888888").grid(
        row=1, column=0, padx=12, pady=6, sticky="w"
    )

    ctk.CTkOptionMenu(
        add_box,
        values=["switch_scene", "show_banner", "show_source", "hide_source", "wait"],
        variable=app.silent_director_action_type,
        command=app.silent_director_update_action_fields,
        fg_color="#333333",
        button_color="#444444",
        button_hover_color="#555555"
    ).grid(row=1, column=1, padx=12, pady=6, sticky="ew")

    app.silent_director_dynamic_frames = {}

    scene_frame = ctk.CTkFrame(add_box, fg_color="transparent")
    scene_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    scene_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(scene_frame, text="Scene", text_color="#888888").grid(
        row=0, column=0, padx=12, pady=6, sticky="w"
    )
    ctk.CTkOptionMenu(
        scene_frame,
        values=scene_values,
        variable=app.silent_director_action_scene,
        fg_color="#333333",
        button_color="#444444",
        button_hover_color="#555555"
    ).grid(row=0, column=1, padx=12, pady=6, sticky="ew")
    app.silent_director_dynamic_frames["scene"] = scene_frame

    source_frame = ctk.CTkFrame(add_box, fg_color="transparent")
    source_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    source_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(source_frame, text="Source", text_color="#888888").grid(
        row=0, column=0, padx=12, pady=6, sticky="w"
    )
    ctk.CTkOptionMenu(
        source_frame,
        values=app.silent_director_source_values(),
        variable=app.silent_director_action_source,
        fg_color="#333333",
        button_color="#444444",
        button_hover_color="#555555"
    ).grid(row=0, column=1, padx=12, pady=6, sticky="ew")
    app.silent_director_dynamic_frames["source"] = source_frame

    banner_frame = ctk.CTkFrame(add_box, fg_color="transparent")
    banner_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    banner_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(banner_frame, text="Banner Text", text_color="#888888").grid(
        row=0, column=0, padx=12, pady=6, sticky="w"
    )
    ctk.CTkEntry(
        banner_frame,
        textvariable=app.silent_director_action_text,
        placeholder_text="Text for Show Banner action"
    ).grid(row=0, column=1, padx=12, pady=6, sticky="ew")
    app.silent_director_dynamic_frames["banner"] = banner_frame

    wait_frame = ctk.CTkFrame(add_box, fg_color="transparent")
    wait_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    wait_frame.grid_columnconfigure(1, weight=1)
    ctk.CTkLabel(wait_frame, text="Duration (Sekunden)", text_color="#888888").grid(
        row=0, column=0, padx=12, pady=6, sticky="w"
    )
    ctk.CTkEntry(
        wait_frame,
        textvariable=app.silent_director_wait_seconds,
        placeholder_text="5"
    ).grid(row=0, column=1, padx=12, pady=6, sticky="ew")
    app.silent_director_dynamic_frames["wait"] = wait_frame

    button_row = ctk.CTkFrame(add_box, fg_color="transparent")
    button_row.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 14))
    button_row.grid_columnconfigure(0, weight=1)

    ctk.CTkButton(
        button_row,
        textvariable=app.silent_director_action_button_text,
        height=42,
        fg_color=GOLD,
        text_color="#111111",
        hover_color=GOLD_DARK,
        command=app.silent_director_add_action
    ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

    ctk.CTkButton(
        button_row,
        text="CANCEL EDIT",
        height=42,
        fg_color="#333333",
        hover_color="#444444",
        command=app.silent_director_cancel_action_edit
    ).grid(row=0, column=1, padx=(6, 0))

    app.silent_director_update_action_fields()

    log_box = ctk.CTkFrame(right, fg_color="#0B0B0B", corner_radius=12)
    log_box.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 12))
    log_box.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(log_box, text="Director Log", text_color=GOLD, font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")
    try:
        app.director_log_text_var.set("\n".join(getattr(app, "director_log_entries", [])[-10:]) or "No Director run yet.")
    except Exception:
        pass
    ctk.CTkLabel(log_box, textvariable=app.director_log_text_var, text_color="#888888", justify="left", anchor="w", wraplength=760).grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")

    actions_bar = ctk.CTkFrame(right, fg_color="transparent")
    actions_bar.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 18))
    ctk.CTkButton(actions_bar, text="SAVE", height=46, fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=app.silent_director_save_selected).pack(side="left", padx=4)
    ctk.CTkButton(
        actions_bar,
        text="DUPLICATE PRESET",
        height=46,
        fg_color="#2D4B3A",
        hover_color="#3B624C",
        command=lambda: app.silent_director_duplicate_preset()
    ).pack(side="left", padx=4)
    app.director_run_button = ctk.CTkButton(
        actions_bar, text="RUN PRESET", height=46, fg_color="#333333",
        hover_color="#444444", command=lambda: app.silent_director_run_preset(),
        state="disabled" if status in ("RUNNING", "WAITING", "STOPPING") else "normal",
    )
    app.director_run_button.pack(side="left", padx=4)
    app.director_stop_button = ctk.CTkButton(
        actions_bar, text="STOP", height=46, fg_color="#5A1F1F",
        hover_color="#7A2A2A", command=app.director_request_stop,
        state="normal" if status in ("RUNNING", "WAITING", "STOPPING") else "disabled",
    )
    app.director_stop_button.pack(side="left", padx=4)
    ctk.CTkButton(actions_bar, text="DELETE", height=46, fg_color="#5A1F1F", hover_color="#7A2A2A", command=app.silent_director_delete_selected).pack(side="left", padx=4)
