"""Drag-and-drop behavior for Silent Director timeline actions."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

from ..core import silent_director

GOLD = "#D6A43A"

def drag_start(app: Any, event, index):
    """Start drag without rebuilding the timeline."""
    rows = list(getattr(app, "silent_director_action_rows", []) or [])
    if not (0 <= index < len(rows)):
        return "break"

    app.silent_director_drag_index = index
    app.silent_director_drop_index = index
    app.silent_director_drag_target = index
    app.silent_director_drag_active = True
    app.silent_director_dragged_card = rows[index]

    try:
        app.silent_director_dragged_card.configure(
            border_width=3,
            border_color=GOLD
        )
    except Exception:
        pass

    app.silent_director_show_floating_drop_indicator(index)

    try:
        app.bind_all("<B1-Motion>", app.silent_director_drag_motion)
        app.bind_all("<ButtonRelease-1>", app.silent_director_drag_release)
        app.bind_all("<Escape>", lambda _e: app.silent_director_drag_cancel())
    except Exception:
        pass

    return "break"


def drag_target_from_y(app: Any, y_root):
    rows = list(getattr(app, "silent_director_action_rows", []) or [])
    if not rows:
        return None

    for idx, row in enumerate(rows):
        try:
            center = row.winfo_rooty() + (row.winfo_height() / 2)
        except Exception:
            continue
        if y_root < center:
            return idx

    return len(rows)


def show_floating_drop_indicator(app: Any, target_index):
    """Show a separate floating overlay so the timeline never needs redrawing."""
    rows = list(getattr(app, "silent_director_action_rows", []) or [])
    frame = getattr(app, "silent_director_actions_frame", None)
    if not rows or frame is None or target_index is None:
        return

    target_index = max(0, min(len(rows), int(target_index)))

    try:
        frame.update_idletasks()

        x = frame.winfo_rootx() + 12
        width = max(240, frame.winfo_width() - 24)

        if target_index < len(rows):
            y = rows[target_index].winfo_rooty() - 8
        else:
            last = rows[-1]
            y = last.winfo_rooty() + last.winfo_height() + 2

        if app.silent_director_drop_overlay is None:
            overlay = ctk.CTkToplevel(app)
            overlay.overrideredirect(True)
            overlay.attributes("-topmost", True)
            try:
                overlay.attributes("-alpha", 0.97)
            except Exception:
                pass

            body = ctk.CTkFrame(
                overlay,
                fg_color="#111111",
                border_color=GOLD,
                border_width=1,
                corner_radius=7
            )
            body.pack(fill="both", expand=True)

            line = ctk.CTkFrame(
                body,
                fg_color=GOLD,
                height=6,
                corner_radius=3
            )
            line.pack(fill="x", padx=6, pady=(5, 1))
            line.pack_propagate(False)

            label = ctk.CTkLabel(
                body,
                text="",
                text_color=GOLD,
                font=ctk.CTkFont(size=11, weight="bold")
            )
            label.pack(anchor="w", padx=8, pady=(0, 5))

            app.silent_director_drop_overlay = overlay
            app.silent_director_drop_overlay_label = label

        app.silent_director_drop_overlay_label.configure(
            text=f"DROP HERE — POSITION {target_index + 1}"
        )
        app.silent_director_drop_overlay.geometry(
            f"{width}x42+{x}+{max(0, int(y))}"
        )
        app.silent_director_drop_overlay.deiconify()
        app.silent_director_drop_overlay.lift()
    except Exception:
        pass


def hide_floating_drop_indicator(app: Any):
    overlay = getattr(app, "silent_director_drop_overlay", None)
    if overlay is not None:
        try:
            overlay.destroy()
        except Exception:
            pass
    app.silent_director_drop_overlay = None
    app.silent_director_drop_overlay_label = None


def drag_motion(app: Any, event):
    if not app.silent_director_drag_active:
        return "break"

    target = app.silent_director_drag_target_from_y(
        getattr(event, "y_root", 0)
    )
    if target is None:
        return "break"

    if target != app.silent_director_drag_target:
        app.silent_director_drag_target = target
        app.silent_director_drop_index = target
        app.silent_director_show_floating_drop_indicator(target)

    return "break"


def drag_release(app: Any, event=None):
    if not app.silent_director_drag_active:
        return "break"

    source_index = app.silent_director_drag_index
    target_index = app.silent_director_drag_target

    if target_index is None and event is not None:
        target_index = app.silent_director_drag_target_from_y(
            getattr(event, "y_root", 0)
        )

    app.silent_director_drag_active = False
    app.silent_director_drag_index = None
    app.silent_director_drop_index = None
    app.silent_director_drag_target = None

    try:
        app.unbind_all("<B1-Motion>")
        app.unbind_all("<ButtonRelease-1>")
        app.unbind_all("<Escape>")
    except Exception:
        pass

    app.silent_director_hide_floating_drop_indicator()

    try:
        if app.silent_director_dragged_card is not None:
            app.silent_director_dragged_card.configure(border_width=1)
    except Exception:
        pass
    app.silent_director_dragged_card = None

    preset = app.silent_director_get_selected_preset()
    if preset and source_index is not None and target_index is not None:
        app.silent_director_presets = silent_director.move_action_to(
            preset.get("name", ""),
            source_index,
            target_index,
        )
        app.silent_director_edit_index = None
        app.silent_director_action_button_text.set("+ ADD ACTION")
        app.obs_workflow_mark_command(
            "Silent Director action reordered by drag and drop"
        )

    # Exactly one rebuild after release.
    app.silent_director_render_actions_list()
    return "break"


def drag_cancel(app: Any):
    app.silent_director_drag_active = False
    app.silent_director_drag_index = None
    app.silent_director_drop_index = None
    app.silent_director_drag_target = None

    try:
        app.unbind_all("<B1-Motion>")
        app.unbind_all("<ButtonRelease-1>")
        app.unbind_all("<Escape>")
    except Exception:
        pass

    app.silent_director_hide_floating_drop_indicator()

    try:
        if app.silent_director_dragged_card is not None:
            app.silent_director_dragged_card.configure(border_width=1)
    except Exception:
        pass
    app.silent_director_dragged_card = None
    return "break"
