from pathlib import Path
import ast
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
PAGE_PATH = ROOT / "vadafok_studio" / "silent_director" / "page.py"


class SilentDirectorPageTests(unittest.TestCase):
    def test_app_delegates_page_construction(self):
        app_source = APP_PATH.read_text(encoding="utf-8")
        page_source = PAGE_PATH.read_text(encoding="utf-8")

        self.assertIn("show_silent_director_page as build_silent_director_page", app_source)
        self.assertIn("return build_silent_director_page(self)", app_source)
        self.assertNotIn('text="Director Presets"', app_source)
        self.assertIn('text="Director Presets"', page_source)

    def test_app_page_method_is_a_thin_adapter(self):
        tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "show_silent_director_page"
        )
        self.assertLessEqual(method.end_lineno - method.lineno + 1, 3)


if __name__ == "__main__":
    unittest.main()
