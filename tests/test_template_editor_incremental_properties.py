from __future__ import annotations

import ast
from pathlib import Path
import unittest


APP_PATH = Path(__file__).resolve().parents[1] / "vadafok_studio" / "app.py"


class TemplateEditorIncrementalPropertiesTests(unittest.TestCase):
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

    def test_properties_panel_caches_widgets(self):
        source = self.function_source("template_build_properties_panel")
        self.assertIn("_template_properties_body_ref", source)
        self.assertIn("_template_properties_editor", source)
        self.assertIn("cache_valid", source)

    def test_selection_switches_visibility_instead_of_rebuilding_widgets(self):
        source = self.function_source("template_build_properties_panel")
        self.assertIn("editor.grid_remove()", source)
        self.assertIn("empty_label.grid_remove()", source)
        self.assertEqual(source.count("widget.destroy()"), 1)

    def test_selection_refresh_still_loads_values_before_panel_state(self):
        source = self.function_source("template_refresh_selection_ui")
        self.assertLess(
            source.index("template_load_selected_properties"),
            source.index("template_build_properties_panel"),
        )


if __name__ == "__main__":
    unittest.main()
