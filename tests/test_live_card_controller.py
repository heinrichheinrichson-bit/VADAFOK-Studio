import sys
import types
from unittest.mock import Mock, patch

sys.modules.setdefault("customtkinter", types.SimpleNamespace())

from vadafok_studio.live_card.controller import LiveCardController


def test_open_quick_caption_delegates_to_compact_window():
    app = Mock()
    controller = LiveCardController(app)
    with patch("vadafok_studio.quick_caption.window.open_quick_caption_window", return_value="window") as opener:
        result = controller.open_quick_caption()
    assert result == "window"
    opener.assert_called_once_with(app)


def test_show_live_card_page_keeps_compatibility_alias():
    app = Mock()
    controller = LiveCardController(app)
    controller.show_live_card = Mock(return_value="live")
    assert controller.show_live_card_page() == "live"
    controller.show_live_card.assert_called_once_with()


def test_pending_live_card_text_is_preserved_until_widget_exists():
    app = Mock(spec=[])
    app.live_card_pending_text = ""
    controller = LiveCardController(app)
    controller.live_card_set_message_text("  Hello  ")
    assert app.live_card_pending_text == "Hello"
    assert controller.live_card_get_message_text() == "Hello"
