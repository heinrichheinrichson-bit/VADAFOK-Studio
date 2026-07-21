import ast
from pathlib import Path
import unittest


APP_PATH = Path(__file__).resolve().parents[1] / "vadafok_studio" / "app.py"
SELECTION_PATH = (
    Path(__file__).resolve().parents[1]
    / "vadafok_studio"
    / "template_editor"
    / "selection_controller.py"
)
LAYER_PATH = (
    Path(__file__).resolve().parents[1]
    / "vadafok_studio"
    / "template_editor"
    / "layer_controller.py"
)


class TemplateEditorSelectionRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.functions = {
            node.name: node
            for node in ast.walk(cls.tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def function_source(self, name):
        node = self.functions[name]
        return ast.get_source_segment(self.source, node) or ""

    def test_partial_layers_selection_refresh_exists(self):
        source = LAYER_PATH.read_text(encoding="utf-8")
        self.assertIn("button.configure", source)
        self.assertIn("_template_layer_field_buttons", source)
        self.assertIn("_template_layer_group_buttons", source)

    def test_selection_refresh_does_not_rebuild_layers_directly(self):
        source = self.function_source("template_refresh_selection_ui")
        self.assertIn("template_update_fields_overlay(refresh_layers=False)", source)
        self.assertIn("template_refresh_layers_selection", source)
        self.assertNotIn("template_build_layers_panel()", source)

    def test_layer_selection_uses_partial_refresh(self):
        source = LAYER_PATH.read_text(encoding="utf-8")
        self.assertIn("template_refresh_selection_ui", source)
        select_method = source.split("def select_layer", 1)[1].split("def move_layer", 1)[0]
        self.assertNotIn("template_build_layers_panel", select_method)

    def test_marquee_selection_uses_shared_refresh(self):
        source = SELECTION_PATH.read_text(encoding="utf-8")
        self.assertIn("template_refresh_selection_ui", source)


if __name__ == "__main__":
    unittest.main()
