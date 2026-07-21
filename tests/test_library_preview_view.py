import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PIL import Image

from vadafok_studio.library.preview_view import (
    GOLD, _load_thumbnail, preview_bounds, select_library_item,
)


class LibraryPreviewImageTests(unittest.TestCase):
    @patch("vadafok_studio.library.preview_view.ctk.CTkImage")
    @patch("vadafok_studio.library.preview_view.ctk.CTkLabel")
    def test_selection_updates_card_borders_without_rebuilding_grid(self, label, _image):
        previous = SimpleNamespace(kind="image", path=Path("old.png"), name="Old")
        selected = SimpleNamespace(
            kind="image", path=Path("new.png"), name="New",
            section="Banners", category="Root", relative="Banners/new.png",
        )
        old_card = Mock()
        new_card = Mock()
        frame = Mock()
        frame.winfo_children.return_value = []
        frame.winfo_width.return_value = 400
        frame.winfo_height.return_value = 400
        app = SimpleNamespace(
            selected_item=previous,
            preview_refs=[],
            selection_preview=frame,
            selection_name=Mock(),
            selection_meta=Mock(),
            library_asset_cards={"old": old_card, "new": new_card},
            item_key=lambda item: "old" if item is previous else "new",
            item_is_favorite=lambda _item: False,
            item_tags=lambda _item: [],
            render_library_grid=Mock(),
        )
        with patch(
            "vadafok_studio.library.preview_view._load_thumbnail",
            return_value=Image.new("RGBA", (10, 10)),
        ):
            select_library_item(app, selected)

        old_card.configure.assert_called_once_with(border_color="#151515")
        new_card.configure.assert_called_once_with(border_color=GOLD)
        app.render_library_grid.assert_not_called()
    def test_preview_uses_available_frame_space_with_margin(self):
        self.assertEqual(preview_bounds(480, 640), (452, 612))

    def test_preview_size_is_capped_for_very_large_windows(self):
        self.assertEqual(preview_bounds(1200, 1000), (560, 640))

    def test_thumbnail_does_not_keep_source_file_open(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "preview.png"
            Image.new("RGB", (640, 360), "gold").save(path)

            thumbnail = _load_thumbnail(path, (220, 124))
            path.unlink()

            self.assertLessEqual(thumbnail.width, 220)
            self.assertLessEqual(thumbnail.height, 124)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
