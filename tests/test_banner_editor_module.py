import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
PAGE_PATH = ROOT / "vadafok_studio" / "banner_editor" / "page.py"


class BannerEditorModuleTests(unittest.TestCase):
    def test_app_delegates_banner_editor_page_to_module(self):
        source = APP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        studio = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio"
        )
        method = next(
            node
            for node in studio.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "show_banner_profiles_page"
        )
        block = ast.get_source_segment(source, method)
        self.assertLessEqual(method.end_lineno - method.lineno + 1, 5)
        self.assertIn("show_banner_profiles_page(self)", block)

    def test_banner_editor_page_preserves_existing_controls_and_callbacks(self):
        source = PAGE_PATH.read_text(encoding="utf-8")
        self.assertIn('text="SAVE PROFILE"', source)
        self.assertIn('text="RESET AREA"', source)
        self.assertIn('text="RESET STYLE"', source)
        self.assertIn("app.editor_mouse_down", source)
        self.assertIn("app.editor_mouse_drag", source)
        self.assertIn("app.editor_mouse_up", source)
        self.assertIn("app.editor_select_banner", source)
        self.assertIn("scan_library(app.project_folder.get())", source)


if __name__ == "__main__":
    unittest.main()
