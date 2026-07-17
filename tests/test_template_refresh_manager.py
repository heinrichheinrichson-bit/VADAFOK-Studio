from __future__ import annotations

import ast
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "vadafok_studio" / "app.py"
MANAGER_PATH = PROJECT_ROOT / "vadafok_studio" / "template_editor" / "refresh_manager.py"


class TemplateRefreshManagerCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_source = APP_PATH.read_text(encoding="utf-8")
        cls.manager_source = MANAGER_PATH.read_text(encoding="utf-8")
        ast.parse(cls.app_source)
        ast.parse(cls.manager_source)

    def test_app_owns_refresh_manager(self):
        self.assertIn("self.template_refresh_manager = TemplateRefreshManager(self)", self.app_source)

    def test_manager_exposes_foundation_methods(self):
        for method in ("canvas", "overlay", "layers", "properties", "selection"):
            self.assertIn(f"def {method}(", self.manager_source)

    def test_legacy_selection_refresh_is_preserved(self):
        start = self.app_source.index("def template_refresh_selection_ui")
        end = self.app_source.index("def ", start + 4)
        method = self.app_source[start:end]
        self.assertIn("template_load_selected_properties", method)
        self.assertIn("template_build_properties_panel", method)
        self.assertIn("template_update_fields_overlay(refresh_layers=False)", method)
        self.assertIn("template_refresh_layers_selection", method)

    def test_legacy_template_switch_refresh_is_preserved(self):
        start = self.app_source.index("def template_refresh_selected_template")
        end = self.app_source.index("def template_build_properties_panel", start)
        method = self.app_source[start:end]
        for fragment in (
            "self.template_build_properties_panel()",
            "self.template_draw_canvas()",
            "self.template_build_layers_panel()",
        ):
            self.assertIn(fragment, method)


if __name__ == "__main__":
    unittest.main()
