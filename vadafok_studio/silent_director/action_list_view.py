"""Timeline action-list rendering for the Silent Director."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk


TEXT = "#F2E2B6"


def _refresh_stats(app: Any, preset: dict) -> None:
    try:
        actions, seconds = app.silent_director_preset_stats(preset)
        app.silent_director_action_count_label.configure(text=str(actions))
        app.silent_director_duration_label.configure(
            text=app.silent_director_format_duration(seconds),
        )
    except Exception:
        pass


def render_actions_list(app: Any) -> None:
    """Rebuild the selected preset's timeline action cards."""
    frame = getattr(app, "silent_director_actions_frame", None)
    if frame is None:
        return

    for child in frame.winfo_children():
        child.destroy()

    app.silent_director_action_rows = []
    app.director_action_card_widgets = {}
    preset = app.silent_director_get_selected_preset()
    if not preset:
        return
    _refresh_stats(app, preset)

    actions = list(preset.get("actions", []) or [])
    if not actions:
        ctk.CTkLabel(
            frame,
            text="No actions yet. Add one below.",
            text_color="#777777",
        ).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        return

    for index, action in enumerate(actions):
        _render_action_card(app, frame, actions, action, index)

    app.director_set_active_action(
        getattr(app, "director_active_action_index", None)
    )


def refresh_action_cards(app: Any) -> bool:
    """Refresh action data in existing cards without destroying the timeline."""
    preset = app.silent_director_get_selected_preset()
    actions = list(preset.get("actions", []) or []) if preset else []
    if preset:
        _refresh_stats(app, preset)
    widgets_map = getattr(app, "director_action_card_widgets", {}) or {}
    if len(actions) != len(widgets_map):
        render_actions_list(app)
        return False
    for index, action in enumerate(actions):
        widgets = widgets_map.get(index, {})
        style = app.silent_director_timeline_style(str(action.get("type", "") or ""))
        widgets["style"] = dict(style)
        widgets["step_text"] = f"Timeline step {index + 1} of {len(actions)}"
        widgets["card"].configure(fg_color=style["card"], border_color=style["accent"])
        widgets["title"].configure(
            text=f"{index + 1}. {style['title']}", text_color=style["accent"],
        )
        widgets["badge"].configure(
            text=style["badge"], fg_color=style["accent"],
        )
        widgets["detail"].configure(text=app.silent_director_timeline_detail(action))
        widgets["runtime"].configure(text=widgets["step_text"])
    app.director_set_active_action(None)
    return True


