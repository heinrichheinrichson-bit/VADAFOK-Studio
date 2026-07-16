from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "vadafok_studio" / "app.py"


class LibraryPickerStaleCanvasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = APP_FILE.read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)
        self.app_class = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio"
        )

    def method(self, name: str) -> str:
        node = next(
            node
            for node in self.app_class.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        )
        return ast.get_source_segment(self.source, node) or ""

    def test_background_setter_supports_deferred_canvas_refresh(self) -> None:
        method = self.method("template_set_background_path")
        self.assertIn("refresh_canvas=True", method)
        self.assertIn("if refresh_canvas:", method)
        self.assertIn("canvas.winfo_exists()", method)

    def test_picker_decides_return_before_background_update(self) -> None:
        method = self.method("assign_selected_template_background")
        return_index = method.index("should_return =")
        update_index = method.index("self.template_set_background_path(")
        self.assertLess(return_index, update_index)

    def test_picker_skips_stale_canvas_refresh(self) -> None:
        method = self.method("assign_selected_template_background")
        self.assertIn("refresh_canvas=not should_return", method)

    def test_picker_cancels_state_and_opens_editor(self) -> None:
        method = self.method("assign_selected_template_background")
        self.assertIn("controller.cancel_picker()", method)
        self.assertIn("self.show_template_editor_page()", method)

    def test_double_click_and_show_use_share_assignment(self) -> None:
        double_click = self.method("library_item_double_click")
        default_action = self.method("default_selected_action")
        self.assertIn("self.default_selected_action()", double_click)
        self.assertIn(
            "self.assign_selected_template_background()",
            default_action,
        )

    def test_simple_click_only_selects(self) -> None:
        method = self.method("select_library_item")
        self.assertNotIn(
            "self.assign_selected_template_background()",
            method,
        )


if __name__ == "__main__":
    unittest.main()
