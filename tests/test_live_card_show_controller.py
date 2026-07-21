import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

from vadafok_studio.live_card.show_controller import LiveCardShowController


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class LiveCardShowControllerTests(unittest.TestCase):
    def make_app(self, obs_ready=True):
        service = SimpleNamespace(
            resolve=Mock(return_value="effect.wav"),
            exists=Mock(return_value=True),
        )
        app = SimpleNamespace(
            config_data={
                "sync_profiler_enabled": False,
                "stream_effect_enabled": True,
                "selected_sound_effect": "Sounds/effect.wav",
                "selected_banner_path": "banner.png",
            },
            ensure_obs_ready=Mock(return_value=obs_ready),
            message_box=Mock(),
            current_scene=Mock(return_value="Scene"),
            caption_engine=Variable("obs_text"),
            caption_banner_source=Variable("Banner"),
            caption_text=Variable("Text"),
            caption_render_source=Variable("Render"),
            caption_group=Variable("Group"),
            stream_effect_source=Variable("Effect"),
            duration=Variable("5"),
            obs=Mock(),
            hide_timer=None,
            after=Mock(),
            hide_card=Mock(),
            save_config=Mock(),
            _sync_sound_service_project=Mock(return_value=service),
            obs_workflow_banner_action=Mock(),
            obs_workflow_current_live_text=Mock(return_value="Hello"),
        )
        app.message_box.get.return_value = "Hello\n"
        return app

    def test_disconnected_obs_aborts_before_reading_or_sending(self):
        app = self.make_app(obs_ready=False)
        LiveCardShowController(app).show_card()
        app.message_box.get.assert_not_called()
        app.obs.set_text.assert_not_called()

    @patch("vadafok_studio.live_card.show_controller.threading.Timer")
    def test_text_show_enables_group_before_playing_sound(self, timer):
        app = self.make_app()
        LiveCardShowController(app).show_card()
        app.obs.set_image_file.assert_called_once_with("Banner", "banner.png")
        app.obs.set_text.assert_called_once_with("Text", "Hello")
        calls = app.obs.mock_calls
        group_index = calls.index(call.enable_source("Scene", "Group", True))
        sound_index = calls.index(call.play_media_file("Effect", "effect.wav"))
        self.assertLess(group_index, sound_index)
        timer.return_value.start.assert_called_once()
        app.save_config.assert_called_once()

    def test_hide_disables_caption_group(self):
        app = self.make_app()
        LiveCardShowController(app).hide_card()
        app.obs.enable_source.assert_called_once_with("Scene", "Group", False)
        app.obs_workflow_banner_action.assert_called_once_with("HIDE Live Card")


if __name__ == "__main__":
    unittest.main()
