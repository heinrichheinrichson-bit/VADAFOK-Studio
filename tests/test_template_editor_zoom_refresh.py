from __future__ import annotations

import ast
from pathlib import Path
import unittest


APP_PATH = Path(__file__).resolve().parents[1] / "vadafok_studio" / "app.py"
CANVAS_PATH = (
    Path(__file__).resolve().parents[1]
    / "vadafok_studio"
    / "template_editor"
    / "canvas_view.py"
)


def method_source(name: str) -> str:
    path = CANVAS_PATH if name == "template_draw_canvas" else APP_PATH
    lookup_name = "draw_canvas" if name == "template_draw_canvas" else name
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == lookup_name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"Method not found: {name}")


class TemplateEditorZoomRefreshTests(unittest.TestCase):
    def test_canvas_redraw_can_skip_layer_rebuild(self):
        method = method_source("template_draw_canvas")
        self.assertIn("refresh_layers: bool = True", method)
        self.assertIn("refresh_layers=refresh_layers", method)

    def test_zoom_skips_layer_rebuild(self):
        method = method_source("template_set_zoom")
        self.assertIn("template_draw_canvas(refresh_layers=False)", method)

    def test_pan_reset_skips_layer_rebuild(self):
        method = method_source("template_pan_reset")
        self.assertIn("template_draw_canvas(refresh_layers=False)", method)

    def test_background_loader_uses_file_aware_cache(self):
        method = method_source("template_load_background_image")
        self.assertIn("st_mtime_ns", method)
        self.assertIn("template_bg_cache_key", method)
        self.assertIn("load_rgba", method)

    def test_old_canvas_is_cleared_after_new_photo_is_ready(self):
        method = method_source("template_draw_canvas")
        photo_pos = method.index("next_bg_photo = tk.PhotoImage")
        clear_pos = method.index('canvas.delete("all")', photo_pos)
        self.assertGreater(clear_pos, photo_pos)


if __name__ == "__main__":
    unittest.main()
