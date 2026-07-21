import unittest
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.card_creator.batch_controller import CardBatchController


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


def make_app():
    return SimpleNamespace(
        card_output_name=Variable("show_card"),
        card_selected_template=Variable("Default"),
        card_export_profile=Variable("Broadcast PNG"),
        card_batch_items=[],
        card_batch_selected_index=None,
        card_creator_values={"Default": {"title": Variable("")}},
        card_default_output_name=Mock(return_value="default_card"),
        card_save_values=Mock(),
        card_values_plain=Mock(return_value={"title": "Hello"}),
        card_build_batch_panel=Mock(),
        card_build_form=Mock(),
        card_update_preview=Mock(),
    )


class CardBatchControllerTests(unittest.TestCase):
    def test_app_batch_mutation_methods_are_thin_adapters(self):
        app_path = Path(__file__).resolve().parents[1] / "vadafok_studio" / "app.py"
        source = app_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        studio = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio")
        expected_calls = {
            "card_batch_current_item_name": "self.card_batch_controller.current_item_name()",
            "card_batch_add_current": "self.card_batch_controller.add_current()",
            "card_batch_duplicate_selected": "self.card_batch_controller.duplicate_selected()",
            "card_batch_remove_selected": "self.card_batch_controller.remove_selected()",
            "card_batch_clear": "self.card_batch_controller.clear()",
            "card_batch_select": "self.card_batch_controller.select(idx)",
        }
        methods = {node.name: node for node in studio.body if isinstance(node, ast.FunctionDef)}

        for name, call in expected_calls.items():
            method = methods[name]
            block = ast.get_source_segment(source, method)
            self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)
            self.assertIn(call, block)

    def test_add_current_captures_values_and_selects_new_item(self):
        app = make_app()
        CardBatchController(app, lambda: ["Default"]).add_current()
        self.assertEqual(app.card_batch_items[0]["values"], {"title": "Hello"})
        self.assertEqual(app.card_batch_items[0]["output_name"], "show_card")
        self.assertEqual(app.card_batch_selected_index, 0)
        app.card_save_values.assert_called_once_with()
        app.card_build_batch_panel.assert_called_once_with()

    def test_duplicate_selected_copies_nested_values(self):
        app = make_app()
        original = {"template": "Default", "output_name": "show_card", "profile": "Broadcast PNG", "values": {"title": "Hello"}}
        app.card_batch_items = [original]
        app.card_batch_selected_index = 0
        CardBatchController(app, lambda: ["Default"]).duplicate_selected()
        self.assertEqual(app.card_batch_items[1]["output_name"], "show_card_copy")
        self.assertIsNot(app.card_batch_items[1]["values"], original["values"])
        self.assertEqual(app.card_batch_selected_index, 1)

    def test_remove_without_selection_preserves_items(self):
        app = make_app()
        app.card_batch_items = [{"output_name": "one"}]
        with patch("vadafok_studio.card_creator.batch_controller.messagebox.showinfo") as info:
            CardBatchController(app, lambda: ["Default"]).remove_selected()
        self.assertEqual(app.card_batch_items, [{"output_name": "one"}])
        info.assert_called_once()
        app.card_build_batch_panel.assert_not_called()

    def test_clear_requires_confirmation(self):
        app = make_app()
        app.card_batch_items = [{"output_name": "one"}]
        with patch("vadafok_studio.card_creator.batch_controller.messagebox.askyesno", return_value=True):
            CardBatchController(app, lambda: ["Default"]).clear()
        self.assertEqual(app.card_batch_items, [])
        self.assertIsNone(app.card_batch_selected_index)
        app.card_build_batch_panel.assert_called_once_with()

    def test_current_item_name_uses_default_for_blank_value(self):
        app = make_app()
        app.card_output_name = Variable("  ")
        self.assertEqual(
            CardBatchController(app, lambda: ["Default"]).current_item_name(),
            "default_card",
        )

    def test_select_restores_item_into_existing_form_variables(self):
        app = make_app()
        app.card_batch_items = [{
            "template": "Default",
            "output_name": "selected_card",
            "profile": "Web PNG",
            "values": {"title": "Selected title"},
        }]

        CardBatchController(app, lambda: ["Default"]).select(0)

        self.assertEqual(app.card_batch_selected_index, 0)
        self.assertEqual(app.card_output_name.get(), "selected_card")
        self.assertEqual(app.card_export_profile.get(), "Web PNG")
        self.assertEqual(
            app.card_creator_values["Default"]["title"].get(),
            "Selected title",
        )
        app.card_build_form.assert_called_once_with()
        app.card_save_values.assert_called_once_with()
        app.card_update_preview.assert_called_once_with()
        app.card_build_batch_panel.assert_called_once_with()

    def test_select_ignores_out_of_range_index(self):
        app = make_app()

        CardBatchController(app, lambda: ["Default"]).select(4)

        self.assertIsNone(app.card_batch_selected_index)
        app.card_build_form.assert_not_called()
