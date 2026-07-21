from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.silent_director.runner import run_preset


ROOT = Path(__file__).resolve().parents[1]


def make_app(**overrides):
    state = SimpleNamespace(
        current_scene="",
        last_scene_switch="",
        now=Mock(return_value="now"),
        add_event=Mock(),
    )
    values = dict(
        silent_director_get_selected_preset=Mock(return_value=None),
        ensure_obs_ready=Mock(return_value=True),
        director_stop_requested=False,
        director_clear_active_action=Mock(),
        director_set_active_action=Mock(),
        director_set_status=Mock(),
        director_log_add=Mock(),
        director_action_label=Mock(side_effect=lambda action: action["type"]),
        silent_director_show_banner_direct=Mock(return_value=True),
        obs=SimpleNamespace(switch_scene=Mock()),
        obs_workflow_state=state,
        obs_workflow_set_source_visibility=Mock(),
        obs_workflow_mark_command=Mock(),
        obs_workflow_refresh=Mock(),
        obs_workflow_log=Mock(),
        director_progress_var=SimpleNamespace(get=lambda: "0 / 0"),
    )
    values.update(overrides)
    return SimpleNamespace(**values)


class SilentDirectorRunnerTests(unittest.TestCase):
    def test_app_delegates_preset_execution(self):
        source = (ROOT / "vadafok_studio" / "app.py").read_text(encoding="utf-8")
        self.assertIn("run_preset as run_silent_director_preset", source)
        self.assertIn("return run_silent_director_preset(self, preset)", source)
        self.assertNotIn("RUN Preset '{name}' started", source)

    @patch("vadafok_studio.silent_director.runner.messagebox.showinfo")
    def test_missing_preset_is_reported_without_obs_access(self, showinfo):
        app = make_app()

        run_preset(app)

        showinfo.assert_called_once_with("Silent Director", "No preset selected.")
        app.ensure_obs_ready.assert_not_called()

    def test_scene_and_source_actions_run_in_order(self):
        preset = {
            "name": "Show",
            "actions": [
                {"type": "switch_scene", "scene": "Main"},
                {"type": "show_source", "source": "Camera"},
                {"type": "hide_source", "source": "Holding"},
            ],
        }
        app = make_app()

        run_preset(app, preset)

        app.obs.switch_scene.assert_called_once_with("Main")
        self.assertEqual(
            app.obs_workflow_set_source_visibility.call_args_list,
            [unittest.mock.call("Camera", True), unittest.mock.call("Holding", False)],
        )
        app.director_set_status.assert_called_with("FINISHED", "Finished", "3 / 3")
        app.director_clear_active_action.assert_called()

    def test_stop_request_prevents_first_action(self):
        app = make_app(director_stop_requested=True)
        preset = {
            "name": "Stopped",
            "actions": [{"type": "switch_scene", "scene": "Main"}],
        }

        # The runner resets a stale flag at start; emulate a user STOP immediately
        # after the run begins via the first status update.
        def request_stop(*_args):
            app.director_stop_requested = True

        app.director_set_status.side_effect = request_stop
        run_preset(app, preset)

        app.obs.switch_scene.assert_not_called()
        self.assertIn("STOPPED by user", [call.args[0] for call in app.director_log_add.call_args_list])


if __name__ == "__main__":
    unittest.main()
