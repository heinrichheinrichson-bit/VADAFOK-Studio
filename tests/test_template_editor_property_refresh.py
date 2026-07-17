from __future__ import annotations

import ast
from pathlib import Path
import unittest


APP_PATH = Path(__file__).resolve().parents[1] / "vadafok_studio" / "app.py"


def method_source(name: str) -> str:
    source = APP_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"Method not found: {name}")


class TemplateEditorPropertyRefreshTests(unittest.TestCase):
    def test_property_edit_uses_overlay_instead_of_full_canvas_redraw(self):
        method = method_source("template_apply_selected_properties")
        self.assertIn("template_update_fields_overlay", method)
        self.assertIn("refresh_layers=False", method)
        self.assertIn("refresh_status=False", method)
        self.assertNotIn("template_draw_canvas", method)

    def test_property_commit_is_debounced(self):
        method = method_source("template_schedule_property_commit")
        self.assertIn("after_cancel", method)
        self.assertIn("self.after(", method)
        self.assertIn("template_commit_selected_properties", method)

    def test_deferred_commit_saves_and_refreshes_dependencies_once(self):
        method = method_source("template_commit_selected_properties")
        self.assertIn("save_template", method)
        self.assertIn("refresh_layers=True", method)
        self.assertIn("refresh_status=True", method)


if __name__ == "__main__":
    unittest.main()
