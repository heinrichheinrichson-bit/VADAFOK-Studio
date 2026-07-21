import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.quick_cards.controller import QuickCardsController


class Variable:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class QuickCardsControllerTests(unittest.TestCase):
    def make_app(self):
        return SimpleNamespace(
            quick_cards_collapsed=set(),
            quick_cards_tree=object(),
            quick_cards_category_widgets={},
            quick_cards_build_tree=Mock(),
            show_quick_cards=Mock(),
            text_library_new_text=Variable(),
            text_library_new_category=Variable(),
            quick_cards_target_category=Variable("Chat"),
            quick_cards_edit_text_var=Variable(),
            quick_cards_editing_category=None,
            quick_cards_editing_text=None,
            text_library_data={"Chat": []},
            live_card_pending_text="",
        )

    def test_toggle_refreshes_tree_without_rebuilding_page(self):
        app = self.make_app()
        controller = QuickCardsController(app)
        controller.toggle_category("Chat")
        self.assertIn("Chat", app.quick_cards_collapsed)
        app.quick_cards_build_tree.assert_called_once()
        app.show_quick_cards.assert_not_called()

    @patch("vadafok_studio.quick_cards.controller.build_category_body")
    @patch("vadafok_studio.quick_cards.controller.text_library_engine.add_text")
    def test_add_text_updates_only_target_category(self, add_text, build_body):
        app = self.make_app()
        app.text_library_new_text.set("Hello chat")
        add_text.return_value = {"Chat": ["Hello chat"]}
        build_body.return_value = True
        controller = QuickCardsController(app)
        controller.add_text()
        add_text.assert_called_once_with("Chat", "Hello chat")
        self.assertEqual(app.live_card_pending_text, "Hello chat")
        self.assertEqual(app.text_library_new_text.get(), "")
        build_body.assert_called_once_with(app, "Chat")
        app.quick_cards_build_tree.assert_not_called()
        app.show_quick_cards.assert_not_called()

    def test_cancel_edit_clears_state_and_refreshes_tree(self):
        app = self.make_app()
        app.quick_cards_editing_category = "Chat"
        app.quick_cards_editing_text = "Old"
        app.quick_cards_edit_text_var.set("Old")
        controller = QuickCardsController(app)
        controller.cancel_text_edit()
        self.assertIsNone(app.quick_cards_editing_category)
        self.assertIsNone(app.quick_cards_editing_text)
        self.assertEqual(app.quick_cards_edit_text_var.get(), "")
        app.quick_cards_build_tree.assert_called_once()

    @patch("vadafok_studio.quick_cards.controller.set_category_collapsed")
    def test_toggle_updates_only_selected_category_when_view_exists(self, update):
        app = self.make_app()
        update.return_value = True
        controller = QuickCardsController(app)
        controller.toggle_category("Chat")
        update.assert_called_once_with(app, "Chat", True)
        app.quick_cards_build_tree.assert_not_called()
        app.show_quick_cards.assert_not_called()


if __name__ == "__main__":
    unittest.main()
