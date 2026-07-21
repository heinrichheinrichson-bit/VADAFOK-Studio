from pathlib import Path
import unittest


class LiveCardModularizationTests(unittest.TestCase):
    def test_live_card_controller_is_wired_into_app(self):
        root = Path(__file__).resolve().parents[1]
        app = (root / "vadafok_studio" / "app.py").read_text(encoding="utf-8")
        controller = (root / "vadafok_studio" / "live_card" / "controller.py").read_text(encoding="utf-8")
        assert "from .live_card.controller import LiveCardController" in app
        assert "self.live_card_controller = LiveCardController(self)" in app
        assert "return self.live_card_controller.open_quick_caption()" in app
        assert "class LiveCardController" in controller
        assert "def show_live_card" in controller
