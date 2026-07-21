import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.card_creator.style_controller import CardStyleController


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


def make_app():
    return SimpleNamespace(
        card_selected_template=Variable("Default"),
        card_template=Mock(
            return_value={"fields": [{"name": "title"}, {"name": "time"}]}
        ),
        card_update_preview=Mock(),
        show_template_editor_page=Mock(),
        template_selected_name=None,
        template_working_data={"cached": True},
    )


class CardStyleControllerTests(unittest.TestCase):
    def test_field_index_returns_matching_position(self):
        app = make_app()
        controller = CardStyleController(app, Mock(), Mock(), Mock())

        self.assertEqual(controller.field_index_by_name("time"), 1)
        self.assertIsNone(controller.field_index_by_name("missing"))

    def test_apply_style_updates_field_saves_and_refreshes(self):
        app = make_app()
        app.template_selected_name = "Default"
        template = {"fields": [{"name": "title"}]}
        style = {"font_size": 90}
        engine = Mock()
        engine.load_style.return_value = style
        loader = Mock(return_value=template)
        saver = Mock()
        controller = CardStyleController(app, engine, loader, saver)

        with patch(
            "vadafok_studio.card_creator.style_controller.messagebox.showinfo"
        ):
            controller.apply_to_field("title", "Gold")

        engine.apply_style.assert_called_once_with(template["fields"][0], style)
        saver.assert_called_once_with("Default", template)
        self.assertIsNone(app.template_working_data)
        app.card_update_preview.assert_called_once_with()

    def test_missing_field_does_not_save(self):
        app = make_app()
        saver = Mock()
        controller = CardStyleController(
            app, Mock(), Mock(return_value={"fields": []}), saver
        )

        with patch(
            "vadafok_studio.card_creator.style_controller.messagebox.showwarning"
        ) as warning:
            controller.apply_to_field("missing", "Gold")

        warning.assert_called_once()
        saver.assert_not_called()

    def test_open_editor_uses_selected_card_template(self):
        app = make_app()

        CardStyleController(app, Mock(), Mock(), Mock()).open_template_editor()

        self.assertEqual(app.template_selected_name, "Default")
        app.show_template_editor_page.assert_called_once_with()
