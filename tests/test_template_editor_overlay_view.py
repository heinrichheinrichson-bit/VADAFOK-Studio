from pathlib import Path
from types import SimpleNamespace
import ast
import unittest
from unittest.mock import Mock

from vadafok_studio.template_editor.overlay_view import update_fields_overlay


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"


class TemplateEditorOverlayViewTests(unittest.TestCase):
    def test_app_delegates_overlay_rendering(self):
        source = APP_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "return update_fields_overlay(self, bg_info, refresh_layers, refresh_status)",
            source,
        )
        tree = ast.parse(source)
        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "template_update_fields_overlay"
        )
        self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)

    def test_missing_canvas_is_safe(self):
        app = SimpleNamespace(template_current=Mock())
        update_fields_overlay(app)
        app.template_current.assert_not_called()

    def test_hidden_fields_are_skipped_and_selected_field_gets_handles(self):
        canvas = Mock()
        fields = [
            {"name": "Visible", "hidden": False, "uppercase": True, "font_size": 50},
            {"name": "Hidden", "hidden": True},
        ]
        app = SimpleNamespace(
            template_canvas=canvas,
            template_clear_fields_overlay=Mock(),
            template_clear_smart_guides=Mock(),
            template_current=Mock(return_value={"fields": fields}),
            template_selected_field=0,
            template_selected_fields={0},
            template_field_screen_rect=Mock(return_value=(10, 20, 110, 70)),
            template_handle_points=Mock(
                return_value=[("nw", 10, 20), ("se", 110, 70)]
            ),
            template_selected_name="Template",
        )

        update_fields_overlay(
            app,
            {"name": "bg.png", "exists": True},
            refresh_layers=False,
            refresh_status=False,
        )

        app.template_field_screen_rect.assert_called_once_with(fields[0])
        self.assertEqual(canvas.create_rectangle.call_count, 3)
        self.assertEqual(canvas.create_text.call_count, 2)

    def test_refresh_flags_skip_status_and_layers(self):
        app = SimpleNamespace(
            template_canvas=Mock(),
            template_clear_fields_overlay=Mock(),
            template_clear_smart_guides=Mock(),
            template_current=Mock(return_value={"fields": []}),
            template_selected_field=None,
            template_selected_fields=set(),
            template_status_label=Mock(),
            template_layers_body=Mock(),
            template_build_layers_panel=Mock(),
        )

        update_fields_overlay(
            app, {"name": "bg.png"}, refresh_layers=False, refresh_status=False
        )

        app.template_status_label.configure.assert_not_called()
        app.template_build_layers_panel.assert_not_called()


if __name__ == "__main__":
    unittest.main()
