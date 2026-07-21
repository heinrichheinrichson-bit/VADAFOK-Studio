import tempfile
import unittest
from pathlib import Path

from PIL import Image

from vadafok_studio.core import export_engine


class ExportEngineAtomicTests(unittest.TestCase):
    def test_profile_save_replaces_target_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            target = folder / "card.png"
            target.write_bytes(b"old")

            export_engine.save_with_profile(
                Image.new("RGBA", (8, 8), "white"),
                target,
                "Broadcast PNG",
            )

            self.assertGreater(target.stat().st_size, 3)
            self.assertEqual(list(folder.glob(".card.*.tmp.png")), [])


if __name__ == "__main__":
    unittest.main()
