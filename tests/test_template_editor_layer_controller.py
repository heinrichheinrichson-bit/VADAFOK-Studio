from pathlib import Path
from types import SimpleNamespace
import ast
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.template_editor.layer_controller import (
    layer_drag_end,
    layer_target_from_y,
    move_layer,
    move_layer_to_index,
)


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"


class TemplateEditorLayerControllerTests(unittest.TestCase):
    def test_app_layer_methods_are_thin_adapters(self):
        tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
        names = {
            "template_layer_drag_start",
            "template_layer_clear_drop_indicator",
            "template_layer_drag_motion",
            "template_layer_show_drop_indicator",
            "template_layer_drag_end",
            "template_layer_target_from_y",
            "template_move_layer_to_index",
            "template_refresh_layers_selection",
            "template_select_layer",
            "template_move_layer",
        }
        self.assertEqual(
            [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
                and node.name in names
                and node.end_lineno - node.lineno + 1 > 2
            ],
            [],
        )

    def test_target_uses_nearest_visible_layer_row(self):
        near = Mock()
        near.winfo_rooty.return_value = 100
        near.winfo_height.return_value = 20
        far = Mock()
        far.winfo_rooty.return_value = 200
        far.winfo_height.return_value = 20
        body = Mock()
        body.grid_slaves.side_effect = lambda row, column: [near] if row == 3 else [far]
        app = SimpleNamespace(
            _template_layer_row_for_field={0: 3, 1: 5},
            template_layers_body=body,
        )
        self.assertEqual(layer_target_from_y(app, 115), 0)
        self.assertEqual(layer_target_from_y(app, 205), 1)

    @patch("vadafok_studio.template_editor.layer_controller.save_template")
    def test_drag_reorder_remaps_all_selected_indices(self, save):
        fields = [{"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}]
        template = {"fields": fields}
        app = SimpleNamespace(
            template_current=Mock(return_value=template),
            template_push_history=Mock(),
            template_selected_fields={0, 1, 3},
            template_selected_field=1,
            template_selected_name="Template",
            template_draw_canvas=Mock(),
            template_build_layers_panel=Mock(),
        )

        move_layer_to_index(app, 1, 3)

        self.assertEqual([field["name"] for field in fields], ["A", "C", "D", "B"])
        self.assertEqual(app.template_selected_fields, {0, 2, 3})
        self.assertEqual(app.template_selected_field, 3)
        app.template_push_history.assert_called_once_with("drag layer reorder")
        save.assert_called_once_with("Template", template)

    @patch("vadafok_studio.template_editor.layer_controller.save_template")
    def test_arrow_move_swaps_selection_and_rebuilds(self, save):
        fields = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        template = {"fields": fields}
        app = SimpleNamespace(
            template_current=Mock(return_value=template),
            template_push_history=Mock(),
            template_selected_fields={0, 2},
            template_selected_field=0,
            template_selected_name="Template",
            template_draw_canvas=Mock(),
            template_build_layers_panel=Mock(),
        )

        move_layer(app, 0, 1)

        self.assertEqual([field["name"] for field in fields], ["B", "A", "C"])
        self.assertEqual(app.template_selected_fields, {1, 2})
        self.assertEqual(app.template_selected_field, 1)
        app.template_build_layers_panel.assert_called_once_with()

    def test_drag_end_without_source_only_rebuilds(self):
        app = SimpleNamespace(
            template_layers_body=Mock(),
            template_layer_clear_drop_indicator=Mock(),
            template_layer_drag_index=None,
            template_layer_drop_target=None,
            template_build_layers_panel=Mock(),
        )
        self.assertEqual(layer_drag_end(app, SimpleNamespace(y_root=0)), "break")
        app.template_build_layers_panel.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
