import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from vadafok_studio.banner_workflow import _load_banner_slots


class LiveCardBannerSlotTests(unittest.TestCase):
    def test_configured_slots_preserve_position_and_empty_places(self):
        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / "first.png"
            third = Path(folder) / "third.png"
            first.write_bytes(b"image")
            third.write_bytes(b"image")
            app = SimpleNamespace(config_data={
                "live_card_banner_slots": [str(first), "", str(third), ""],
                "live_card_banner_slots_initialized": True,
            })

            slots = _load_banner_slots(app)

            self.assertEqual(slots[0].path, first)
            self.assertIsNone(slots[1])
            self.assertEqual(slots[2].path, third)
            self.assertIsNone(slots[3])

    def test_initialized_empty_slots_stay_empty(self):
        app = SimpleNamespace(config_data={
            "live_card_banner_slots": ["", "", "", ""],
            "live_card_banner_slots_initialized": True,
        })
        self.assertEqual(_load_banner_slots(app), [None, None, None, None])


if __name__ == "__main__":
    unittest.main()
