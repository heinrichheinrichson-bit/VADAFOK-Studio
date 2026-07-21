import ast
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PIL import Image

from vadafok_studio.card_creator.preview import CardPreviewController


class CardPreviewControllerTests(unittest.TestCase):
    def test_update_without_preview_frame_is_safe(self):
        app = SimpleNamespace(card_preview_update_job="queued")

        CardPreviewController(app, Mock(), Mock()).update()

        self.assertIsNone(app.card_preview_update_job)

    def test_update_renders_real_background_and_updates_widgets(self):
        with tempfile.TemporaryDirectory() as temporary:
            background = Path(temporary) / "background.png"
            Image.new("RGBA", (320, 180), "black").save(background)
            rendered = Image.new("RGBA", (320, 180), "white")
            export_engine = Mock()
            export_engine.apply_export_profile.return_value = rendered
            export_engine.get_export_profile.return_value = {
                "format": "PNG",
                "size": None,
            }
            render_image = Mock(return_value=rendered)
            preview_info = Mock()
            profile_info = Mock()
            label = Mock()
            label.winfo_exists.return_value = True
            app = SimpleNamespace(
                card_preview_update_job="queued",
                card_preview_frame=Mock(),
                card_background_path=Mock(return_value=str(background)),
                card_selected_template=SimpleNamespace(get=lambda: "Default"),
                card_export_profile=SimpleNamespace(get=lambda: "Broadcast PNG"),
                card_preview_background_key=None,
                card_preview_background_cache=None,
                card_template=Mock(return_value={"fields": []}),
                card_values_plain=Mock(return_value={"title": "Hello"}),
                card_preview_info=preview_info,
                card_export_profile_info=profile_info,
                card_creator_preview_image=None,
                card_creator_preview_label=label,
            )

            with patch(
                "vadafok_studio.card_creator.preview.ctk.CTkImage",
                return_value=Mock(),
            ) as image_widget:
                CardPreviewController(app, export_engine, render_image).update()

            self.assertIsNone(app.card_preview_update_job)
            self.assertIsNotNone(app.card_preview_background_cache)
            render_image.assert_called_once()
            export_engine.apply_export_profile.assert_called_once_with(
                rendered, "Broadcast PNG"
            )
            image_widget.assert_called_once()
            preview_info.configure.assert_called_once_with(
                text="Default | 320×180 | Broadcast PNG"
            )
            profile_info.configure.assert_called_once_with(
                text="PNG | Originalgröße"
            )
            label.configure.assert_called_once()

    def test_app_preview_method_is_thin_adapter(self):
        app_path = Path(__file__).resolve().parents[1] / "vadafok_studio" / "app.py"
        source = app_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        studio = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio"
        )
        method = next(
            node for node in studio.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "card_update_preview"
        )
        block = ast.get_source_segment(source, method)

        self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)
        self.assertIn("return self.card_preview_controller.update()", block)
