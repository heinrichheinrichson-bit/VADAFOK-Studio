import tempfile
import unittest
from pathlib import Path

from PIL import Image

from vadafok_studio.library.preview_view import _load_thumbnail, preview_bounds


class LibraryPreviewImageTests(unittest.TestCase):
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
