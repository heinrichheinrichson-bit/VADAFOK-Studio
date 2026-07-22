import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.obs_connection.controller import OBSConnectionController


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


def make_app():
    variables = {
        "host": "localhost", "port": "4455", "password": "secret",
        "caption_engine": "smart_png",
        "scene_name": "", "caption_group": "VADAFOK Caption",
        "caption_text": "VADAFOK Caption Text",
        "caption_banner_source": "VADAFOK Caption Banner",
        "caption_render_source": "VADAFOK Caption Render",
        "scene_card_source": "VADAFOK Scene Card",
        "stream_effect_source": "VADAFOK Stream Effect",
    }
    app = SimpleNamespace(
        obs=Mock(connected=False), save_config=Mock(),
        obs_workflow_set_sidebar_status=Mock(),
        config_data={},
    )
    app.obs.version_summary.return_value = "OBS 32.0 · WebSocket 5.6"
    for name, value in variables.items():
        setattr(app, name, Variable(value))
    return app


class OBSConnectionControllerTests(unittest.TestCase):
    def test_connect_ignores_status_widgets_from_destroyed_page(self):
        app = make_app()
        stale_status = Mock()
        stale_status.winfo_exists.return_value = 0
        stale_detail = Mock()
        stale_detail.winfo_exists.return_value = 0
        app.obs_connection_status_label = stale_status
        app.obs_connection_detail_label = stale_detail
        controller = OBSConnectionController(app)

        self.assertTrue(controller.connect(show_dialog=False))

        stale_status.configure.assert_not_called()
        stale_detail.configure.assert_not_called()
        self.assertIsNone(app.obs_connection_status_label)
        self.assertIsNone(app.obs_connection_detail_label)

    def test_endpoint_validation_rejects_invalid_port(self):
        app = make_app()
        app.port = Variable("70000")
        controller = OBSConnectionController(app)

        with patch("vadafok_studio.obs_connection.controller.messagebox.showwarning"):
            self.assertFalse(controller.validate_endpoint())

    def test_successful_connect_updates_shared_status_and_saves(self):
        app = make_app()
        controller = OBSConnectionController(app)

        self.assertTrue(controller.connect(show_dialog=False))

        app.obs.connect.assert_called_once_with("localhost", "4455", "secret")
        app.obs_workflow_set_sidebar_status.assert_called_once_with(True)
        app.save_config.assert_called_once_with()

    def test_failed_connect_does_not_save_password_or_settings(self):
        app = make_app()
        app.obs.connect.side_effect = ConnectionRefusedError("refused")
        controller = OBSConnectionController(app)

        self.assertFalse(controller.connect(show_dialog=False))

        app.save_config.assert_not_called()
        app.obs_workflow_set_sidebar_status.assert_called_once_with(False)

    def test_source_diagnosis_checks_nested_scene_sources(self):
        app = make_app()
        names = [
            app.caption_group.get(), app.caption_text.get(),
            app.caption_banner_source.get(), app.caption_render_source.get(),
            app.scene_card_source.get(), app.stream_effect_source.get(),
        ]
        app.obs.connected = True
        app.obs.probe.return_value = True
        app.obs.get_current_scene_name.return_value = "Live"
        app.obs.get_scene_list.return_value = ["Live"]
        app.obs.get_scene_sources_recursive.return_value = [
            {"name": name, "parent": "VADAFOK Caption"} for name in names
        ]
        controller = OBSConnectionController(app)
        controller._add_diagnostic = Mock()

        self.assertTrue(controller.diagnose_sources())

        app.obs.get_scene_sources_recursive.assert_called_once_with("Live")

    def test_smart_png_does_not_require_inactive_obs_text_sources(self):
        app = make_app()
        app.obs.connected = True
        app.obs.probe.return_value = True
        app.obs.get_current_scene_name.return_value = "Live"
        app.obs.get_scene_list.return_value = ["Live"]
        app.obs.get_scene_sources_recursive.return_value = [
            {"name": app.caption_group.get()},
            {"name": app.caption_render_source.get()},
        ]
        controller = OBSConnectionController(app)
        controller._add_diagnostic = Mock()

        self.assertTrue(controller.diagnose_sources())

    def test_authentication_errors_are_explained_without_exposing_password(self):
        message = OBSConnectionController.friendly_error(
            RuntimeError("authentication password rejected"),
        )
        self.assertIn("Authentifizierung", message)
        self.assertNotIn("secret", message)


if __name__ == "__main__":
    unittest.main()
