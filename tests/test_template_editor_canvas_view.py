from pathlib import Path
from types import SimpleNamespace
import ast
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.template_editor.canvas_view import draw_canvas


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"


class TemplateEditorCanvasViewTests(unittest.TestCase):
    def test_app_delegates_canvas_drawing(self):
        source = APP_PATH.read_text(encoding="utf-8")
        self.assertIn("return draw_canvas(self, refresh_layers)", source)
        tree = ast.parse(source)
        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "template_draw_canvas"
        )
        self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)

    def test_missing_canvas_is_safe(self):
        app = SimpleNamespace(template_current=Mock())
        draw_canvas(app)
        app.template_current.assert_not_called()

    @patch("vadafok_studio.template_editor.canvas_view.image_status")
    @patch("vadafok_studio.template_editor.canvas_view.background_path")
    def test_missing_background_draws_fallback_and_overlay(self, background, status):
        background.return_value = ""
        status.return_value = {"exists": False, "name": "-", "size": None}
        canvas = Mock()
        canvas.winfo_width.return_value = 800
        canvas.winfo_height.return_value = 500
        app = SimpleNamespace(
            template_canvas=canvas,
            template_current=Mock(return_value={"fields": []}),
            template_selected_name="Template",
            template_zoom_factor=1.0,
            template_pan_x=0,
            template_pan_y=0,
            template_update_fields_overlay=Mock(),
        )

        draw_canvas(app, refresh_layers=False)

        canvas.delete.assert_called_once_with("all")
        canvas.create_rectangle.assert_called_once()
        app.template_update_fields_overlay.assert_called_once_with(
            status.return_value, refresh_layers=False
        )


if __name__ == "__main__":
    unittest.main()
