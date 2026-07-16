from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "vadafok_studio" / "app.py"


class LibraryPickerRuntimeReturnTests(unittest.TestCase):
    def setUp(self):
        self.source = APP_FILE.read_text(encoding="utf-8")

    def method(self, name):
        start = self.source.index(f"def {name}")
        tail = self.source[start:]
        next_method = tail.find("\n    def ", 1)
        return tail if next_method < 0 else tail[:next_method]

    def test_open_picker_sets_runtime_fallback_after_library_build(self):
        method = self.method("open_template_background_picker")
        self.assertIn(
            "self.library_controller.open_template_background_picker()",
            method,
        )
        self.assertIn(
            "self.library_template_background_picker_mode = True",
            method,
        )
        self.assertIn(
            'self.library_return_page = "Template Editor"',
            method,
        )

    def test_assignment_combines_all_return_signals(self):
        method = self.method("assign_selected_template_background")
        for required in (
            "controller_return",
            "flag_return",
            "page_return",
            "should_return =",
            "controller_return",
            "or flag_return",
            "or page_return",
            "if should_return:",
        ):
            self.assertIn(required, method)

    def test_assignment_clears_state_and_returns(self):
        method = self.method("assign_selected_template_background")
        self.assertIn("controller.cancel_picker()", method)
        self.assertIn("self.show_template_editor_page()", method)

    def test_show_use_reaches_background_assignment(self):
        method = self.method("default_selected_action")
        self.assertIn(
            "self.assign_selected_template_background()",
            method,
        )

    def test_simple_click_does_not_apply(self):
        method = self.method("select_library_item")
        self.assertNotIn(
            "self.assign_selected_template_background()",
            method,
        )


if __name__ == "__main__":
    unittest.main()
