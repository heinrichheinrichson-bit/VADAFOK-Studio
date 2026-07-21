import ast
import unittest
from pathlib import Path


class CardFormViewTests(unittest.TestCase):
    def test_app_form_method_is_thin_adapter(self):
        root = Path(__file__).resolve().parents[1]
        app_path = root / "vadafok_studio" / "app.py"
        form_path = root / "vadafok_studio" / "card_creator" / "form_view.py"
        source = app_path.read_text(encoding="utf-8")
        form_source = form_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        studio = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio"
        )
        method = next(
            node for node in studio.body
            if isinstance(node, ast.FunctionDef) and node.name == "card_build_form"
        )
        block = ast.get_source_segment(source, method)

        self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)
        self.assertIn("return build_card_form(self)", block)
        self.assertIn("def build_card_form(app) -> None:", form_source)
        self.assertIn('trace_add("write", app.card_preview_changed)', form_source)
