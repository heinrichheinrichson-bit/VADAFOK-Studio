from __future__ import annotations

import ast
from pathlib import Path
import unittest


APP_PATH = Path(__file__).resolve().parents[1] / "vadafok_studio" / "app.py"
OVERLAY_PATH = (
    Path(__file__).resolve().parents[1]
    / "vadafok_studio"
    / "template_editor"
    / "overlay_view.py"
)
MOUSE_PATH = (
    Path(__file__).resolve().parents[1]
    / "vadafok_studio"
    / "template_editor"
    / "mouse_controller.py"
)


def method_source(name: str) -> str:
    if name == "template_update_fields_overlay":
        path, lookup_name = OVERLAY_PATH, "update_fields_overlay"
    elif name in ("template_mouse_drag", "template_mouse_up"):
        path, lookup_name = MOUSE_PATH, name.removeprefix("template_")
    else:
        path, lookup_name = APP_PATH, name
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == lookup_name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"Method not found: {name}")


class TemplateEditorDragPartialRefreshTests(unittest.TestCase):
    def test_overlay_supports_targeted_refresh_flags(self):
        method = method_source("template_update_fields_overlay")
        self.assertIn("refresh_layers: bool = True", method)
        self.assertIn("refresh_status: bool = True", method)
        self.assertIn("if refresh_layers", method)
        self.assertIn("if refresh_status", method)

    def test_drag_skips_layers_and_status_rebuilds(self):
        method = method_source("template_mouse_drag")
        self.assertGreaterEqual(method.count("refresh_layers=False"), 2)
        self.assertGreaterEqual(method.count("refresh_status=False"), 2)
        self.assertNotIn("template_build_layers_panel()", method)

    def test_release_refreshes_status_without_layers_rebuild(self):
        method = method_source("template_mouse_up")
        self.assertIn("template_update_fields_overlay(refresh_layers=False)", method)


if __name__ == "__main__":
    unittest.main()
