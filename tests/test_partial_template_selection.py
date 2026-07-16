from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_FILE = PROJECT_ROOT / "vadafok_studio" / "app.py"


class PartialTemplateSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = APP_FILE.read_text(encoding="utf-8")

    def _method(self, name: str, next_name: str) -> str:
        start = self.source.index(f"def {name}")
        end = self.source.index(f"def {next_name}", start)
        return self.source[start:end]

    def test_selection_does_not_reload_full_page(self) -> None:
        method = self._method("card_select_template", "card_template")
        self.assertNotIn("show_card_creator_page", method)

    def test_selection_uses_targeted_updates(self) -> None:
        method = self._method("card_select_template", "card_template")
        for required in (
            "self.card_refresh_recent_templates()",
            "self.card_refresh_all_templates()",
            "self.card_build_form()",
            "self.card_update_preview()",
        ):
            self.assertIn(required, method)

    def test_all_template_buttons_are_reused(self) -> None:
        self.assertIn("self.card_template_buttons = {}", self.source)
        self.assertIn("def card_refresh_all_templates(self):", self.source)
        self.assertIn("button.configure(text=prefix + name)", self.source)

    def test_template_list_has_dedicated_container(self) -> None:
        self.assertIn("self.card_all_templates_frame = ctk.CTkFrame", self.source)
        self.assertIn(
            "self.card_all_templates_label.pack(",
            self.source,
        )


if __name__ == "__main__":
    unittest.main()
