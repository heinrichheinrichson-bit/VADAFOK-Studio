import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from PIL import Image

from vadafok_studio.live_card.preview_view import (
    _load_preview_image,
    schedule_render_preview,
)


class LiveCardPreviewImageTests(unittest.TestCase):
    def test_typing_preview_is_debounced(self):
        app = SimpleNamespace(
            live_preview_update_job="old",
            after_cancel=Mock(),
            after=Mock(return_value="new"),
            update_render_preview=Mock(),
        )
        schedule_render_preview(app)
        app.after_cancel.assert_called_once_with("old")
        app.after.assert_called_once_with(140, app.update_render_preview)
        self.assertEqual(app.live_preview_update_job, "new")

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
