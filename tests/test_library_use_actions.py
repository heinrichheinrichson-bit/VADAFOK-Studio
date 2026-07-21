import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.library import use_actions


class LibraryUseActionTests(unittest.TestCase):
    def banner_app(self, picker=False):
        return SimpleNamespace(
            selected_item=SimpleNamespace(
                kind="image", path=Path("Banners/example.png"), name="Example",
            ),
            library_banner_picker_mode=picker,
            library_banner_target_slot=None,
            library_return_page="Live Card" if picker else None,
            config_data={},
            ensure_obs_ready=Mock(return_value=False),
            show_live_card=Mock(),
            update_render_preview=Mock(),
            after=Mock(),
        )

    @patch.object(use_actions.messagebox, "showinfo")
    @patch.object(use_actions, "save_config")
    def test_banner_selection_is_saved_without_obs(self, save, showinfo):
        app = self.banner_app()
        use_actions.use_as_caption_banner(app)
        self.assertEqual(
            app.config_data["selected_banner_path"],
            str(Path("Banners/example.png")),
        )
        save.assert_called_once_with(app.config_data)
        showinfo.assert_called_once()

    @patch.object(use_actions, "save_config")
    def test_picker_returns_to_live_card_and_refreshes_preview(self, _save):
        app = self.banner_app(picker=True)
        use_actions.use_as_caption_banner(app)
        self.assertFalse(app.library_banner_picker_mode)
        self.assertIsNone(app.library_return_page)
        app.show_live_card.assert_called_once()
        app.update_render_preview.assert_called_once()

    @patch.object(use_actions, "save_config")
    def test_targeted_picker_replaces_exact_banner_slot(self, save):
        app = self.banner_app(picker=True)
        app.library_banner_target_slot = 2
        app.config_data["live_card_banner_slots"] = ["one", "two", "old", "four"]

        use_actions.use_as_caption_banner(app)

        self.assertEqual(
            app.config_data["live_card_banner_slots"],
            ["one", "two", str(Path("Banners/example.png")), "four"],
        )
        self.assertTrue(app.config_data["live_card_banner_slots_initialized"])
        self.assertIsNone(app.library_banner_target_slot)
        save.assert_called_once_with(app.config_data)

    @patch.object(use_actions.messagebox, "showwarning")
    def test_scene_card_rejects_non_image(self, warning):
        app = SimpleNamespace(
            selected_item=SimpleNamespace(kind="sound"),
            obs=SimpleNamespace(connected=True),
        )
        use_actions.show_as_scene_card(app)
        warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()
