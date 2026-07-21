from pathlib import Path
from types import SimpleNamespace
import ast
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.template_editor.properties_view import build_properties_panel


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
VIEW_PATH = ROOT / "vadafok_studio" / "template_editor" / "properties_view.py"


class TemplateEditorPropertiesViewTests(unittest.TestCase):
    def test_app_delegates_properties_panel_rendering(self):
        source = APP_PATH.read_text(encoding="utf-8")
        view_source = VIEW_PATH.read_text(encoding="utf-8")
        self.assertIn("return build_properties_panel(self)", source)
        self.assertIn('text="Uppercase"', view_source)
        tree = ast.parse(source)
        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "template_build_properties_panel"
        )
        self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)

    def test_missing_properties_body_is_safe(self):
        build_properties_panel(SimpleNamespace())

    @patch("vadafok_studio.template_editor.properties_view.ctk.CTkLabel")
    @patch("vadafok_studio.template_editor.properties_view.ctk.CTkFrame")
    def test_valid_cache_is_reused_for_selected_field(self, frame_class, label_class):
        body = Mock()
        editor = Mock()
        empty_label = Mock()
        editor.winfo_exists.return_value = True
        empty_label.winfo_exists.return_value = True
        app = SimpleNamespace(
            template_props_body=body,
            _template_properties_body_ref=body,
            _template_properties_editor=editor,
            _template_properties_empty_label=empty_label,
            template_selected_field=0,
        )

        build_properties_panel(app)

        body.winfo_children.assert_not_called()
        frame_class.assert_not_called()
        label_class.assert_not_called()
        empty_label.grid_remove.assert_called_once_with()
        editor.grid.assert_called_once_with()

    def test_empty_selection_hides_cached_editor(self):
        body = Mock()
        editor = Mock()
        empty_label = Mock()
        editor.winfo_exists.return_value = True
        empty_label.winfo_exists.return_value = True
        app = SimpleNamespace(
            template_props_body=body,
            _template_properties_body_ref=body,
            _template_properties_editor=editor,
            _template_properties_empty_label=empty_label,
            template_selected_field=None,
        )

        build_properties_panel(app)

        editor.grid_remove.assert_called_once_with()
        empty_label.grid.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
