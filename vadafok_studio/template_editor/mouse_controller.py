"""Mouse interaction for the Template Editor canvas."""

from __future__ import annotations

from typing import Any

from ..core.template_store import save_template

def handle_points(app: Any, x1, y1, x2, y2):
    return [
        ("nw", x1, y1),
        ("n", (x1+x2)//2, y1),
        ("ne", x2, y1),
        ("w", x1, (y1+y2)//2),
        ("e", x2, (y1+y2)//2),
        ("sw", x1, y2),
        ("s", (x1+x2)//2, y2),
        ("se", x2, y2),
    ]


def hit_test(app: Any, x, y):
    template = app.template_current()
    tol = 10

    # selected field handles first
    if app.template_selected_field is not None and 0 <= app.template_selected_field < len(template["fields"]):
        f = template["fields"][app.template_selected_field]
        x1, y1, x2, y2 = app.template_field_screen_rect(f)
        for name, hx, hy in app.template_handle_points(x1, y1, x2, y2):
            if abs(x - hx) <= tol and abs(y - hy) <= tol:
                return app.template_selected_field, name

        near_left = abs(x - x1) <= tol and y1 <= y <= y2
        near_right = abs(x - x2) <= tol and y1 <= y <= y2
        near_top = abs(y - y1) <= tol and x1 <= x <= x2
        near_bottom = abs(y - y2) <= tol and x1 <= x <= x2
        if near_left:
            return app.template_selected_field, "w"
        if near_right:
            return app.template_selected_field, "e"
        if near_top:
            return app.template_selected_field, "n"
        if near_bottom:
            return app.template_selected_field, "s"

    # any field body
    for idx in reversed(range(len(template["fields"]))):
        f = template["fields"][idx]
        if f.get("hidden", False):
            continue
        x1, y1, x2, y2 = app.template_field_screen_rect(f)
        if x1 <= x <= x2 and y1 <= y <= y2:
            return idx, "move"
    return None, None


def cursor_for_mode(app: Any, mode):
    if mode == "move":
        return "fleur"
    if mode in ("nw", "se"):
        return "size_nw_se"
    if mode in ("ne", "sw"):
        return "size_ne_sw"
    if mode in ("n", "s"):
        return "sb_v_double_arrow"
    if mode in ("e", "w"):
        return "sb_h_double_arrow"
    return "crosshair"


def mouse_motion(app: Any, event):
    _idx, mode = app.template_hit_test(event.x, event.y)
    app.template_canvas.configure(cursor=app.template_cursor_for_mode(mode))


def mouse_down(app: Any, event):
    try:
        app.template_canvas.focus_set()
    except Exception:
        pass
    idx, mode = app.template_hit_test(event.x, event.y)
    multi_pressed = app.template_multi_select_modifier(event)

    if idx is None:
        # Empty canvas drag starts marquee selection.
        # Plain drag replaces selection. Ctrl/Cmd-like modifier drag adds to selection.
        app.template_marquee_start_select(event, add_mode=multi_pressed)
        return

    selected = set(getattr(app, "template_selected_fields", set()))

    if multi_pressed:
        # Ctrl/Shift + click toggles membership.
        app.template_toggle_selection(idx)
    else:
        # Important group-drag behavior:
        # If multiple fields are already selected and the user clicks one of them,
        # keep the whole selection. This allows dragging the group.
        if idx in selected and len(selected) > 1:
            app.template_selected_field = idx
        else:
            app.template_set_single_selection(idx)

    app.template_refresh_selection_ui()

    if app.template_is_field_locked(idx):
        app.template_drag_mode = None
        app.template_drag_start = None
        app.template_drag_original = None
        app.template_group_drag_originals = None
        return

    app.template_drag_history_snapshot = app.template_snapshot()
    app.template_drag_mode = mode
    app.template_drag_start = (event.x, event.y)
    template = app.template_current()
    app.template_drag_original = dict(template["fields"][idx])

    selected = set(getattr(app, "template_selected_fields", set()))
    if idx in selected and len(selected) > 1 and mode == "move":
        app.template_group_drag_originals = {
            i: dict(template["fields"][i])
            for i in selected
            if 0 <= i < len(template.get("fields", [])) and not app.template_is_field_locked(i)
        }
        if not app.template_group_drag_originals:
            app.template_group_drag_originals = None
    else:
        app.template_group_drag_originals = None

    app.template_update_fields_overlay()


def mouse_drag(app: Any, event):
    if app.template_marquee_drag(event):
        return
    if app.template_selected_field is None or app.template_drag_original is None:
        return

    template = app.template_current()
    sx, sy = app.template_drag_start
    dx = int((event.x - sx) / app.template_canvas_scale)
    dy = int((event.y - sy) / app.template_canvas_scale)

    # Group move: if multiple fields are selected and one selected field is dragged,
    # move all selected fields together. Resizing remains single-field for now.
    group_originals = getattr(app, "template_group_drag_originals", None)
    if group_originals and (app.template_drag_mode or "move") == "move":
        design_w, design_h = getattr(app, "template_canvas_design_size", (1280, 720))

        # Keep the entire group inside the template bounds.
        min_dx = max(-int(f.get("x", 0)) for f in group_originals.values())
        min_dy = max(-int(f.get("y", 0)) for f in group_originals.values())
        max_dx = min(design_w - (int(f.get("x", 0)) + int(f.get("width", 0))) for f in group_originals.values())
        max_dy = min(design_h - (int(f.get("y", 0)) + int(f.get("height", 0))) for f in group_originals.values())
        dx = max(min_dx, min(max_dx, dx))
        dy = max(min_dy, min(max_dy, dy))

        template = app.template_current()
        for idx, original in group_originals.items():
            f = dict(original)
            f["x"] = int(f.get("x", 0)) + dx
            f["y"] = int(f.get("y", 0)) + dy
            template["fields"][idx] = f

        app.template_update_fields_overlay(
            refresh_layers=False,
            refresh_status=False,
        )
        return

    f = dict(app.template_drag_original)
    x, y, w, h = f["x"], f["y"], f["width"], f["height"]
    mode = app.template_drag_mode or "move"

    if mode == "move":
        x += dx
        y += dy
    else:
        if "w" in mode:
            x += dx
            w -= dx
        if "e" in mode:
            w += dx
        if "n" in mode:
            y += dy
            h -= dy
        if "s" in mode:
            h += dy

    if w < 0:
        x += w
        w = abs(w)
    if h < 0:
        y += h
        h = abs(h)

    min_w, min_h = 40, 30
    design_w, design_h = getattr(app, "template_canvas_design_size", (1280, 720))
    x = max(0, min(design_w - min_w, x))
    y = max(0, min(design_h - min_h, y))
    w = max(min_w, min(design_w - x, w))
    h = max(min_h, min(design_h - y, h))

    # Smart Guides / Smart Snap before final constraints.
    x, y, w, h, guides_x, guides_y = app.template_apply_smart_snap(x, y, w, h, mode)

    min_w, min_h = 40, 30
    design_w, design_h = getattr(app, "template_canvas_design_size", (1280, 720))
    x = max(0, min(design_w - min_w, x))
    y = max(0, min(design_h - min_h, y))
    w = max(min_w, min(design_w - x, w))
    h = max(min_h, min(design_h - y, h))

    f["x"], f["y"], f["width"], f["height"] = int(x), int(y), int(w), int(h)
    template["fields"][app.template_selected_field] = f
    app.template_update_fields_overlay(
        refresh_layers=False,
        refresh_status=False,
    )
    app.template_draw_smart_guides(guides_x, guides_y)


def mouse_up(app: Any, event):
    if app.template_marquee_finish(event):
        return
    app.template_clear_smart_guides()
    if getattr(app, "template_drag_history_snapshot", None) is not None:
        current = app.template_current()
        if current != app.template_drag_history_snapshot:
            app.template_undo_stack.append(app.template_drag_history_snapshot)
            limit = int(getattr(app, "template_history_limit", 80))
            if len(app.template_undo_stack) > limit:
                app.template_undo_stack = app.template_undo_stack[-limit:]
            app.template_redo_stack.clear()
        app.template_drag_history_snapshot = None
    save_template(app.template_selected_name, app.template_current())
    app.template_update_fields_overlay(refresh_layers=False)
    app.template_drag_mode = None
    app.template_drag_start = None
    app.template_drag_original = None
    app.template_group_drag_originals = None
