from __future__ import annotations

import unittest
from unittest.mock import MagicMock, Mock, patch

from vadafok_studio.card_creator.controller import CardCreatorController
from vadafok_studio.card_creator.state import CardCreatorState


class CardCreatorControllerTests(unittest.TestCase):
    def make_app(self):
        app = MagicMock()
        app.card_selected_template.get.return_value = ""
        app.card_default_output_name.return_value = "output.png"
        app.card_creator_state = CardCreatorState()
        return app

    def make_controller(self, app, templates=None, default="A", loader=None):
        names = templates if templates is not None else ["A", "B"]
        return CardCreatorController(
            app,
            lambda: list(names),
            Mock(),
            Mock(return_value=default),
            loader or Mock(side_effect=lambda name: {"name": name}),
        )

    @patch("vadafok_studio.card_creator.controller.record_recent_template")
    def test_select_template_updates_only_targeted_parts(self, record):
        app = self.make_app()
        record.return_value = ["B", "A"]
        controller = self.make_controller(app)

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
        controller = self.make_controller(app, templates=["A"])

        self.assertFalse(controller.select_template("Missing"))
        app.card_selected_template.set.assert_not_called()
        app.card_update_preview.assert_not_called()

    @patch("vadafok_studio.card_creator.controller.remove_recent_template")
    def test_remove_recent_refreshes_only_recent_area(self, remove):
        app = self.make_app()
        remove.return_value = ["A"]
        controller = self.make_controller(app)

        result = controller.remove_recent("B")

        self.assertEqual(result, ["A"])
        app.card_refresh_recent_templates.assert_called_once()
        app.show_card_creator_page.assert_not_called()

    def test_current_template_uses_configured_default(self):
        app = self.make_app()
        loader = Mock(side_effect=lambda name: {"name": name})
        controller = self.make_controller(
            app, templates=["A", "B"], default="B", loader=loader
        )

        result = controller.current_template()

        self.assertEqual(result, {"name": "B"})
        app.card_selected_template.set.assert_called_once_with("B")
        loader.assert_called_once_with("B")


if __name__ == "__main__":
    unittest.main()
