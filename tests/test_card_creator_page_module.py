import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
PAGE_PATH = ROOT / "vadafok_studio" / "card_creator" / "page.py"


class CardCreatorPageModuleTests(unittest.TestCase):
    def test_app_delegates_card_creator_page_to_module(self):
        source = APP_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        studio = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio"
        )
        method = next(
            node for node in studio.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "show_card_creator_page"
        )
        block = ast.get_source_segment(source, method)
        self.assertLessEqual(method.end_lineno - method.lineno + 1, 5)
        self.assertIn("show_card_creator_page(self)", block)

    def test_card_creator_page_preserves_existing_controls_and_callbacks(self):
        source = PAGE_PATH.read_text(encoding="utf-8")
        self.assertIn('text="UPDATE PREVIEW"', source)
        self.assertIn('text="RENDER CARD"', source)
        self.assertIn('text="IMPORT CSV/XLSX"', source)
        self.assertIn('text="SAVE PROJECT"', source)
        self.assertIn('text="LOAD PROJECT"', source)
        self.assertIn("app.card_build_form", source)
        self.assertIn("app.card_build_batch_panel", source)
        self.assertIn("app.card_update_preview", source)
        self.assertIn("list_templates()", source)


if __name__ == "__main__":
    unittest.main()
