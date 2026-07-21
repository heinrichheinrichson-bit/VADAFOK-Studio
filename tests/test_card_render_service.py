import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from PIL import Image

from vadafok_studio.card_creator.render_service import CardRenderService


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class CardRenderServiceTests(unittest.TestCase):
    def make_service(
        self,
        app,
        folder,
        configured=None,
        render=None,
        export_engine=None,
    ):
        folder = Path(folder)
        return CardRenderService(
            app,
            Mock(return_value={}),
            Mock(return_value=configured or folder / "missing.png"),
            Mock(return_value=folder),
            folder,
            render or Mock(),
            export_engine or Mock(),
        )

    def test_empty_template_has_no_background(self):
        app = SimpleNamespace(card_selected_template=Variable(""))
        service = CardRenderService(
            app, Mock(), Mock(), Mock(), Path("exports"), Mock(), Mock()
        )

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
                folder,
                Mock(),
                Mock(),
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
                folder,
                Mock(),
                Mock(),
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
                folder,
                Mock(),
                Mock(),
            )

            self.assertEqual(service.resolve_background_path(), str(image))

    def test_render_to_file_applies_profile_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            background = folder / "background.png"
            Image.new("RGBA", (20, 10), "black").save(background)
            output = folder / "final.png"
            app = SimpleNamespace(
                card_selected_template=Variable("Default"),
                card_export_profile=Variable("Broadcast PNG"),
                card_template=Mock(return_value={"fields": []}),
                card_values_plain=Mock(return_value={"title": "Hello"}),
                card_output_path=Mock(return_value=output),
            )

            def render(_template, _values, path, _background, size=None):
                self.assertIsNone(size)
                Image.new("RGBA", (20, 10), "white").save(path)

            engine = Mock()
            service = self.make_service(
                app,
                folder,
                configured=background,
                render=Mock(side_effect=render),
                export_engine=engine,
            )

            result = service.render_to_file(final=True)

            self.assertEqual(result, output)
            engine.save_with_profile.assert_called_once()
            args = engine.save_with_profile.call_args.args
            self.assertEqual(args[1:], (output, "Broadcast PNG"))
            self.assertFalse(
                (folder / "_vadafok_card_temp_profile_source.png").exists()
            )
