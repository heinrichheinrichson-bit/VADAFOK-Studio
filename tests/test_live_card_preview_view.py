import tempfile
import unittest
from pathlib import Path

from PIL import Image

from vadafok_studio.live_card.preview_view import _load_preview_image


class LiveCardPreviewImageTests(unittest.TestCase):
    def test_preview_does_not_lock_rendered_png(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "caption.png"
            Image.new("RGB", (1000, 400), "black").save(path)
            preview = _load_preview_image(path)
            path.unlink()
            self.assertLessEqual(preview.width, 520)
            self.assertLessEqual(preview.height, 300)
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
