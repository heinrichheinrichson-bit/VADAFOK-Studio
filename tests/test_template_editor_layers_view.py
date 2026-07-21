from pathlib import Path
from types import SimpleNamespace
import ast
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.template_editor.layers_view import build_layers_panel


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"


class TemplateEditorLayersViewTests(unittest.TestCase):
    def test_app_delegates_layer_panel_rendering(self):
        source = APP_PATH.read_text(encoding="utf-8")
        self.assertIn("return build_layers_panel(self)", source)
        self.assertNotIn('text="Keine Felder"', source)

        tree = ast.parse(source)
        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "template_build_layers_panel"
        )
        self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)

    @patch("vadafok_studio.template_editor.layers_view.ctk.CTkLabel")
    def test_empty_template_clears_old_rows_and_shows_hint(self, label):
        old_row = Mock()
        body = Mock()
        body.winfo_children.return_value = [old_row]
        app = SimpleNamespace(
            template_layers_body=body,
            template_current=Mock(return_value={"fields": [], "groups": []}),
            template_clean_groups=Mock(),
            template_selected_fields=set(),
            template_selected_field=None,
        )

        build_layers_panel(app)

        old_row.destroy.assert_called_once_with()
        self.assertEqual(label.call_args.kwargs["text"], "Keine Felder")
        self.assertEqual(app._template_layer_row_for_group, {})
        self.assertEqual(app._template_layer_row_for_field, {})

    def test_missing_layer_body_is_safe(self):
        app = SimpleNamespace(template_current=Mock())

        build_layers_panel(app)

        app.template_current.assert_not_called()


if __name__ == "__main__":
    unittest.main()
