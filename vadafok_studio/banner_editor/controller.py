"""Banner Editor behavior controller.

The controller owns the existing Banner Editor profile, canvas, overlay, and
mouse interaction logic. UI widgets and runtime state remain on the app
instance so this refactor does not alter behavior.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from PIL import Image

from ..core.banner_profiles import (
    ensure_profile,
    reset_profile_style,
    save_banner_profiles,
)
from ..core.layout_engine import (
    apply_layout_field_to_banner_profile,
    banner_profile_to_layout_field,
)

GOLD = "#D6A43A"


class BannerEditorController:
    """Coordinate Banner Editor state and interactions for one app instance."""

    def __init__(self, app):
        self.app = app

    def editor_select_banner(self, item):
        app = self.app
        app.editor_selected_banner = item
        profile = ensure_profile(app.banner_profiles, item.relative)
        self.editor_load_profile_values(profile)
        if not profile["text_area"]["width"] or not profile["text_area"]["height"]:
            try:
                img = Image.open(item.path).convert("RGBA")
                w, h = img.size
                profile["text_area"] = {"x": int(w * 0.12), "y": int(h * 0.24), "width": int(w * 0.76), "height": int(h * 0.52)}
                save_banner_profiles(app.banner_profiles)
            except Exception:
                pass
        self.editor_draw_canvas()


    def editor_profile(self):
        app = self.app
        if not app.editor_selected_banner:
            return None
        return ensure_profile(app.banner_profiles, app.editor_selected_banner.relative)



    def editor_load_profile_values(self, profile):
        app = self.app
        app.editor_font_family.set(profile.get("font_family", app.caption_font_family.get()))
        app.editor_font_size.set(int(profile.get("font_size", app.caption_font_size.get())))
        app.editor_text_color.set(profile.get("text_color", app.caption_text_color.get()))
        app.editor_stroke_color.set(profile.get("stroke_color", app.caption_stroke_color.get()))
        app.editor_stroke_width.set(int(profile.get("stroke_width", app.caption_stroke_width.get())))
        app.editor_uppercase.set(bool(profile.get("uppercase", app.caption_uppercase.get())))


    def editor_apply_profile_values(self):
        app = self.app
        profile = self.editor_profile()
        if not profile:
            return
        try:
            profile["font_family"] = app.editor_font_family.get()
            profile["font_size"] = int(app.editor_font_size.get())
            profile["text_color"] = app.editor_text_color.get()
            profile["stroke_color"] = app.editor_stroke_color.get()
            profile["stroke_width"] = int(app.editor_stroke_width.get())
            profile["uppercase"] = bool(app.editor_uppercase.get())
            save_banner_profiles(app.banner_profiles)
            self.editor_update_overlay()
        except Exception:
            pass


    def editor_save_profile(self):
        app = self.app
        if not app.editor_selected_banner:
            messagebox.showwarning("Banner Editor", "Bitte zuerst ein Banner auswählen.")
            return
        self.editor_apply_profile_values()
        profile = self.editor_profile()
        if profile:
            field = banner_profile_to_layout_field(profile)
            apply_layout_field_to_banner_profile(profile, field)
        save_banner_profiles(app.banner_profiles)
        messagebox.showinfo("Banner Editor", f"Profil gespeichert:\n{app.editor_selected_banner.name}")
        app.show_banner_profiles_page()



    def editor_reset_style(self):
        app = self.app
        if not app.editor_selected_banner:
            return
        profile = self.editor_profile()
        reset_profile_style(profile)
        self.editor_load_profile_values(profile)
        save_banner_profiles(app.banner_profiles)
        self.editor_update_overlay()
        messagebox.showinfo("Banner Editor", "Profilwerte wurden auf Standard zurückgesetzt.")


    def editor_reset_area(self):
        app = self.app
        if not app.editor_selected_banner:
            return
        profile = self.editor_profile()
        img = Image.open(app.editor_selected_banner.path).convert("RGBA")
        w, h = img.size
        profile["text_area"] = {"x": int(w * 0.12), "y": int(h * 0.24), "width": int(w * 0.76), "height": int(h * 0.52)}
        save_banner_profiles(app.banner_profiles)
        self.editor_draw_canvas()



    def editor_draw_canvas(self, full_redraw=True):
        """
        Anti-flicker drawing:
        - full_redraw=True loads/scales the banner once.
        - full_redraw=False updates only overlay rectangle, handles, and sample text.
        """
        app = self.app
        if not hasattr(app, "editor_canvas") or not app.editor_selected_banner:
            return

        if full_redraw or app.editor_banner_image_id is None:
            self.editor_redraw_banner()
        self.editor_update_overlay()


    def editor_redraw_banner(self):
        app = self.app
        canvas = app.editor_canvas
        canvas.delete("all")
        app.editor_handle_ids = []
        app.editor_area_rect_id = None
        app.editor_sample_text_id = None

        banner = Image.open(app.editor_selected_banner.path).convert("RGBA")
        bw, bh = banner.size
        app.editor_canvas_banner_size = (bw, bh)

        canvas.update_idletasks()
        cw = max(400, canvas.winfo_width())
        ch = max(260, canvas.winfo_height())
        scale = min((cw - 30) / bw, (ch - 30) / bh)
        app.editor_canvas_scale = scale

        display_w = int(bw * scale)
        display_h = int(bh * scale)
        offset_x = (cw - display_w) // 2
        offset_y = (ch - display_h) // 2
        app.editor_canvas_offset = (offset_x, offset_y)

        display = banner.resize((display_w, display_h))
        app.editor_canvas_photo = tk.PhotoImage(data=self._pil_to_png_bytes(display))
        app.editor_banner_image_id = canvas.create_image(
            offset_x,
            offset_y,
            image=app.editor_canvas_photo,
            anchor="nw",
            tags="banner"
        )


    def editor_update_overlay(self):
        app = self.app
        canvas = app.editor_canvas
        if not app.editor_selected_banner:
            return

        profile = self.editor_profile()
        if not profile:
            return

        # Delete overlay only. Do NOT delete banner image. This prevents flicker.
        for item_id in [app.editor_area_rect_id, app.editor_sample_text_id]:
            if item_id:
                try:
                    canvas.delete(item_id)
                except Exception:
                    pass

        for item_id in app.editor_handle_ids:
            try:
                canvas.delete(item_id)
            except Exception:
                pass
        app.editor_handle_ids = []

        ox, oy = app.editor_canvas_offset
        s = app.editor_canvas_scale
        area = profile["text_area"]

        x1 = ox + int(area["x"] * s)
        y1 = oy + int(area["y"] * s)
        x2 = ox + int((area["x"] + area["width"]) * s)
        y2 = oy + int((area["y"] + area["height"]) * s)

        app.editor_area_rect_id = canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="#D6A43A",
            stipple="gray25",
            outline=GOLD,
            width=3,
            tags="area"
        )

        text = (app.editor_sample_text.get() or "HELLO WORLD")
        if app.editor_uppercase.get():
            text = text.upper()
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        app.editor_sample_text_id = canvas.create_text(
            cx, cy,
            text=text,
            fill=app.editor_text_color.get(),
            font=("Arial", max(10, min(42, int(app.editor_font_size.get() / 5))), "bold"),
            width=max(50, x2 - x1 - 20),
            justify="center",
            tags="sample"
        )

        for hx, hy in self.editor_handle_points(x1, y1, x2, y2):
            hid = canvas.create_rectangle(
                hx - 6, hy - 6, hx + 6, hy + 6,
                fill=GOLD,
                outline="#111111",
                tags="handle"
            )
            app.editor_handle_ids.append(hid)

        if hasattr(app, "editor_status_label"):
            app.editor_status_label.configure(
                text=f"✓ {app.editor_selected_banner.name} | Bereich {area['width']}×{area['height']}",
                text_color="#8FE6A0"
            )


    def _pil_to_png_bytes(self, image):
        app = self.app
        import io, base64
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue())


    def editor_draw_sample_text(self, canvas, x1, y1, x2, y2):
        app = self.app
        text = (app.editor_sample_text.get() or "HELLO WORLD")
        if app.editor_uppercase.get():
            text = text.upper()
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        canvas.create_text(cx, cy, text=text, fill="white", font=("Arial", 22, "bold"), width=max(50, x2-x1-20), justify="center", tags="sample")


    def editor_handle_points(self, x1, y1, x2, y2):
        app = self.app
        return [
            (x1, y1), ((x1+x2)//2, y1), (x2, y1),
            (x1, (y1+y2)//2), (x2, (y1+y2)//2),
            (x1, y2), ((x1+x2)//2, y2), (x2, y2)
        ]


    def editor_hit_test(self, x, y):
        app = self.app
        profile = self.editor_profile()
        if not profile:
            return None
        ox, oy = app.editor_canvas_offset
        s = app.editor_canvas_scale
        area = profile["text_area"]
        x1 = ox + area["x"] * s
        y1 = oy + area["y"] * s
        x2 = ox + (area["x"] + area["width"]) * s
        y2 = oy + (area["y"] + area["height"]) * s
        tol = 10

        near_left = abs(x - x1) <= tol
        near_right = abs(x - x2) <= tol
        near_top = abs(y - y1) <= tol
        near_bottom = abs(y - y2) <= tol

        if near_left and near_top: return "nw"
        if near_right and near_top: return "ne"
        if near_left and near_bottom: return "sw"
        if near_right and near_bottom: return "se"
        if near_left and y1 <= y <= y2: return "w"
        if near_right and y1 <= y <= y2: return "e"
        if near_top and x1 <= x <= x2: return "n"
        if near_bottom and x1 <= x <= x2: return "s"
        if x1 <= x <= x2 and y1 <= y <= y2: return "move"
        return "new"



    def editor_mouse_motion(self, event):
        app = self.app
        if not app.editor_selected_banner:
            return
        mode = self.editor_hit_test(event.x, event.y)
        cursor = "crosshair"
        if mode == "move":
            cursor = "fleur"
        elif mode in ("nw", "se"):
            cursor = "size_nw_se"
        elif mode in ("ne", "sw"):
            cursor = "size_ne_sw"
        elif mode in ("n", "s"):
            cursor = "sb_v_double_arrow"
        elif mode in ("e", "w"):
            cursor = "sb_h_double_arrow"
        app.editor_canvas.configure(cursor=cursor)


    def editor_mouse_down(self, event):
        app = self.app
        if not app.editor_selected_banner:
            return
        app.editor_drag_mode = self.editor_hit_test(event.x, event.y)
        app.editor_drag_start = (event.x, event.y)
        profile = self.editor_profile()
        app.editor_drag_original = dict(profile["text_area"])

        if app.editor_drag_mode == "new":
            ox, oy = app.editor_canvas_offset
            s = app.editor_canvas_scale
            bx = int((event.x - ox) / s)
            by = int((event.y - oy) / s)
            profile["text_area"] = {"x": bx, "y": by, "width": 1, "height": 1}
            app.editor_drag_original = dict(profile["text_area"])


    def editor_mouse_drag(self, event):
        app = self.app
        if not app.editor_drag_mode or not app.editor_selected_banner:
            return

        profile = self.editor_profile()
        area = dict(app.editor_drag_original)
        sx, sy = app.editor_drag_start
        dx = int((event.x - sx) / app.editor_canvas_scale)
        dy = int((event.y - sy) / app.editor_canvas_scale)
        bw, bh = app.editor_canvas_banner_size
        mode = app.editor_drag_mode

        x, y, w, h = area["x"], area["y"], area["width"], area["height"]

        if mode == "move":
            x += dx
            y += dy
        elif mode == "new":
            w = dx
            h = dy
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

        x = max(0, min(bw - 20, x))
        y = max(0, min(bh - 20, y))
        w = max(20, min(bw - x, w))
        h = max(20, min(bh - y, h))

        profile["text_area"] = {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
        self.editor_update_overlay()


    def editor_mouse_up(self, event):
        app = self.app
        if app.editor_selected_banner:
            save_banner_profiles(app.banner_profiles)
        app.editor_drag_mode = None
        app.editor_drag_start = None
        app.editor_drag_original = None

