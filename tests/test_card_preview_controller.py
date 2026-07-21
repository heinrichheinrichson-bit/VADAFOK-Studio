import ast
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PIL import Image

from vadafok_studio.card_creator.preview import CardPreviewController, preview_bounds
from vadafok_studio.card_creator.state import CardCreatorState


class CardPreviewControllerTests(unittest.TestCase):
    def test_preview_bounds_follow_available_space_and_are_capped(self):
        frame = SimpleNamespace(winfo_width=lambda: 1500, winfo_height=lambda: 1100)
        self.assertEqual(preview_bounds(frame), (1200, 960))

    def test_preview_bounds_fall_back_before_widget_has_geometry(self):
        frame = SimpleNamespace(winfo_width=lambda: 1, winfo_height=lambda: 1)
        self.assertEqual(preview_bounds(frame), (760, 620))

    def test_zoom_is_bounded_and_fit_resets_pan(self):
        app = SimpleNamespace(card_creator_state=CardCreatorState())
        controller = CardPreviewController(app, Mock(), Mock())
        controller._display_preview = Mock()
        controller.state.preview_zoom = 2.5
        controller.zoom_by(0.1)
        self.assertEqual(controller.state.preview_zoom, 2.5)
        controller.state.preview_pan_x = 20
        controller.state.preview_pan_y = -10
        controller.fit()
        self.assertEqual(controller.state.preview_zoom, 1.0)
        self.assertEqual((controller.state.preview_pan_x, controller.state.preview_pan_y), (0, 0))

    def test_changed_schedules_save_and_fast_preview(self):
        jobs = iter(("save-job", "preview-job"))
        app = SimpleNamespace(
            card_creator_state=CardCreatorState(),
            card_values_save_job="old-save",
            card_preview_update_job="old-preview",
            card_auto_preview=SimpleNamespace(get=lambda: True),
            card_save_values=Mock(),
            card_update_preview=Mock(),
            after=Mock(side_effect=lambda _delay, _callback: next(jobs)),
            after_cancel=Mock(),
        )

        CardPreviewController(app, Mock(), Mock()).changed()

        self.assertEqual(app.card_values_save_job, "save-job")
        self.assertEqual(app.card_preview_update_job, "preview-job")
        self.assertEqual(
            app.after.call_args_list[0].args,
            (350, app.card_save_values),
        )
        self.assertEqual(
            app.after.call_args_list[1].args,
            (25, app.card_update_preview),
        )
        self.assertEqual(app.after_cancel.call_count, 2)

    def test_changed_skips_preview_when_auto_preview_is_disabled(self):
        app = SimpleNamespace(
            card_creator_state=CardCreatorState(),
            card_values_save_job=None,
            card_preview_update_job=None,
            card_auto_preview=SimpleNamespace(get=lambda: False),
            card_save_values=Mock(),
            card_update_preview=Mock(),
            after=Mock(return_value="save-job"),
            after_cancel=Mock(),
        )

        CardPreviewController(app, Mock(), Mock()).changed()

        app.after.assert_called_once_with(350, app.card_save_values)
        self.assertIsNone(app.card_preview_update_job)

    def test_update_without_preview_frame_is_safe(self):
        app = SimpleNamespace(
            card_preview_update_job="queued",
            card_creator_state=CardCreatorState(),
        )

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
                card_creator_state=CardCreatorState(),
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
            self.assertIsNotNone(
                app.card_creator_state.preview_background_cache
            )
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
