import tempfile
import unittest
from pathlib import Path

from PIL import Image

from vadafok_studio.library.preview_view import _load_thumbnail


class LibraryPreviewImageTests(unittest.TestCase):
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
