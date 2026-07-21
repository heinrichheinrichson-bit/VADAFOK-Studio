from pathlib import Path
from types import SimpleNamespace
import ast
import unittest
from unittest.mock import Mock

from vadafok_studio.template_editor.smart_guides import (
    apply_smart_snap,
    draw_smart_guides,
    field_edges,
    screen_line_x,
    screen_line_y,
    smart_targets,
)


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class TemplateEditorSmartGuidesTests(unittest.TestCase):
    def test_app_smart_guide_methods_are_thin_adapters(self):
        source = APP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        methods = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name.startswith("template_")
            and ("smart" in node.name or "screen_line" in node.name or node.name == "template_field_edges")
        ]
        self.assertTrue(methods)
        self.assertEqual(
            [(node.name, node.end_lineno - node.lineno + 1) for node in methods if node.end_lineno - node.lineno + 1 > 2],
            [],
        )

    def test_screen_conversion_respects_offset_and_scale(self):
        app = SimpleNamespace(template_canvas_offset=(10, 20), template_canvas_scale=1.5)
        self.assertEqual(screen_line_x(app, 100), 160)
        self.assertEqual(screen_line_y(app, 100), 170)

    def test_field_edges_include_centers(self):
        self.assertEqual(
            field_edges(None, {"x": 10, "y": 20, "width": 100, "height": 40}),
            {"left": 10, "center_x": 60, "right": 110, "top": 20, "center_y": 40, "bottom": 60},
        )

    def test_targets_skip_selected_and_hidden_fields(self):
        fields = [
            {"x": 0, "y": 0, "width": 10, "height": 10},
            {"x": 20, "y": 20, "width": 10, "height": 10, "hidden": True},
            {"x": 40, "y": 40, "width": 20, "height": 20},
        ]
        app = SimpleNamespace(
            template_current=Mock(return_value={"fields": fields}),
            template_canvas_design_size=(200, 100),
            template_selected_field=0,
            template_field_edges=lambda field: field_edges(None, field),
        )
        targets_x, targets_y = smart_targets(app)
        self.assertIn(("template_center_x", 100), targets_x)
        self.assertIn(("field2_left", 40), targets_x)
        self.assertNotIn(("field0_left", 0), targets_x)
        self.assertNotIn(("field1_left", 20), targets_x)
        self.assertIn(("field2_center_y", 50), targets_y)

    def test_move_snaps_inside_tolerance_but_not_outside(self):
        app = SimpleNamespace(
            template_smart_snap_enabled=Variable(True),
            template_smart_guides_enabled=Variable(True),
            template_smart_guide_tolerance=8,
            template_smart_targets=Mock(return_value=([("line", 100)], [])),
        )
        self.assertEqual(apply_smart_snap(app, 93, 10, 0, 20, "move"), (100, 10, 0, 20, [100], []))
        self.assertEqual(apply_smart_snap(app, 91, 10, 0, 20, "move"), (91, 10, 0, 20, [], []))

    def test_disabled_snap_returns_input_unchanged(self):
        app = SimpleNamespace(template_smart_snap_enabled=Variable(False))
        self.assertEqual(apply_smart_snap(app, 1, 2, 3, 4, "move"), (1, 2, 3, 4, [], []))

    def test_guides_remain_visible_when_snap_is_disabled(self):
        app = SimpleNamespace(
            template_smart_snap_enabled=Variable(False),
            template_smart_guides_enabled=Variable(True),
            template_smart_guide_tolerance=8,
            template_smart_targets=Mock(return_value=([("line", 100)], [])),
        )
        self.assertEqual(
            apply_smart_snap(app, 93, 10, 0, 20, "move"),
            (93, 10, 0, 20, [100], []),
        )

    def test_snap_remains_active_when_guides_are_disabled(self):
        app = SimpleNamespace(
            template_smart_snap_enabled=Variable(True),
            template_smart_guides_enabled=Variable(False),
            template_smart_guide_tolerance=8,
            template_smart_targets=Mock(return_value=([("line", 100)], [])),
        )
        self.assertEqual(
            apply_smart_snap(app, 93, 10, 0, 20, "move"),
            (100, 10, 0, 20, [], []),
        )

    def test_disabled_guides_clear_existing_lines_without_drawing(self):
        canvas = Mock()
        app = SimpleNamespace(
            template_canvas=canvas,
            template_smart_guides_enabled=Variable(False),
        )
        draw_smart_guides(app, [10], [20])
        canvas.delete.assert_called_once_with("template_smart_guide")
        canvas.create_line.assert_not_called()


if __name__ == "__main__":
    unittest.main()
