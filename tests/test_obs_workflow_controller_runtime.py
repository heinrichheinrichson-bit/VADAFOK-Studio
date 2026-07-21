import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.core.obs_workflow import OBSWorkflowState
from vadafok_studio.obs_workflow.controller import OBSWorkflowController


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


def make_app():
    app = SimpleNamespace(
        obs=Mock(), obs_workflow_state=OBSWorkflowState(),
        show_obs_workflow_page=Mock(), ensure_obs_ready=Mock(return_value=True),
        obs_workflow_set_sidebar_status=Mock(), update_idletasks=Mock(),
        config_data={"stream_effect_enabled": False},
    )
    variables = {
        "caption_engine": "smart_png",
        "caption_group": "VADAFOK Caption",
        "caption_text": "VADAFOK Caption Text",
        "caption_banner_source": "VADAFOK Caption Banner",
        "caption_render_source": "VADAFOK Caption Render",
        "scene_card_source": "VADAFOK Scene Card",
        "stream_effect_source": "VADAFOK Stream Effect",
    }
    for name, value in variables.items():
        setattr(app, name, Variable(value))
    return app


class OBSWorkflowRuntimeTests(unittest.TestCase):
    def test_failed_connection_does_not_show_second_error_dialog(self):
        app = make_app()
        app.connect_obs = Mock(return_value=False)
        controller = OBSWorkflowController(app)

        with patch("vadafok_studio.obs_workflow.controller.messagebox.showerror") as error:
            self.assertFalse(controller.obs_workflow_connect())

        error.assert_not_called()
        app.show_obs_workflow_page.assert_called_once_with()

    def test_scene_switch_refreshes_sources_for_actual_program_scene(self):
        app = make_app()
        app.obs.get_current_scene_name.return_value = "Gameplay"
        app.obs.get_scene_sources.return_value = [
            {"name": "Camera", "enabled": True},
        ]
        controller = OBSWorkflowController(app)
        controller.obs_workflow_render_sources_panel = Mock(return_value=True)

        controller.obs_workflow_switch_scene("Gameplay")

        app.obs.switch_scene.assert_called_once_with("Gameplay")
        app.obs.get_current_scene_name.assert_called_once_with()
        app.obs.get_scene_sources.assert_called_once_with("Gameplay")
        self.assertEqual(app.obs_workflow_state.sources[0]["name"], "Camera")
        controller.obs_workflow_render_sources_panel.assert_called_once_with()

    def test_required_sources_follow_active_caption_engine(self):
        app = make_app()
        controller = OBSWorkflowController(app)

        smart_sources = controller.obs_workflow_required_overlay_sources()
        self.assertIn("VADAFOK Caption Render", smart_sources)
        self.assertNotIn("VADAFOK Caption Text", smart_sources)
        self.assertNotIn("VADAFOK Caption Banner", smart_sources)

        app.caption_engine = Variable("obs_text")
        text_sources = controller.obs_workflow_required_overlay_sources()
        self.assertIn("VADAFOK Caption Text", text_sources)
        self.assertIn("VADAFOK Caption Banner", text_sources)
        self.assertNotIn("VADAFOK Caption Render", text_sources)

    def test_overlay_installer_is_collapsed_by_default_and_remembers_toggle(self):
        app = make_app()
        controller = OBSWorkflowController(app)

        self.assertFalse(app.obs_workflow_state.overlay_installer_expanded)
        controller.obs_workflow_toggle_installer()

        self.assertTrue(app.obs_workflow_state.overlay_installer_expanded)
        app.show_obs_workflow_page.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
