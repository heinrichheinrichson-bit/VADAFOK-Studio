"""Smart-guide geometry and rendering for the Template Editor."""

from __future__ import annotations

from typing import Any

GOLD = "#D6A43A"

def clear_smart_guides(app: Any):
    if hasattr(app, "template_canvas"):
        try:
            app.template_canvas.delete("template_smart_guide")
        except Exception:
            pass


def screen_line_x(app: Any, x):
    ox, _oy = getattr(app, "template_canvas_offset", (0, 0))
    scale = getattr(app, "template_canvas_scale", 1.0)
    return ox + int(x * scale)


def screen_line_y(app: Any, y):
    _ox, oy = getattr(app, "template_canvas_offset", (0, 0))
    scale = getattr(app, "template_canvas_scale", 1.0)
    return oy + int(y * scale)


def field_edges(app: Any, field):
    x = int(field.get("x", 0))
    y = int(field.get("y", 0))
    w = int(field.get("width", 0))
    h = int(field.get("height", 0))
    return {
        "left": x,
        "center_x": x + w // 2,
        "right": x + w,
        "top": y,
        "center_y": y + h // 2,
        "bottom": y + h,
    }


def smart_targets(app: Any):
    template = app.template_current()
    design_w, design_h = getattr(app, "template_canvas_design_size", (1280, 720))

    targets_x = [
        ("template_left", 0),
        ("template_center_x", design_w // 2),
        ("template_right", design_w),
    ]
    targets_y = [
        ("template_top", 0),
        ("template_center_y", design_h // 2),
        ("template_bottom", design_h),
    ]

    for idx, field in enumerate(template.get("fields", [])):
        if idx == app.template_selected_field or field.get("hidden", False):
            continue
        edges = app.template_field_edges(field)
        targets_x.extend([
            (f"field{idx}_left", edges["left"]),
            (f"field{idx}_center_x", edges["center_x"]),
            (f"field{idx}_right", edges["right"]),
        ])
        targets_y.extend([
            (f"field{idx}_top", edges["top"]),
            (f"field{idx}_center_y", edges["center_y"]),
            (f"field{idx}_bottom", edges["bottom"]),
        ])

    return targets_x, targets_y


def draw_smart_guides(app: Any, guides_x=None, guides_y=None):
    if not hasattr(app, "template_canvas"):
        return
    canvas = app.template_canvas
    canvas.delete("template_smart_guide")

    if not (getattr(app, "template_smart_guides_enabled", None) and app.template_smart_guides_enabled.get()):
        return

    guides_x = guides_x or []
    guides_y = guides_y or []

    design_w, design_h = getattr(app, "template_canvas_design_size", (1280, 720))
    ox, oy = getattr(app, "template_canvas_offset", (0, 0))
    scale = getattr(app, "template_canvas_scale", 1.0)
    x_min = ox
    x_max = ox + int(design_w * scale)
    y_min = oy
    y_max = oy + int(design_h * scale)

    for x in guides_x:
        sx = app.template_screen_line_x(x)
        canvas.create_line(
            sx, y_min, sx, y_max,
            fill=GOLD,
            width=2,
            dash=(6, 4),
            tags=("template_smart_guide",)
        )

    for y in guides_y:
        sy = app.template_screen_line_y(y)
        canvas.create_line(
            x_min, sy, x_max, sy,
            fill=GOLD,
            width=2,
            dash=(6, 4),
            tags=("template_smart_guide",)
        )

    try:
        canvas.tag_raise("template_smart_guide")
    except Exception:
        pass


def apply_smart_snap(app: Any, x, y, w, h, mode):
    """
    Returns x, y, w, h and active guide lines.
    Smart snap uses design coordinates, so it works correctly with zoom and pan.
    """
    snap_enabled = bool(
        getattr(app, "template_smart_snap_enabled", None)
        and app.template_smart_snap_enabled.get()
    )
    guides_enabled = bool(
        getattr(app, "template_smart_guides_enabled", None)
        and app.template_smart_guides_enabled.get()
    )
    if not snap_enabled and not guides_enabled:
        return x, y, w, h, [], []

    tolerance = int(getattr(app, "template_smart_guide_tolerance", 8))
    targets_x, targets_y = app.template_smart_targets()

    moving = (mode or "move") == "move"
    guides_x = []
    guides_y = []

    def nearest_delta(values, targets):
        best = None
        for _name, target in targets:
            for value in values:
                delta = target - value
                if abs(delta) <= tolerance and (best is None or abs(delta) < abs(best[0])):
                    best = (delta, target)
        return best

    if moving:
        edges = {
            "left": x,
            "center_x": x + w // 2,
            "right": x + w,
            "top": y,
            "center_y": y + h // 2,
            "bottom": y + h,
        }

        snap_x = nearest_delta([edges["left"], edges["center_x"], edges["right"]], targets_x)
        if snap_x:
            if snap_enabled:
                x += snap_x[0]
            if guides_enabled:
                guides_x.append(snap_x[1])

        snap_y = nearest_delta([edges["top"], edges["center_y"], edges["bottom"]], targets_y)
        if snap_y:
            if snap_enabled:
                y += snap_y[0]
            if guides_enabled:
                guides_y.append(snap_y[1])

    else:
        # Resize snapping: snap only the actively moved edge(s).
            if "w" in mode:
                snap = nearest_delta([x], targets_x)
                if snap:
                    if snap_enabled:
                        old_right = x + w
                        x = snap[1]
                        w = old_right - x
                    if guides_enabled:
                        guides_x.append(snap[1])
            if "e" in mode:
                snap = nearest_delta([x + w], targets_x)
                if snap:
                    if snap_enabled:
                        w = snap[1] - x
                    if guides_enabled:
                        guides_x.append(snap[1])
            if "n" in mode:
                snap = nearest_delta([y], targets_y)
                if snap:
                    if snap_enabled:
                        old_bottom = y + h
                        y = snap[1]
                        h = old_bottom - y
                    if guides_enabled:
                        guides_y.append(snap[1])
            if "s" in mode:
                snap = nearest_delta([y + h], targets_y)
                if snap:
                    if snap_enabled:
                        h = snap[1] - y
                    if guides_enabled:
                        guides_y.append(snap[1])

    return x, y, w, h, guides_x, guides_y


def smart_guides_changed(app: Any):
    app.template_clear_smart_guides()
