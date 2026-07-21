"""OBS Workflow page construction."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from ..core import obs_workflow

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
DARK = "#090909"
PANEL = "#111111"
TEXT = "#F2E2B6"


def render_sources_list(app: Any, sources_list: Any) -> None:
    """Render the current scene sources without rebuilding the dashboard."""
    for child in sources_list.winfo_children():
        child.destroy()
    app.obs_source_row_widgets = {}
    state = app.obs_workflow_state
    for idx, source in enumerate(state.sources or ["No source cache yet"]):
        if isinstance(source, dict):
            source_name = source.get("name", "")
            enabled = bool(source.get("enabled", False))
            row_frame = ctk.CTkFrame(sources_list, fg_color="#0B0B0B", corner_radius=8)
            row_frame.grid(row=idx, column=0, padx=6, pady=3, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=1)
            source_label = ctk.CTkLabel(
                row_frame, text=("✓ " if enabled else "✗ ") + source_name,
                text_color="#8FE6A0" if enabled else "#F08A8A", anchor="w",
            )
            source_label.grid(row=0, column=0, padx=10, pady=6, sticky="ew")
            show_btn = ctk.CTkButton(
                row_frame, text="SHOW", width=64,
                fg_color=GOLD if not enabled else "#333333",
                text_color="#111111" if not enabled else "#AAAAAA",
                hover_color=GOLD_DARK,
                command=lambda name=source_name: app.obs_workflow_set_source_visibility(name, True),
            )
            show_btn.grid(row=0, column=1, padx=(4, 4), pady=6)
            hide_btn = ctk.CTkButton(
                row_frame, text="HIDE", width=64,
                fg_color="#5A1F1F" if enabled else "#333333",
                text_color="#FFFFFF" if enabled else "#AAAAAA",
                hover_color="#7A2A2A",
                command=lambda name=source_name: app.obs_workflow_set_source_visibility(name, False),
            )
            hide_btn.grid(row=0, column=2, padx=(4, 8), pady=6)
            app.obs_source_row_widgets[source_name] = {
                "label": source_label, "show_btn": show_btn, "hide_btn": hide_btn,
            }
        else:
            ctk.CTkLabel(
                sources_list, text=str(source), text_color=TEXT, anchor="w",
            ).grid(row=idx, column=0, padx=10, pady=5, sticky="ew")


def show_obs_workflow_page(app: Any) -> None:
    """Build and display the OBS Workflow workspace."""
    app.set_active("OBS Workflow")
    app.clear_main()
    app.page_title("OBS Workflow Dashboard")

    if not hasattr(app, "obs_workflow_state"):
        app.obs_workflow_state = obs_workflow.OBSWorkflowState()

    state = app.obs_workflow_state
    connected = app.obs_workflow_is_connected()
    if hasattr(state, "set_connected"):
        state.set_connected(connected)
    else:
        state.connected = connected

    try:
        app.obs_workflow_load_scene_favorites()
    except Exception:
        pass

    outer = ctk.CTkFrame(app.main, fg_color=DARK)
    outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
    outer.grid_columnconfigure(0, weight=2)
    outer.grid_columnconfigure(1, weight=3)
    outer.grid_rowconfigure(2, weight=0)
    outer.grid_rowconfigure(3, weight=1)

    top = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 14))
    top.grid_columnconfigure((0, 1, 2, 3), weight=1)

    current_scene = getattr(state, "current_scene", "") or "Unknown"
    try:
        app.obs_workflow_current_scene_var.set(current_scene)
        last_switch = getattr(state, "last_scene_switch", "") or "-"
        last_time = getattr(state, "last_scene_switch_time", "") or ""
        app.obs_workflow_last_switch_var.set(last_switch + (f"  {last_time}" if last_time else ""))
    except Exception:
        pass

    cards = [
        ("OBS", "CONNECTED" if connected else "DISCONNECTED", "#8FE6A0" if connected else "#F08A8A"),
        ("Current Scene", current_scene, GOLD),
        ("Connected Since", getattr(state, "connected_since", "") or "-", "#BCA870"),
        ("Last Switch", (getattr(state, "last_scene_switch", "") or "-") + (f"  {getattr(state, 'last_scene_switch_time', '')}" if getattr(state, "last_scene_switch_time", "") else ""), "#BCA870"),
    ]

    for col, (title, value, color) in enumerate(cards):
        card = ctk.CTkFrame(top, fg_color="#0B0B0B", corner_radius=14)
        card.grid(row=0, column=col, sticky="ew", padx=8, pady=14)
        ctk.CTkLabel(card, text=title, text_color="#888888").pack(anchor="w", padx=14, pady=(10, 2))
        if title == "Current Scene":
            ctk.CTkLabel(
                card,
                textvariable=app.obs_workflow_current_scene_var,
                text_color=color,
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(anchor="w", padx=14, pady=(0, 12))
        elif title == "Last Switch":
            ctk.CTkLabel(
                card,
                textvariable=app.obs_workflow_last_switch_var,
                text_color=color,
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(anchor="w", padx=14, pady=(0, 12))
        else:
            ctk.CTkLabel(
                card,
                text=value,
                text_color=color,
                font=ctk.CTkFont(size=18, weight="bold")
            ).pack(anchor="w", padx=14, pady=(0, 12))

    buttons = ctk.CTkFrame(top, fg_color="transparent")
    buttons.grid(row=1, column=0, columnspan=4, sticky="e", padx=10, pady=(0, 12))
    ctk.CTkButton(buttons, text="CONNECT", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=app.obs_workflow_connect).pack(side="left", padx=4)
    ctk.CTkButton(buttons, text="RECONNECT", fg_color="#333333", hover_color="#444444", command=app.obs_workflow_connect).pack(side="left", padx=4)
    ctk.CTkButton(buttons, text="DISCONNECT", fg_color="#5A1F1F", hover_color="#7A2A2A", command=app.obs_workflow_disconnect).pack(side="left", padx=4)
    ctk.CTkButton(buttons, text="REFRESH", fg_color="#333333", hover_color="#444444", command=app.obs_workflow_refresh).pack(side="left", padx=4)
    ctk.CTkButton(buttons, text="DIRECTOR", fg_color="#333333", hover_color="#444444", command=app.show_silent_director_page).pack(side="left", padx=4)

    fav_box = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    fav_box.grid(row=1, column=0, sticky="ew", padx=(0, 7), pady=(0, 14))
    fav_box.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(fav_box, text="Quick Scene Favorites", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 8))
    fav_area = ctk.CTkFrame(fav_box, fg_color="transparent")
    fav_area.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 14))
    for column in range(3):
        fav_area.grid_columnconfigure(column, weight=1)

    try:
        app.obs_workflow_favorite_buttons = {}
    except Exception:
        pass

    if not getattr(app, "scene_favorites", []):
        ctk.CTkLabel(fav_area, text="No favorites yet. Add scenes below.", text_color="#777777").grid(row=0, column=0, sticky="w")
    else:
        for favorite_index, fav_scene in enumerate(app.scene_favorites):
            fav_button = ctk.CTkButton(
                fav_area, text=f"SCENE  {fav_scene}", height=46,
                fg_color=GOLD if fav_scene == current_scene else "#171717",
                text_color="#111111" if fav_scene == current_scene else "#D9C58C",
                hover_color=GOLD_DARK,
                command=lambda s=fav_scene: app.obs_workflow_switch_scene(s)
            )
            fav_button.grid(
                row=favorite_index // 3, column=favorite_index % 3,
                sticky="ew", padx=4, pady=4,
            )
            try:
                app.obs_workflow_favorite_buttons[fav_scene] = fav_button
            except Exception:
                pass

    health_box = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    health_box.grid(row=1, column=1, sticky="ew", padx=(7, 0), pady=(0, 14))
    health_box.grid_columnconfigure(1, weight=1)
    ready, missing_count, total = app.obs_workflow_health_counts()
    health_text = f"{ready} / {total} Ready" if total else "Not scanned"
    health_color = "#8FE6A0" if total and missing_count == 0 else ("#F0C06A" if total else "#777777")
    ctk.CTkLabel(health_box, text="Overlay Health", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 4))
    ctk.CTkLabel(health_box, text=health_text, text_color=health_color, font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=1, sticky="w", padx=8, pady=(14, 4))
    ctk.CTkLabel(health_box, text=(f"{missing_count} scene(s) need attention" if total else "Run a scan to check overlay coverage."), text_color="#AAAAAA").grid(row=1, column=0, columnspan=2, sticky="w", padx=18, pady=(0, 12))
    ctk.CTkButton(health_box, text="SCAN", width=90, fg_color="#333333", hover_color="#444444", command=app.obs_workflow_scan_overlay_health).grid(row=0, column=2, rowspan=2, sticky="e", padx=18, pady=14)

    installer_box = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    installer_box.grid(row=2, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 14))
    installer_box.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(installer_box, text="Overlay Installer", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=18, pady=(14, 6))
    installer_expanded = bool(getattr(state, "overlay_installer_expanded", False))
    ctk.CTkButton(
        installer_box,
        text="EINKLAPPEN" if installer_expanded else "AUFKLAPPEN",
        width=100, fg_color="#333333", hover_color="#444444",
        command=app.obs_workflow_toggle_installer,
    ).grid(row=0, column=3, sticky="e", padx=18, pady=(10, 6))

    source_values = app.obs_workflow_overlay_installer_source_values()
    current_source = getattr(state, "overlay_installer_source_scene", "") or (current_scene if current_scene in source_values else source_values[0])
    if current_source != "No scenes loaded":
        state.overlay_installer_source_scene = current_source

    installer_source_label = ctk.CTkLabel(installer_box, text="Source Scene", text_color="#888888")
    installer_source_label.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 4))
    source_menu = ctk.CTkOptionMenu(
        installer_box,
        values=source_values,
        command=app.obs_workflow_overlay_installer_set_source,
        fg_color="#333333",
        button_color="#444444",
        button_hover_color="#555555"
    )
    source_menu.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(0, 8))
    try:
        source_menu.set(current_source)
    except Exception:
        pass

    selected = list(getattr(state, "overlay_installer_selected_scenes", []) or [])
    selected_text = f"{len(selected)} selected"
    installer_selected_label = ctk.CTkLabel(installer_box, text=selected_text, text_color="#BCA870")
    installer_selected_label.grid(row=1, column=2, sticky="e", padx=8, pady=(0, 8))

    btn_row = ctk.CTkFrame(installer_box, fg_color="transparent")
    btn_row.grid(row=1, column=3, sticky="e", padx=18, pady=(0, 8))
    ctk.CTkButton(btn_row, text="SELECT MISSING", fg_color="#333333", hover_color="#444444", command=app.obs_workflow_overlay_installer_select_missing).pack(side="left", padx=4)
    ctk.CTkButton(btn_row, text="CLEAR", fg_color="#333333", hover_color="#444444", command=app.obs_workflow_overlay_installer_clear_selection).pack(side="left", padx=4)
    ctk.CTkButton(btn_row, text="INSTALL SELECTED", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=app.obs_workflow_overlay_installer_install_selected).pack(side="left", padx=4)

    target_area = ctk.CTkScrollableFrame(installer_box, fg_color="#0B0B0B", corner_radius=12, height=95)
    target_area.grid(row=2, column=0, columnspan=4, sticky="ew", padx=18, pady=(0, 14))
    target_area.grid_columnconfigure(0, weight=1)

    health_results = getattr(state, "overlay_health", []) or []
    if not health_results:
        ctk.CTkLabel(target_area, text="Run Overlay Health SCAN first. Then use SELECT MISSING.", text_color="#777777").grid(row=0, column=0, padx=10, pady=8, sticky="w")
    else:
        row_i = 0
        for item in health_results:
            scene_name = item.get("scene", "")
            if not scene_name or scene_name == current_source:
                continue
            ok = bool(item.get("ok"))
            is_selected = scene_name in selected
            label = ("[x] " if is_selected else "[ ] ") + scene_name
            label += "  READY" if ok else f"  MISSING {len(item.get('missing', []))}"
            color = "#8FE6A0" if ok else "#F0C06A"
            row = ctk.CTkFrame(target_area, fg_color="#171717" if is_selected else "transparent", corner_radius=8)
            row.grid(row=row_i, column=0, sticky="ew", padx=6, pady=3)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkButton(
                row,
                text=label,
                anchor="w",
                fg_color="transparent",
                hover_color="#2C2C2C",
                text_color=color,
                command=lambda s=scene_name: app.obs_workflow_overlay_installer_toggle_scene(s)
            ).grid(row=0, column=0, sticky="ew", padx=6, pady=4)
            row_i += 1

    if not installer_expanded:
        installer_source_label.grid_remove()
        source_menu.grid_remove()
        installer_selected_label.grid_remove()
        btn_row.grid_remove()
        target_area.grid_remove()

    scenes_box = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    scenes_box.grid(row=3, column=0, sticky="nsew", padx=(0, 7), pady=0)
    scenes_box.grid_columnconfigure(0, weight=1)
    scenes_box.grid_rowconfigure(1, weight=1)
    ctk.CTkLabel(scenes_box, text="Scenes", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
    scenes_list = ctk.CTkScrollableFrame(scenes_box, fg_color="#0B0B0B", corner_radius=12)
    scenes_list.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
    scenes_list.grid_columnconfigure(0, weight=1)

    app.obs_workflow_scene_rows = {}

    for idx, scene in enumerate(state.scenes or ["No scene cache yet"]):
        scene_text = str(scene)
        is_placeholder = scene_text == "No scene cache yet"
        is_current = scene_text == current_scene and not is_placeholder
        is_fav = scene_text in getattr(app, "scene_favorites", [])

        row_frame = ctk.CTkFrame(
            scenes_list,
            fg_color="#171717" if is_current else "transparent",
            corner_radius=8
        )
        row_frame.grid(row=idx, column=0, padx=6, pady=3, sticky="ew")
        row_frame.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            row_frame,
            text=(f"● LIVE  {scene_text}" if is_current else scene_text),
            text_color="#8FE6A0" if is_current else TEXT,
            anchor="w"
        )
        label.grid(row=0, column=0, padx=10, pady=6, sticky="ew")

        if not is_placeholder:
            label.bind("<Double-Button-1>", lambda _e, s=scene_text: app.obs_workflow_switch_scene(s))
            row_frame.bind("<Double-Button-1>", lambda _e, s=scene_text: app.obs_workflow_switch_scene(s))

            favorite_btn = ctk.CTkButton(
                row_frame,
                text="STAR" if is_fav else "ADD",
                width=58,
                fg_color=GOLD if is_fav else "#333333",
                text_color="#111111" if is_fav else "#D9C58C",
                hover_color=GOLD_DARK,
                command=lambda s=scene_text, f=is_fav: app.obs_workflow_remove_scene_favorite(s) if f else app.obs_workflow_add_scene_favorite(s)
            )
            favorite_btn.grid(row=0, column=1, padx=(4, 4), pady=6)

            switch_btn = ctk.CTkButton(
                row_frame,
                text="SWITCH",
                width=80,
                fg_color=GOLD if not is_current else "#333333",
                text_color="#111111" if not is_current else "#AAAAAA",
                hover_color=GOLD_DARK,
                command=lambda s=scene_text: app.obs_workflow_switch_scene(s)
            )
            switch_btn.grid(row=0, column=2, padx=(4, 8), pady=6)

            app.obs_workflow_scene_rows[scene_text] = {
                "row": row_frame,
                "label": label,
                "switch": switch_btn,
            }

    right_box = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    right_box.grid(row=3, column=1, sticky="nsew", padx=(7, 0), pady=0)
    right_box.grid_columnconfigure(0, weight=1)
    right_box.grid_rowconfigure(2, weight=1)
    ctk.CTkLabel(right_box, text="Current Scene Control", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")

    current_health = app.obs_workflow_current_scene_health()
    if current_health:
        scene_health_text = "Overlay Ready" if current_health.get("ok") else f"Overlay Missing: {len(current_health.get('missing', []))}"
        scene_health_color = "#8FE6A0" if current_health.get("ok") else "#F0C06A"
    else:
        scene_health_text = "Overlay Health not scanned"
        scene_health_color = "#777777"

    summary = ctk.CTkFrame(right_box, fg_color="#0B0B0B", corner_radius=12)
    summary.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 10))
    summary.grid_columnconfigure(0, weight=1)

    app.obs_workflow_live_scene_var.set(f"LIVE SCENE  {current_scene}")
    last_switch_label = f"Last Scene Switch: {getattr(state, 'last_scene_switch', '-')}"
    if getattr(state, "last_scene_switch_time", ""):
        last_switch_label += f" at {state.last_scene_switch_time}"
    app.obs_workflow_last_scene_control_var.set(last_switch_label)

    ctk.CTkLabel(
        summary,
        textvariable=app.obs_workflow_live_scene_var,
        text_color="#8FE6A0",
        font=ctk.CTkFont(size=22, weight="bold"),
        anchor="w"
    ).grid(row=0, column=0, padx=12, pady=(10, 2), sticky="ew")

    app.obs_workflow_scene_health_label = ctk.CTkLabel(
        summary,
        text=scene_health_text,
        text_color=scene_health_color,
        anchor="w"
    )
    app.obs_workflow_scene_health_label.grid(row=1, column=0, padx=12, pady=(0, 2), sticky="ew")

    ctk.CTkLabel(
        summary,
        textvariable=app.obs_workflow_last_scene_control_var,
        text_color="#888888",
        anchor="w"
    ).grid(row=2, column=0, padx=12, pady=(0, 10), sticky="ew")

    sources_list = ctk.CTkScrollableFrame(right_box, fg_color="#0B0B0B", corner_radius=12)
    sources_list.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
    sources_list.grid_columnconfigure(0, weight=1)
    app.obs_workflow_sources_list = sources_list
    render_sources_list(app, sources_list)

    bottom = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
    bottom.grid(row=4, column=0, columnspan=2, sticky="ew", padx=0, pady=(14, 0))
    bottom.grid_columnconfigure(0, weight=1)
    last = state.last_command or "No command yet"
    if state.last_command_time:
        last = f"{last}  ({state.last_command_time})"
    ctk.CTkLabel(bottom, text=f"Last Command: {last}", text_color="#BCA870", anchor="w").grid(row=0, column=0, padx=18, pady=(14, 4), sticky="ew")
    activity = "\n".join(app.obs_workflow_recent_activity()) or "No recent activity yet."
    ctk.CTkLabel(bottom, text="Recent Activity", text_color=GOLD, font=ctk.CTkFont(size=14, weight="bold"), anchor="w").grid(row=1, column=0, padx=18, pady=(4, 2), sticky="ew")
    ctk.CTkLabel(bottom, text=activity, text_color="#888888", justify="left", anchor="w").grid(row=2, column=0, padx=18, pady=(0, 14), sticky="ew")
