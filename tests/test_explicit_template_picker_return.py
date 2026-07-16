from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "vadafok_studio" / "app.py"
CONTROLLER_FILE = ROOT / "vadafok_studio" / "library" / "controller.py"


class LibraryControllerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app_source = APP_FILE.read_text(encoding="utf-8")
        self.controller_source = CONTROLLER_FILE.read_text(encoding="utf-8")
        tree = ast.parse(self.app_source)
        self.app_class = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio"
        )

    def method(self, name: str) -> str:
        node = next(
            node for node in self.app_class.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        )
        return ast.get_source_segment(self.app_source, node) or ""

    def test_controller_is_integrated(self) -> None:
        self.assertIn("from .library import LibraryController", self.app_source)
        self.assertIn(
            "self.library_controller = LibraryController(self)",
            self.app_source,
        )

    def test_picker_open_delegates_to_controller(self) -> None:
        self.assertIn(
            "self.library_controller.open_template_background_picker()",
            self.method("open_template_background_picker"),
        )

    def test_assignment_queries_controller_state_before_update(self) -> None:
        method = self.method("assign_selected_template_background")
        self.assertIn(
            "controller.is_template_background_picker",
            method,
        )
        self.assertIn("refresh_canvas=not should_return", method)

    def test_assignment_finishes_with_cancel_and_editor_open(self) -> None:
        method = self.method("assign_selected_template_background")
        self.assertIn("controller.cancel_picker()", method)
        self.assertIn("self.show_template_editor_page()", method)

    def test_simple_click_does_not_apply(self) -> None:
        self.assertNotIn(
            "self.assign_selected_template_background()",
            self.method("select_library_item"),
        )


if __name__ == "__main__":
    unittest.main()
