import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.library import asset_actions


class LibraryAssetActionTests(unittest.TestCase):
    def make_app(self):
        item = SimpleNamespace(relative="Banners/example.png", path="example.png")
        return SimpleNamespace(
            selected_item=item,
            asset_meta={"favorites": [], "tags": {}},
            item_key=lambda selected: selected.relative,
            select_library_item=Mock(),
        )

    @patch.object(asset_actions, "save_asset_meta")
    def test_toggle_favorite_adds_and_removes_selected_asset(self, save):
        app = self.make_app()
        asset_actions.toggle_favorite(app)
        self.assertEqual(app.asset_meta["favorites"], ["Banners/example.png"])
        asset_actions.toggle_favorite(app)
        self.assertEqual(app.asset_meta["favorites"], [])
        self.assertEqual(save.call_count, 2)

    @patch.object(asset_actions, "save_asset_meta")
    @patch.object(asset_actions.simpledialog, "askstring")
    def test_edit_tags_trims_and_removes_case_insensitive_duplicates(self, ask, save):
        app = self.make_app()
        ask.return_value = " Ending, ending, Stream , "
        asset_actions.edit_tags(app)
        self.assertEqual(
            app.asset_meta["tags"]["Banners/example.png"],
            ["Ending", "Stream"],
        )
        save.assert_called_once_with(app.asset_meta)
        app.select_library_item.assert_called_once_with(app.selected_item)


if __name__ == "__main__":
    unittest.main()
