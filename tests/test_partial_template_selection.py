from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_FILE = PROJECT_ROOT / "vadafok_studio" / "app.py"
CONTROLLER_FILE = (
    PROJECT_ROOT / "vadafok_studio" / "card_creator" / "controller.py"
)
PAGE_FILE = PROJECT_ROOT / "vadafok_studio" / "card_creator" / "page.py"


class PartialTemplateSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app_source = APP_FILE.read_text(encoding="utf-8")
        self.controller_source = CONTROLLER_FILE.read_text(encoding="utf-8")
        self.page_source = PAGE_FILE.read_text(encoding="utf-8")

    def test_selection_delegates_to_controller(self) -> None:
        start = self.app_source.index("def card_select_template")
        end = self.app_source.index("def card_template", start)
        method = self.app_source[start:end]

        self.assertIn(
            "self.card_creator_controller.select_template(name)",
            method,
        )
        self.assertNotIn("show_card_creator_page", method)

    def test_controller_uses_targeted_updates(self) -> None:
        start = self.controller_source.index("def select_template")
        method = self.controller_source[start:]

        for required in (
            "self.app.card_refresh_recent_templates()",
            "self.app.card_refresh_all_templates()",
            "self.app.card_build_form()",
            "self.app.card_update_preview()",
        ):
            self.assertIn(required, method)

        self.assertNotIn("show_card_creator_page", method)

    def test_all_template_buttons_are_reused(self) -> None:
        self.assertIn("app.card_template_buttons = {}", self.page_source)
        self.assertIn(
            "def card_refresh_all_templates(self):",
            self.app_source,
        )
        self.assertIn(
            "button.configure(text=prefix + name)",
            self.app_source,
        )

    def test_template_list_has_dedicated_container(self) -> None:
        self.assertIn(
            "app.card_all_templates_frame = ctk.CTkFrame",
            self.page_source,
        )
        self.assertIn(
            "app.card_all_templates_label.pack(",
            self.page_source,
        )


if __name__ == "__main__":
    unittest.main()
