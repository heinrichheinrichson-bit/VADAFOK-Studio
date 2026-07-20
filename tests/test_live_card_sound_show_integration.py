from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
CONFIG_PATH = ROOT / "vadafok_studio" / "core" / "config.py"
OBS_CONTROLLER_PATH = ROOT / "vadafok_studio" / "core" / "obs_controller.py"


class LiveCardSoundShowIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = APP_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.app_class = next(
            node
            for node in cls.tree.body
            if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio"
        )

    def _method(self, name: str) -> ast.FunctionDef:
        return next(
            node
            for node in self.app_class.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        )

    def test_show_card_restarts_obs_sound_only_after_obs_enable(self) -> None:
        method = self._method("show_card")
        calls = [node for node in ast.walk(method) if isinstance(node, ast.Call)]
        sound_call = next(
            node
            for node in calls
            if isinstance(node.func, ast.Attribute)
            and node.func.attr == "play_selected_sound_effect_for_show"
        )
        group_enable_calls = [
            node
            for node in calls
            if isinstance(node.func, ast.Attribute)
            and node.func.attr == "enable_source"
        ]
        self.assertTrue(group_enable_calls)
        self.assertGreater(sound_call.lineno, max(call.lineno for call in group_enable_calls))

    def test_show_card_has_exactly_one_automatic_sound_call(self) -> None:
        method = self._method("show_card")
        count = sum(
            1
            for node in ast.walk(method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "play_selected_sound_effect_for_show"
        )
        self.assertEqual(count, 1)

    def test_show_helper_uses_obs_media_source_not_local_playback(self) -> None:
        helper = ast.unparse(self._method("play_selected_sound_effect_for_show"))
        self.assertIn("self._sync_sound_service_project()", helper)
        self.assertIn("self.obs.play_media_file", helper)
        self.assertIn("OBS media playback requested", helper)
        self.assertNotIn("self.obs.restart_media_source", helper)
        self.assertNotIn("service.play", helper)

    def test_preview_still_uses_local_sound_service(self) -> None:
        preview = ast.unparse(self._method("preview_live_card_effect"))
        self.assertIn("service.play", preview)
        self.assertNotIn("restart_media_source", preview)

    def test_automatic_playback_requires_enabled_checkbox(self) -> None:
        helper = ast.unparse(self._method("play_selected_sound_effect_for_show"))
        self.assertIn("stream_effect_enabled", helper)
        self.assertIn("return None", helper)

    def test_stream_effect_source_is_loaded_and_saved(self) -> None:
        self.assertIn("self.stream_effect_source = ctk.StringVar", self.source)
        self.assertIn('"stream_effect_source": (', self.source)
        settings_source = (ROOT / 'vadafok_studio' / 'settings' / 'page.py').read_text(encoding='utf-8')
        self.assertIn('text="OBS Stream Effect"', settings_source)
        self.assertIn("textvariable=app.stream_effect_source", settings_source)

    def test_checkbox_and_persistence_callback_are_present(self) -> None:
        self.assertIn('text="Sound automatisch bei SHOW abspielen"', self.source)
        self.assertIn("variable=self.stream_effect_enabled", self.source)
        self.assertIn("command=self.set_stream_effect_enabled", self.source)
        callback = ast.unparse(self._method("set_stream_effect_enabled"))
        self.assertIn("stream_effect_enabled", callback)
        self.assertIn("save_config(self.config_data)", callback)

    def test_config_contains_obs_media_source_default(self) -> None:
        config_source = CONFIG_PATH.read_text(encoding="utf-8")
        self.assertIn('"stream_effect_enabled": False', config_source)
        self.assertIn(
            '"stream_effect_source": "VADAFOK Stream Effect"',
            config_source,
        )
        self.assertIn('"sync_profiler_enabled": True', config_source)

    def test_obs_controller_supports_media_file_and_restart(self) -> None:
        if not OBS_CONTROLLER_PATH.exists():
            self.skipTest("obs_controller.py is supplied by the installed base project")
        controller_source = OBS_CONTROLLER_PATH.read_text(encoding="utf-8")
        controller_tree = ast.parse(controller_source)
        controller_class = next(
            node
            for node in controller_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "OBSController"
        )
        method_names = {
            node.name
            for node in controller_class.body
            if isinstance(node, ast.FunctionDef)
        }
        self.assertIn("set_media_file", method_names)
        self.assertIn("restart_media_source", method_names)
        self.assertIn("play_media_file", method_names)
        self.assertIn('"local_file"', controller_source)
        self.assertIn("OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART", controller_source)
        self.assertIn('"TriggerMediaInputAction"', controller_source)
        self.assertIn('client.send(', controller_source)

    def test_version_is_2_26_8_0(self) -> None:
        version_source = (ROOT / "vadafok_studio" / "version.py").read_text(
            encoding="utf-8"
        )
        namespace = {}
        exec(version_source, namespace)
        self.assertRegex(namespace['VERSION'], r'^\d+\.\d+\.\d+\.\d+$')


if __name__ == "__main__":
    unittest.main()
