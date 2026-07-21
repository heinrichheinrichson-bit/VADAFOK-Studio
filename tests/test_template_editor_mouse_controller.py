from pathlib import Path
from types import SimpleNamespace
import ast
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.template_editor.mouse_controller import (
    handle_points,
    hit_test,
    mouse_drag,
    mouse_up,
)


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"


class TemplateEditorMouseControllerTests(unittest.TestCase):
    def test_app_mouse_methods_are_thin_adapters(self):
        tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
        names = {
            "template_handle_points",
            "template_hit_test",
            "template_cursor_for_mode",
            "template_mouse_motion",
            "template_mouse_down",
            "template_mouse_drag",
            "template_mouse_up",
        }
        large = [
            (node.name, node.end_lineno - node.lineno + 1)
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name in names
            and node.end_lineno - node.lineno + 1 > 2
        ]
        self.assertEqual(large, [])

    def test_handle_points_cover_all_edges_and_corners(self):
        points = handle_points(None, 10, 20, 110, 60)
        self.assertEqual([name for name, _x, _y in points], ["nw", "n", "ne", "w", "e", "sw", "s", "se"])
        self.assertIn(("n", 60, 20), points)

    def test_hit_test_prefers_selected_resize_handle(self):
        field = {"name": "Field"}
        app = SimpleNamespace(
            template_current=Mock(return_value={"fields": [field]}),
            template_selected_field=0,
            template_field_screen_rect=Mock(return_value=(10, 20, 110, 60)),
            template_handle_points=lambda *args: handle_points(None, *args),
        )
        self.assertEqual(hit_test(app, 10, 20), (0, "nw"))
        self.assertEqual(hit_test(app, 50, 40), (0, "move"))

    def test_group_drag_moves_all_fields_and_skips_expensive_refreshes(self):
        template = {
            "fields": [
                {"x": 10, "y": 20, "width": 100, "height": 50},
                {"x": 200, "y": 100, "width": 80, "height": 40},
            ]
        }
        app = SimpleNamespace(
            template_marquee_drag=Mock(return_value=False),
            template_selected_field=0,
            template_drag_original=dict(template["fields"][0]),
            template_drag_start=(0, 0),
            template_canvas_scale=1.0,
            template_group_drag_originals={
                0: dict(template["fields"][0]),
                1: dict(template["fields"][1]),
            },
            template_drag_mode="move",
            template_canvas_design_size=(500, 300),
            template_current=Mock(return_value=template),
            template_update_fields_overlay=Mock(),
        )

        mouse_drag(app, SimpleNamespace(x=15, y=10))

        self.assertEqual((template["fields"][0]["x"], template["fields"][0]["y"]), (25, 30))
        self.assertEqual((template["fields"][1]["x"], template["fields"][1]["y"]), (215, 110))
        app.template_update_fields_overlay.assert_called_once_with(
            refresh_layers=False, refresh_status=False
        )

    @patch("vadafok_studio.template_editor.mouse_controller.save_template")
    def test_mouse_up_records_one_undo_snapshot_and_saves(self, save):
        before = {"fields": [{"x": 0}]}
        current = {"fields": [{"x": 10}]}
        app = SimpleNamespace(
            template_marquee_finish=Mock(return_value=False),
            template_clear_smart_guides=Mock(),
            template_drag_history_snapshot=before,
            template_current=Mock(return_value=current),
            template_undo_stack=[],
            template_redo_stack=[{"old": True}],
            template_history_limit=80,
            template_selected_name="Template",
            template_update_fields_overlay=Mock(),
            template_drag_mode="move",
            template_drag_start=(0, 0),
            template_drag_original={"x": 0},
            template_group_drag_originals=None,
        )

        mouse_up(app, SimpleNamespace())

        self.assertEqual(app.template_undo_stack, [before])
        self.assertEqual(app.template_redo_stack, [])
        save.assert_called_once_with("Template", current)
        self.assertIsNone(app.template_drag_history_snapshot)


if __name__ == "__main__":
    unittest.main()
