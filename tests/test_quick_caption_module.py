import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class QuickCaptionModuleTests(unittest.TestCase):
    def test_app_delegates_compact_window_to_module(self):
        text = (ROOT / "vadafok_studio/app.py").read_text(encoding="utf-8")
        tree = ast.parse(text)
        studio = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio")
        method = next(node for node in studio.body if isinstance(node, ast.FunctionDef) and node.name == "open_quick_caption")
        self.assertLessEqual(method.end_lineno - method.lineno + 1, 8)
        block = ast.get_source_segment(text, method)
        self.assertIn("open_quick_caption_window(self)", block)

    def test_compact_window_remains_separate_from_large_live_card_page(self):
        text = (ROOT / "vadafok_studio/quick_caption/window.py").read_text(encoding="utf-8")
        self.assertIn('app.show_live_card()', text)
        self.assertIn('app.set_message(text)', text)
        self.assertIn('app.show_card()', text)
        self.assertIn('text="ENGLISH"', text)
        self.assertIn('geometry("520x340")', text)


if __name__ == "__main__":
    unittest.main()