def _render_action_card(
    app: Any, frame: Any, actions: list[dict], action: dict, index: int
) -> None:
    action_type = str(action.get("type", "") or "").strip()
    style = app.silent_director_timeline_style(action_type)
    detail = app.silent_director_timeline_detail(action)

    item = ctk.CTkFrame(frame, fg_color="transparent")
    item.grid(row=index, column=0, sticky="ew", padx=0, pady=0)
    item.grid_columnconfigure(1, weight=1)
    rail = ctk.CTkFrame(item, fg_color="transparent", width=54)
    rail.grid(row=0, column=0, sticky="ns", padx=(2, 8), pady=0)
    rail.grid_columnconfigure(0, weight=1)

    badge = ctk.CTkLabel(
        rail,
        text=style["badge"],
        width=38,
        height=38,
        fg_color=style["accent"],
        text_color="#111111",
        corner_radius=19,
        font=ctk.CTkFont(size=11, weight="bold"),
    )
    badge.grid(row=0, column=0, pady=(10, 4))
    if index < len(actions) - 1:
        connector = ctk.CTkFrame(
            rail,
            fg_color=style["accent"],
            width=3,
            height=26,
            corner_radius=1,
        )
        connector.grid(row=1, column=0, pady=(0, 0))
        connector.grid_propagate(False)
        ctk.CTkLabel(
            rail,
            text="▼",
            text_color=style["accent"],
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=2, column=0, pady=(0, 2))

    card = ctk.CTkFrame(
        item,
        fg_color=style["card"],
        corner_radius=12,
        border_color=style["accent"],
        border_width=1,
    )
    card.grid(row=0, column=1, sticky="ew", pady=6)
    card.grid_columnconfigure(1, weight=1)
    app.silent_director_action_rows.append(card)

    drag_handle = ctk.CTkLabel(
        card,
        text="☰\nDRAG",
        width=52,
        text_color=style["accent"],
        fg_color="#101010",
        corner_radius=8,
        cursor="fleur",
        font=ctk.CTkFont(size=11, weight="bold"),
    )
    drag_handle.grid(row=0, column=0, rowspan=3, padx=(8, 6), pady=8, sticky="ns")
    drag_handle.bind(
        "<ButtonPress-1>",
        lambda event, i=index: app.silent_director_drag_start(event, i),
    )

    title_button = ctk.CTkButton(
        card,
        text=f"{index + 1}. {style['title']}",
        anchor="w",
        fg_color="transparent",
        hover_color="#2A2A2A",
        text_color=style["accent"],
        font=ctk.CTkFont(size=15, weight="bold"),
        command=lambda i=index: app.silent_director_edit_action(i),
    )
    title_button.grid(row=0, column=1, padx=(6, 8), pady=(8, 0), sticky="ew")
    detail_label = ctk.CTkLabel(
        card,
        text=detail,
        text_color=TEXT,
        anchor="w",
        justify="left",
        wraplength=470,
        font=ctk.CTkFont(size=13),
    )
    detail_label.grid(row=1, column=1, padx=(12, 8), pady=(2, 2), sticky="ew")

    step_text = f"Timeline step {index + 1} of {len(actions)}"
    runtime_label = ctk.CTkLabel(
        card,
        text=step_text,
        text_color="#7E7E7E",
        anchor="w",
        font=ctk.CTkFont(size=10),
    )
    runtime_label.grid(row=2, column=1, padx=(12, 8), pady=(0, 8), sticky="ew")
    app.director_action_card_widgets[index] = {
        "card": card,
        "title": title_button,
        "badge": badge,
        "detail": detail_label,
        "runtime": runtime_label,
        "style": dict(style),
        "step_text": step_text,
    }

    controls = ctk.CTkFrame(card, fg_color="transparent")
    controls.grid(row=0, column=2, rowspan=3, padx=8, pady=7)
    _render_controls(app, controls, index)


def _render_controls(app: Any, controls: Any, index: int) -> None:
    ctk.CTkButton(
        controls,
        text="EDIT",
        width=54,
        fg_color="#333333",
        hover_color="#444444",
        command=lambda i=index: app.silent_director_edit_action(i),
    ).grid(row=0, column=0, padx=2, pady=2)
    ctk.CTkButton(
        controls,
        text="DUP",
        width=48,
        fg_color="#2D4B3A",
        hover_color="#3B624C",
        command=lambda i=index: app.silent_director_duplicate_action(i),
    ).grid(row=0, column=1, padx=2, pady=2)
    ctk.CTkButton(
        controls,
        text="▲",
        width=36,
        fg_color="#333333",
        hover_color="#444444",
        command=lambda i=index: app.silent_director_move_action(i, -1),
    ).grid(row=0, column=2, padx=2, pady=2)
    ctk.CTkButton(
        controls,
        text="▼",
        width=36,
        fg_color="#333333",
        hover_color="#444444",
        command=lambda i=index: app.silent_director_move_action(i, 1),
    ).grid(row=0, column=3, padx=2, pady=2)
    ctk.CTkButton(
        controls,
        text="DELETE",
        width=68,
        fg_color="#5A1F1F",
        hover_color="#7A2A2A",
        command=lambda i=index: app.silent_director_delete_action(i),
    ).grid(row=1, column=0, columnspan=4, padx=2, pady=2, sticky="ew")
