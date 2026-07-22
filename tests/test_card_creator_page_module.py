import ast
import unittest
from pathlib import Path
from unittest.mock import Mock

from vadafok_studio.card_creator.page import _widgets_exist

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
PAGE_PATH = ROOT / "vadafok_studio" / "card_creator" / "page.py"


class CardCreatorPageModuleTests(unittest.TestCase):
    def test_destroyed_batch_row_widgets_are_rejected(self):
        live = Mock()
        live.winfo_exists.return_value = 1
        destroyed = Mock()
        destroyed.winfo_exists.return_value = 0
        self.assertTrue(_widgets_exist((live,)))
        self.assertFalse(_widgets_exist((live, destroyed)))

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
        self.assertIn('text="VORSCHAU AKTUALISIEREN"', source)
        self.assertIn('text="KARTE RENDERN"', source)
        self.assertIn('text="IMPORT CSV/XLSX"', source)
        self.assertIn('text="SAVE PROJECT"', source)
        self.assertIn('text="LOAD PROJECT"', source)
        self.assertIn("app.card_build_form", source)
        self.assertIn("app.card_build_batch_panel", source)
        self.assertIn("app.card_update_preview", source)
        self.assertIn("list_templates()", source)

    def test_batch_panel_rendering_is_owned_by_page_module(self):
        app_source = APP_PATH.read_text(encoding="utf-8")
        page_source = PAGE_PATH.read_text(encoding="utf-8")
        app_tree = ast.parse(app_source)
        studio = next(
            node for node in app_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio"
        )
        method = next(
            node for node in studio.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "card_build_batch_panel"
        )
        block = ast.get_source_segment(app_source, method)

        self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)
        self.assertIn("return build_batch_panel(self)", block)
        self.assertIn("def build_batch_panel(app):", page_source)
        self.assertIn("app.card_batch_select(index)", page_source)
        self.assertIn("state = app.card_creator_state", page_source)
        self.assertNotIn("app.card_batch_items", page_source)
        self.assertNotIn("app.card_batch_selected_index", page_source)
        self.assertIn("def update_batch_selection(app):", page_source)
        self.assertIn("app.card_batch_rows = rows", page_source)
        self.assertNotIn("for widget in app.card_batch_body.winfo_children()", page_source)
        self.assertIn("app.card_batch_rows = []", page_source)
        self.assertIn("def _widgets_exist(widgets)", page_source)


if __name__ == "__main__":
    unittest.main()
