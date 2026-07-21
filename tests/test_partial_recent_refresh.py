from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_FILE = PROJECT_ROOT / "vadafok_studio" / "app.py"
CONTROLLER_FILE = (
    PROJECT_ROOT / "vadafok_studio" / "card_creator" / "controller.py"
)
PAGE_FILE = PROJECT_ROOT / "vadafok_studio" / "card_creator" / "page.py"
TEMPLATE_LIST_FILE = (
    PROJECT_ROOT / "vadafok_studio" / "card_creator" / "template_list_view.py"
)


class PartialRecentRefreshTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app_source = APP_FILE.read_text(encoding="utf-8")
        self.controller_source = CONTROLLER_FILE.read_text(encoding="utf-8")
        self.page_source = PAGE_FILE.read_text(encoding="utf-8")
        self.template_list_source = TEMPLATE_LIST_FILE.read_text(encoding="utf-8")

    def test_recent_refresh_method_exists(self) -> None:
        self.assertIn(
            "def card_refresh_recent_templates(self):",
            self.app_source,
        )

    def test_remove_button_calls_controller_directly(self) -> None:
        self.assertIn(
            "app.card_creator_controller.remove_recent(",
            self.template_list_source,
        )
        self.assertNotIn("def card_remove_recent_template", self.app_source)

    def test_controller_refreshes_only_recent_area(self) -> None:
        start = self.controller_source.index("def remove_recent")
        end = self.controller_source.index("def select_template", start)
        method = self.controller_source[start:end]

        self.assertIn("self.app.card_refresh_recent_templates()", method)
        self.assertNotIn("show_card_creator_page", method)

    def test_dedicated_recent_container_exists(self) -> None:
        self.assertIn(
            "app.card_recent_templates_frame = ctk.CTkFrame",
            self.page_source,
        )

    def test_refresh_only_destroys_recent_children(self) -> None:
        method = self.template_list_source.split(
            "def refresh_recent_templates", 1
        )[1]

        self.assertIn(
            "for child in frame.winfo_children():",
            method,
        )
        self.assertIn("child.destroy()", method)
        self.assertNotIn("show_card_creator_page", method)


if __name__ == "__main__":
    unittest.main()
