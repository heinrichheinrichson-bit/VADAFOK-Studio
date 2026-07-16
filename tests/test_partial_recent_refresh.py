from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_FILE = PROJECT_ROOT / "vadafok_studio" / "app.py"
CONTROLLER_FILE = (
    PROJECT_ROOT / "vadafok_studio" / "card_creator" / "controller.py"
)


class PartialRecentRefreshTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app_source = APP_FILE.read_text(encoding="utf-8")
        self.controller_source = CONTROLLER_FILE.read_text(encoding="utf-8")

    def test_recent_refresh_method_exists(self) -> None:
        self.assertIn(
            "def card_refresh_recent_templates(self):",
            self.app_source,
        )

    def test_remove_delegates_to_controller(self) -> None:
        start = self.app_source.index("def card_remove_recent_template")
        end = self.app_source.index("def card_select_template", start)
        method = self.app_source[start:end]

        self.assertIn(
            "self.card_creator_controller.remove_recent(name)",
            method,
        )
        self.assertNotIn("self.show_card_creator_page()", method)

    def test_controller_refreshes_only_recent_area(self) -> None:
        start = self.controller_source.index("def remove_recent")
        end = self.controller_source.index("def select_template", start)
        method = self.controller_source[start:end]

        self.assertIn("self.app.card_refresh_recent_templates()", method)
        self.assertNotIn("show_card_creator_page", method)

    def test_dedicated_recent_container_exists(self) -> None:
        self.assertIn(
            "self.card_recent_templates_frame = ctk.CTkFrame",
            self.app_source,
        )

    def test_refresh_only_destroys_recent_children(self) -> None:
        start = self.app_source.index("def card_refresh_recent_templates")
        end = self.app_source.index("def card_remove_recent_template", start)
        method = self.app_source[start:end]

        self.assertIn(
            "for child in self.card_recent_templates_frame.winfo_children():",
            method,
        )
        self.assertIn("child.destroy()", method)
        self.assertNotIn("show_card_creator_page", method)


if __name__ == "__main__":
    unittest.main()
