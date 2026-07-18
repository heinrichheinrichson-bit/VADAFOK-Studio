from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
CONFIG_PATH = ROOT / "vadafok_studio" / "core" / "config.py"


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

    def test_show_card_calls_sound_only_after_obs_enable(self) -> None:
        method = self._method("show_card")
        calls = [node for node in ast.walk(method) if isinstance(node, ast.Call)]
        sound_call = next(
            node for node in calls
            if isinstance(node.func, ast.Attribute)
            and node.func.attr == "play_selected_sound_effect_for_show"
        )
        group_enable_calls = [
            node for node in calls
            if isinstance(node.func, ast.Attribute)
            and node.func.attr == "enable_source"
        ]
        self.assertTrue(group_enable_calls)
        self.assertGreater(sound_call.lineno, max(call.lineno for call in group_enable_calls))

    def test_show_card_has_exactly_one_automatic_sound_call(self) -> None:
        method = self._method("show_card")
        count = sum(
            1 for node in ast.walk(method)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "play_selected_sound_effect_for_show"
        )
        self.assertEqual(count, 1)

    def test_sound_helper_uses_existing_private_service_sync_method(self) -> None:
        helper = ast.unparse(self._method("play_selected_sound_effect_for_show"))
        self.assertIn("self._sync_sound_service_project()", helper)
        self.assertNotIn("self.sync_sound_service_project()", helper)

    def test_automatic_playback_requires_enabled_checkbox(self) -> None:
        helper = ast.unparse(self._method("play_selected_sound_effect_for_show"))
        self.assertIn('stream_effect_enabled', helper)
        self.assertIn("return None", helper)

    def test_checkbox_and_persistence_callback_are_present(self) -> None:
        self.assertIn('text="Sound automatisch bei SHOW abspielen"', self.source)
        self.assertIn("variable=self.stream_effect_enabled", self.source)
        self.assertIn("command=self.set_stream_effect_enabled", self.source)
        callback = ast.unparse(self._method("set_stream_effect_enabled"))
        self.assertIn("stream_effect_enabled", callback)
        self.assertIn("save_config(self.config_data)", callback)

    def test_config_defaults_to_disabled(self) -> None:
        config_source = CONFIG_PATH.read_text(encoding="utf-8")
        self.assertIn('"stream_effect_enabled": False', config_source)

    def test_sound_service_uses_async_windows_playback(self) -> None:
        service_source = (
            ROOT / "vadafok_studio" / "services" / "sound_service.py"
        ).read_text(encoding="utf-8")
        self.assertIn("SND_ASYNC", service_source)
        self.assertIn("SND_NODEFAULT", service_source)

    def test_version_is_2_26_3_0(self) -> None:
        version_source = (ROOT / "vadafok_studio" / "version.py").read_text(encoding="utf-8")
        self.assertIn('VERSION = "2.26.3.0"', version_source)


if __name__ == "__main__":
    unittest.main()
