import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from vadafok_studio.card_creator.render_service import CardRenderService


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class CardRenderServiceTests(unittest.TestCase):
    def test_empty_template_has_no_background(self):
        app = SimpleNamespace(card_selected_template=Variable(""))
        service = CardRenderService(app, Mock(), Mock(), Mock())

        self.assertEqual(service.resolve_background_path(), "")

    def test_configured_background_has_priority(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            configured = folder / "configured.png"
            configured.write_bytes(b"image")
            fallback = folder / "background.png"
            fallback.write_bytes(b"fallback")
            app = SimpleNamespace(card_selected_template=Variable("Default"))
            service = CardRenderService(
                app,
                Mock(return_value={}),
                Mock(return_value=configured),
                Mock(return_value=folder),
            )

            self.assertEqual(service.resolve_background_path(), str(configured))

    def test_named_fallback_precedes_other_images(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            named = folder / "background.jpg"
            named.write_bytes(b"named")
            other = folder / "other.png"
            other.write_bytes(b"other")
            app = SimpleNamespace(card_selected_template=Variable("Default"))
            service = CardRenderService(
                app,
                Mock(return_value={}),
                Mock(return_value=folder / "missing.png"),
                Mock(return_value=folder),
            )

            self.assertEqual(service.resolve_background_path(), str(named))

    def test_first_supported_image_is_last_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            image = folder / "custom.webp"
            image.write_bytes(b"image")
            app = SimpleNamespace(card_selected_template=Variable("Default"))
            service = CardRenderService(
                app,
                Mock(return_value={}),
                Mock(return_value=folder / "missing.png"),
                Mock(return_value=folder),
            )

            self.assertEqual(service.resolve_background_path(), str(image))
