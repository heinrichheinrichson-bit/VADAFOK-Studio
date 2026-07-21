from pathlib import Path
from types import SimpleNamespace
import ast
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.template_editor.controller import TemplateEditorController


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
PAGE_PATH = ROOT / "vadafok_studio" / "template_editor" / "page.py"


class TemplateEditorPageTests(unittest.TestCase):
    def test_app_routes_page_through_controller(self):
        app_source = APP_PATH.read_text(encoding="utf-8")
        page_source = PAGE_PATH.read_text(encoding="utf-8")
        self.assertIn("return self.template_editor_controller.show_page()", app_source)
        self.assertNotIn('page_title("Template Editor")', app_source)
        self.assertIn('page_title("Template Editor")', page_source)
        tree = ast.parse(app_source)
        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "show_template_editor_page"
        )
        self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)

    @patch("vadafok_studio.template_editor.controller.show_template_editor_page")
    def test_controller_delegates_to_page_builder(self, page_builder):
        app = SimpleNamespace()
        page_builder.return_value = Mock()
        controller = TemplateEditorController(app, Mock(return_value=[]), Mock())
        self.assertIs(controller.show_page(), page_builder.return_value)
        page_builder.assert_called_once_with(app)


if __name__ == "__main__":
    unittest.main()
