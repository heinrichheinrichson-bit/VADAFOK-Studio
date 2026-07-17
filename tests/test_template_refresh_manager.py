from __future__ import annotations

import ast
from pathlib import Path
import unittest

from vadafok_studio.template_editor.refresh_manager import TemplateRefreshManager

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "vadafok_studio" / "app.py"
MANAGER_PATH = PROJECT_ROOT / "vadafok_studio" / "template_editor" / "refresh_manager.py"


class _FakeApp:
    def __init__(self, *, with_properties_body: bool = True):
        self.calls: list[tuple] = []
        self.template_layers_body = object()
        if with_properties_body:
            self.template_props_body = object()

    def template_load_selected_properties(self):
        self.calls.append(("load_properties",))

    def template_build_properties_panel(self):
        self.calls.append(("build_properties",))

    def template_update_fields_overlay(self, **kwargs):
        self.calls.append(("overlay", kwargs))

    def template_refresh_layers_selection(self):
        self.calls.append(("layers_selection",))

    def template_draw_canvas(self, **kwargs):
        self.calls.append(("canvas", kwargs))

    def template_build_layers_panel(self):
        self.calls.append(("layers_full",))


class TemplateRefreshManagerCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_source = APP_PATH.read_text(encoding="utf-8")
        cls.manager_source = MANAGER_PATH.read_text(encoding="utf-8")
        ast.parse(cls.app_source)
        ast.parse(cls.manager_source)

    def _selection_method(self) -> str:
        start = self.app_source.index("def template_refresh_selection_ui")
        end = self.app_source.index("def ", start + 4)
        return self.app_source[start:end]

    def test_app_owns_refresh_manager(self):
        self.assertIn(
            "self.template_refresh_manager = TemplateRefreshManager(self)",
            self.app_source,
        )

    def test_manager_exposes_foundation_methods(self):
        for method in ("canvas", "overlay", "layers", "properties", "selection"):
            self.assertIn(f"def {method}(", self.manager_source)

    def test_legacy_selection_wrapper_is_preserved(self):
        method = self._selection_method()
        expected = (
            "template_load_selected_properties",
            "template_build_properties_panel",
            "template_update_fields_overlay(refresh_layers=False)",
            "template_refresh_layers_selection",
        )
        for fragment in expected:
            self.assertIn(fragment, method)

    def test_legacy_selection_order_is_preserved(self):
        method = self._selection_method()
        positions = [
            method.index("template_load_selected_properties"),
            method.index("template_build_properties_panel"),
            method.index("template_update_fields_overlay(refresh_layers=False)"),
            method.index("template_refresh_layers_selection"),
        ]
        self.assertEqual(positions, sorted(positions))

    def test_manager_still_preserves_full_selection_refresh_order(self):
        app = _FakeApp()
        TemplateRefreshManager(app).selection(refresh_properties=True)
        self.assertEqual(
            app.calls,
            [
                ("load_properties",),
                ("build_properties",),
                (
                    "overlay",
                    {
                        "bg_info": None,
                        "refresh_layers": False,
                        "refresh_status": True,
                    },
                ),
                ("layers_selection",),
            ],
        )

    def test_manager_still_supports_selection_without_properties(self):
        app = _FakeApp()
        TemplateRefreshManager(app).selection(refresh_properties=False)
        self.assertEqual(
            app.calls,
            [
                (
                    "overlay",
                    {
                        "bg_info": None,
                        "refresh_layers": False,
                        "refresh_status": True,
                    },
                ),
                ("layers_selection",),
            ],
        )


if __name__ == "__main__":
    unittest.main()
