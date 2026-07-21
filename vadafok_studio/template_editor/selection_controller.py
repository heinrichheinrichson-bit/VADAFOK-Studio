"""Selection and marquee behavior for the Template Editor."""

from __future__ import annotations

from typing import Any

GOLD = "#D6A43A"

def multi_select_modifier(app: Any, event):
    state = int(getattr(event, "state", 0) or 0)

    # Tk modifier masks differ a bit by platform/theme.
    # Common masks:
    # Shift = 0x0001
    # Ctrl  = 0x0004
    # Also use our explicit key state fallback.
    return (
        bool(state & 0x0001)
        or bool(state & 0x0004)
        or bool(getattr(app, "template_shift_down", False))
        or bool(getattr(app, "template_ctrl_down", False))
    )


def sync_selection_set(app: Any):
    if not hasattr(app, "template_selected_fields"):
        app.template_selected_fields = set()
    if app.template_selected_field is None:
        if len(app.template_selected_fields) == 1:
            app.template_selected_field = next(iter(app.template_selected_fields))
        return
    app.template_selected_fields.add(app.template_selected_field)


def selection_count(app: Any):
    if not hasattr(app, "template_selected_fields"):
        app.template_selected_fields = set()
    return len(app.template_selected_fields)


def clear_selection(app: Any):
    app.template_selected_field = None
    app.template_selected_fields = set()


def set_single_selection(app: Any, idx):
    app.template_selected_field = idx
    app.template_selected_fields = {idx} if idx is not None else set()


def toggle_selection(app: Any, idx):
    if not hasattr(app, "template_selected_fields"):
        app.template_selected_fields = set()
    if idx in app.template_selected_fields:
        app.template_selected_fields.remove(idx)
        if app.template_selected_field == idx:
            app.template_selected_field = next(iter(app.template_selected_fields), None)
    else:
        app.template_selected_fields.add(idx)
        app.template_selected_field = idx


def marquee_clear(app: Any):
    if hasattr(app, "template_canvas") and getattr(app, "template_marquee_item", None):
        try:
            app.template_canvas.delete(app.template_marquee_item)
        except Exception:
            pass
    app.template_marquee_item = None


def marquee_start_select(app: Any, event, add_mode=False):
    app.template_marquee_clear()
    app.template_marquee_active = True
    app.template_marquee_start = (event.x, event.y)
    app.template_marquee_add_mode = bool(add_mode)
    app.template_drag_mode = None
    app.template_drag_start = None
    app.template_drag_original = None
    app.template_group_drag_originals = None

    if hasattr(app, "template_canvas"):
        app.template_marquee_item = app.template_canvas.create_rectangle(
            event.x, event.y, event.x, event.y,
            outline=GOLD,
            width=2,
            dash=(6, 4),
            fill="#D6A43A",
            stipple="gray25",
            tags=("template_marquee",)
        )
        try:
            app.template_canvas.tag_raise("template_marquee")
        except Exception:
            pass


def marquee_drag(app: Any, event):
    if not getattr(app, "template_marquee_active", False):
        return False
    if not app.template_marquee_start:
        return True

    x0, y0 = app.template_marquee_start
    x1, y1 = event.x, event.y
    if hasattr(app, "template_canvas") and getattr(app, "template_marquee_item", None):
        app.template_canvas.coords(app.template_marquee_item, x0, y0, x1, y1)
    return True


def marquee_finish(app: Any, event):
    if not getattr(app, "template_marquee_active", False):
        return False

    x0, y0 = app.template_marquee_start or (event.x, event.y)
    x1, y1 = event.x, event.y
    app.template_marquee_active = False

    min_x, max_x = sorted((x0, x1))
    min_y, max_y = sorted((y0, y1))
    moved = abs(max_x - min_x) >= 4 or abs(max_y - min_y) >= 4

    app.template_marquee_clear()

    if not moved:
        if not getattr(app, "template_marquee_add_mode", False):
            app.template_clear_selection()
            app.template_refresh_selection_ui()
        return True

    template = app.template_current()
    found = set()

    for idx, field in enumerate(template.get("fields", [])):
        if field.get("hidden", False):
            continue

        fx1, fy1, fx2, fy2 = app.template_field_screen_rect(field)

        # Select fields whose visible rectangle intersects the marquee rectangle.
        intersects = not (fx2 < min_x or fx1 > max_x or fy2 < min_y or fy1 > max_y)
        if intersects:
            found.add(idx)

    if getattr(app, "template_marquee_add_mode", False):
        selected = set(getattr(app, "template_selected_fields", set()))
        selected.update(found)
        app.template_selected_fields = selected
        if found:
            app.template_selected_field = next(iter(found))
    else:
        app.template_selected_fields = found
        app.template_selected_field = next(iter(found), None)

    app.template_refresh_selection_ui()

    return True
