import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
CONFIG_PATH = ROOT / "vadafok_studio" / "core" / "config.py"
VERSION_PATH = ROOT / "vadafok_studio" / "version.py"
EDITOR_PATH = ROOT / "vadafok_studio" / "sound_favorites" / "editor.py"
LIVE_CONTROLLER_PATH = ROOT / "vadafok_studio" / "live_card" / "controller.py"


class SoundFavoritesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app_source = APP_PATH.read_text(encoding="utf-8")
        cls.live_source = LIVE_CONTROLLER_PATH.read_text(encoding="utf-8")
        cls.combined_source = cls.app_source + "\n" + cls.live_source
        cls.config_source = CONFIG_PATH.read_text(encoding="utf-8")
        cls.version_source = VERSION_PATH.read_text(encoding="utf-8")
        cls.app_tree = ast.parse(cls.app_source)
        cls.editor_source = EDITOR_PATH.read_text(encoding="utf-8")

    def test_version_is_semantic(self):
        namespace = {}
        exec(self.version_source, namespace)
        self.assertRegex(namespace["VERSION"], r"^\d+\.\d+\.\d+\.\d+$")

    def test_config_has_exactly_four_default_slots(self):
        namespace = {"__file__": str(CONFIG_PATH)}
        exec(compile(self.config_source, str(CONFIG_PATH), "exec"), namespace)
        favorites = namespace["DEFAULT_CONFIG"]["sound_favorites"]
        self.assertEqual(4, len(favorites))
        self.assertEqual(
            ["Favorit 1", "Favorit 2", "Favorit 3", "Favorit 4"],
            [item["name"] for item in favorites],
        )
        self.assertTrue(all(item["file"] == "" for item in favorites))

    def test_required_favorite_methods_exist(self):
        methods = {
            node.name
            for node in ast.walk(self.app_tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        self.assertTrue({
            "_ensure_sound_favorites",
            "_apply_selected_sound_effect",
            "select_sound_favorite",
            "replace_sound_favorite",
            "refresh_sound_favorite_buttons",
            "open_sound_favorites_editor",
        }.issubset(methods))

    def test_quick_select_uses_existing_selected_effect_pipeline(self):
        self.assertIn("return self._apply_selected_sound_effect(relative)", self.live_source)
        self.assertIn('app.config_data["selected_sound_effect"] = relative', self.live_source)
        self.assertIn("app.obs.set_media_file(source_name, media_file)", self.live_source)

    def test_editor_keeps_files_portable(self):
        self.assertIn("portable_effect_path(service, selected)", self.editor_source)
        self.assertIn("innerhalb des Projektordners Sounds", self.editor_source)

    def test_editor_is_delegated_to_its_module(self):
        self.assertIn("from ..sound_favorites.editor import open_sound_favorites_editor_window", self.live_source)
        self.assertIn("return open_sound_favorites_editor_window(app)", self.live_source)
        self.assertIn("def open_sound_favorites_editor_window(app):", self.editor_source)

    def test_live_card_builds_four_favorite_buttons(self):
        self.assertIn("for index in range(4):", self.live_source)
        self.assertIn("command=lambda slot=index: self.select_sound_favorite(slot)", self.live_source)
        self.assertIn('text="FAVORITEN BEARBEITEN"', self.live_source)

    def test_empty_slot_is_handled_without_playback(self):
        self.assertIn("return self.replace_sound_favorite(index)", self.live_source)
        self.assertIn("if not relative:", self.live_source)


if __name__ == "__main__":
    unittest.main()
