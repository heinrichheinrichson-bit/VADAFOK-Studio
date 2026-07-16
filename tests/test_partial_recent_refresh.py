from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_FILE = PROJECT_ROOT / "vadafok_studio" / "app.py"


class PartialRecentRefreshTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = APP_FILE.read_text(encoding="utf-8")

    def test_recent_refresh_method_exists(self) -> None:
        self.assertIn("def card_refresh_recent_templates(self):", self.source)

    def test_remove_does_not_reload_whole_page(self) -> None:
        start = self.source.index("def card_remove_recent_template")
        end = self.source.index("def card_select_template", start)
        method = self.source[start:end]

        self.assertIn("self.card_refresh_recent_templates()", method)
        self.assertNotIn("self.show_card_creator_page()", method)

    def test_dedicated_recent_container_exists(self) -> None:
        self.assertIn("self.card_recent_templates_frame", self.source)
        self.assertIn(
            "self.card_recent_templates_frame = ctk.CTkFrame",
            self.source,
        )

    def test_refresh_only_destroys_recent_children(self) -> None:
        start = self.source.index("def card_refresh_recent_templates")
        end = self.source.index("def card_remove_recent_template", start)
        method = self.source[start:end]

        self.assertIn(
            "for child in self.card_recent_templates_frame.winfo_children():",
            method,
        )
        self.assertIn("child.destroy()", method)
        self.assertNotIn("show_card_creator_page", method)


if __name__ == "__main__":
    unittest.main()
