from pathlib import Path
from types import SimpleNamespace
import ast
import unittest
from unittest.mock import Mock

from vadafok_studio.template_editor.selection_controller import (
    marquee_finish,
    marquee_start_select,
    multi_select_modifier,
    toggle_selection,
)


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"


class TemplateEditorSelectionControllerTests(unittest.TestCase):
    def test_app_selection_methods_are_thin_adapters(self):
        tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
        names = {
            "template_multi_select_modifier",
            "template_sync_selection_set",
            "template_selection_count",
            "template_clear_selection",
            "template_set_single_selection",
            "template_toggle_selection",
            "template_marquee_clear",
            "template_marquee_start_select",
            "template_marquee_drag",
            "template_marquee_finish",
        }
        large = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name in names
            and node.end_lineno - node.lineno + 1 > 2
        ]
        self.assertEqual(large, [])

    def test_shift_ctrl_and_explicit_key_state_enable_additive_selection(self):
        app = SimpleNamespace(template_shift_down=False, template_ctrl_down=False)
        self.assertTrue(multi_select_modifier(app, SimpleNamespace(state=0x0001)))
        self.assertTrue(multi_select_modifier(app, SimpleNamespace(state=0x0004)))
        app.template_ctrl_down = True
        self.assertTrue(multi_select_modifier(app, SimpleNamespace(state=0)))

    def test_toggle_selection_updates_primary_field(self):
        app = SimpleNamespace(template_selected_fields={1, 2}, template_selected_field=2)
        toggle_selection(app, 2)
        self.assertEqual(app.template_selected_fields, {1})
        self.assertEqual(app.template_selected_field, 1)
        toggle_selection(app, 3)
        self.assertEqual(app.template_selected_fields, {1, 3})
        self.assertEqual(app.template_selected_field, 3)

    def test_marquee_start_resets_drag_state_and_draws_rectangle(self):
        canvas = Mock()
        canvas.create_rectangle.return_value = "marquee"
        app = SimpleNamespace(
            template_canvas=canvas,
            template_marquee_clear=Mock(),
            template_drag_mode="move",
            template_drag_start=(1, 1),
            template_drag_original={"x": 1},
            template_group_drag_originals={0: {}},
        )
        event = SimpleNamespace(x=10, y=20)
        marquee_start_select(app, event, add_mode=True)
        self.assertEqual(app.template_marquee_item, "marquee")
        self.assertTrue(app.template_marquee_active)
        self.assertTrue(app.template_marquee_add_mode)
        self.assertIsNone(app.template_drag_mode)

    def test_marquee_selects_intersections_and_skips_hidden_fields(self):
        fields = [
            {"name": "Inside"},
            {"name": "Outside"},
            {"name": "Hidden", "hidden": True},
        ]
        rects = {
            "Inside": (10, 10, 30, 30),
            "Outside": (100, 100, 120, 120),
            "Hidden": (15, 15, 25, 25),
        }
        app = SimpleNamespace(
            template_marquee_active=True,
            template_marquee_start=(0, 0),
            template_marquee_add_mode=False,
            template_marquee_clear=Mock(),
            template_current=Mock(return_value={"fields": fields}),
            template_field_screen_rect=lambda field: rects[field["name"]],
            template_selected_fields={1},
            template_selected_field=1,
            template_refresh_selection_ui=Mock(),
        )

        self.assertTrue(marquee_finish(app, SimpleNamespace(x=50, y=50)))
        self.assertEqual(app.template_selected_fields, {0})
        self.assertEqual(app.template_selected_field, 0)
        app.template_refresh_selection_ui.assert_called_once_with()

    def test_additive_marquee_keeps_existing_selection(self):
        field = {"name": "New"}
        app = SimpleNamespace(
            template_marquee_active=True,
            template_marquee_start=(0, 0),
            template_marquee_add_mode=True,
            template_marquee_clear=Mock(),
            template_current=Mock(return_value={"fields": [field]}),
            template_field_screen_rect=Mock(return_value=(5, 5, 15, 15)),
            template_selected_fields={3},
            template_selected_field=3,
            template_refresh_selection_ui=Mock(),
        )
        marquee_finish(app, SimpleNamespace(x=20, y=20))
        self.assertEqual(app.template_selected_fields, {0, 3})


if __name__ == "__main__":
    unittest.main()
