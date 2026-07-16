from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from vadafok_studio.card_creator.controller import CardCreatorController


class CardCreatorControllerTests(unittest.TestCase):
    def make_app(self):
        app = MagicMock()
        app.card_selected_template.get.return_value = ""
        app.card_default_output_name.return_value = "output.png"
        return app

    @patch("vadafok_studio.card_creator.controller.record_recent_template")
    def test_select_template_updates_only_targeted_parts(self, record):
        app = self.make_app()
        record.return_value = ["B", "A"]
        controller = CardCreatorController(app, lambda: ["A", "B"])

        self.assertTrue(controller.select_template("B"))
        record.assert_called_once_with("B", ["A", "B"])
        app.card_selected_template.set.assert_called_once_with("B")
        app.card_refresh_recent_templates.assert_called_once()
        app.card_refresh_all_templates.assert_called_once()
        app.card_build_form.assert_called_once()
        app.card_update_preview.assert_called_once()
        app.show_card_creator_page.assert_not_called()

    def test_unknown_template_is_ignored(self):
        app = self.make_app()
        controller = CardCreatorController(app, lambda: ["A"])

        self.assertFalse(controller.select_template("Missing"))
        app.card_selected_template.set.assert_not_called()
        app.card_update_preview.assert_not_called()

    @patch("vadafok_studio.card_creator.controller.remove_recent_template")
    def test_remove_recent_refreshes_only_recent_area(self, remove):
        app = self.make_app()
        remove.return_value = ["A"]
        controller = CardCreatorController(app, lambda: ["A", "B"])

        result = controller.remove_recent("B")

        self.assertEqual(result, ["A"])
        app.card_refresh_recent_templates.assert_called_once()
        app.show_card_creator_page.assert_not_called()


if __name__ == "__main__":
    unittest.main()
