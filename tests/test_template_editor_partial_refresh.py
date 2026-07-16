from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_FILE = PROJECT_ROOT / "vadafok_studio" / "app.py"
CONTROLLER_FILE = (
    PROJECT_ROOT / "vadafok_studio" / "template_editor" / "controller.py"
)


class TemplateEditorPartialRefreshTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app_source = APP_FILE.read_text(encoding="utf-8")
        self.controller_source = CONTROLLER_FILE.read_text(encoding="utf-8")

    def test_controller_calls_partial_refresh(self) -> None:
        start = self.controller_source.index("def select_template")
        method = self.controller_source[start:]

        self.assertIn(
            '"template_refresh_selected_template"',
            method,
        )
        self.assertIn("if callable(refresh):", method)
        self.assertIn("refresh()", method)

        before_fallback = method.split(
            "# Defensive fallback",
            1,
        )[0]
        self.assertNotIn(
            "self.app.show_template_editor_page()",
            before_fallback,
        )

    def test_app_has_template_button_registry(self) -> None:
        self.assertIn("self.template_list_buttons = {}", self.app_source)
        self.assertIn(
            "self.template_list_buttons[name] = button",
            self.app_source,
        )

    def test_partial_refresh_updates_targeted_areas(self) -> None:
        start = self.app_source.index(
            "def template_refresh_selected_template"
        )
        end = self.app_source.index(
            "def template_build_properties_panel",
            start,
        )
        method = self.app_source[start:end]

        required_fragments = (
            "self.template_refresh_template_list_selection()",
            'getattr(self, "template_status_label", None)',
            "status_label.configure(",
            "self.template_build_properties_panel()",
            "self.template_ensure_field_ids()",
            "self.template_draw_canvas()",
            "self.template_build_style_presets_panel()",
            "self.template_build_layers_panel()",
        )

        for fragment in required_fragments:
            self.assertIn(fragment, method)

        self.assertNotIn("show_template_editor_page", method)
        self.assertNotIn("clear_main", method)

    def test_status_label_update_is_guarded(self) -> None:
        start = self.app_source.index(
            "def template_refresh_selected_template"
        )
        end = self.app_source.index(
            "def template_build_properties_panel",
            start,
        )
        method = self.app_source[start:end]

        self.assertIn("if status_label is not None:", method)
        self.assertIn("status_label.configure(", method)


if __name__ == "__main__":
    unittest.main()
