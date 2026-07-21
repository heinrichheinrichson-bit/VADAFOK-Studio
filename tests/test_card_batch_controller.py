import unittest
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.card_creator.batch_controller import CardBatchController
from vadafok_studio.card_creator.state import CardCreatorState
from vadafok_studio.core import batch_engine as real_batch_engine


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class TestApp(SimpleNamespace):
    """Expose legacy names only inside tests while assertions migrate."""

    @property
    def card_batch_items(self):
        return self.card_creator_state.batch_items

    @card_batch_items.setter
    def card_batch_items(self, items):
        self.card_creator_state.batch_items = items

    @property
    def card_batch_selected_index(self):
        return self.card_creator_state.batch_selected_index

    @card_batch_selected_index.setter
    def card_batch_selected_index(self, index):
        self.card_creator_state.batch_selected_index = index


def make_app():
    return TestApp(
        card_output_name=Variable("show_card"),
        card_selected_template=Variable("Default"),
        card_export_profile=Variable("Broadcast PNG"),
        card_creator_state=CardCreatorState(),
        card_creator_values={"Default": {"title": Variable("")}},
        card_default_output_name=Mock(return_value="default_card"),
        card_save_values=Mock(),
        card_values_plain=Mock(return_value={"title": "Hello"}),
        card_build_batch_panel=Mock(),
        card_build_form=Mock(),
        card_update_preview=Mock(),
        card_choose_batch_output_directory=Mock(return_value=Path("exports")),
        card_render_to_file=Mock(return_value=Path("exports/card.png")),
    )


def make_controller(app, batch_engine=None):
    return CardBatchController(
        app,
        app.card_creator_state,
        lambda: ["Default"],
        batch_engine or real_batch_engine,
    )


class CardBatchControllerTests(unittest.TestCase):
    def test_app_batch_mutation_methods_are_thin_adapters(self):
        app_path = Path(__file__).resolve().parents[1] / "vadafok_studio" / "app.py"
        source = app_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        studio = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "VadafokStudio")
        expected_calls = {
            "card_batch_current_item_name": "self.card_batch_controller.current_item_name()",
            "card_batch_add_current": "self.card_batch_controller.add_current()",
            "card_batch_duplicate_selected": "self.card_batch_controller.duplicate_selected()",
            "card_batch_remove_selected": "self.card_batch_controller.remove_selected()",
            "card_batch_clear": "self.card_batch_controller.clear()",
            "card_batch_select": "self.card_batch_controller.select(idx)",
            "card_save_batch_project": "self.card_batch_controller.save_project()",
            "card_load_batch_project": "self.card_batch_controller.load_project()",
            "card_import_batch_file": "self.card_batch_controller.import_file()",
            "card_render_batch": "self.card_batch_controller.render()",
        }
        methods = {node.name: node for node in studio.body if isinstance(node, ast.FunctionDef)}

        for name, call in expected_calls.items():
            method = methods[name]
            block = ast.get_source_segment(source, method)
            self.assertLessEqual(method.end_lineno - method.lineno + 1, 2)
            self.assertIn(call, block)

        self.assertIn("self.card_creator_state = CardCreatorState()", source)
        self.assertNotIn("self.card_batch_items = []", source)
        self.assertNotIn("self.card_batch_selected_index = None", source)
        self.assertNotIn("def card_batch_items(self)", source)
        self.assertNotIn("def card_batch_selected_index(self)", source)

    def test_add_current_captures_values_and_selects_new_item(self):
        app = make_app()
        make_controller(app).add_current()
        self.assertEqual(app.card_batch_items[0]["values"], {"title": "Hello"})
        self.assertEqual(app.card_batch_items[0]["output_name"], "show_card")
        self.assertEqual(app.card_batch_selected_index, 0)
        app.card_save_values.assert_called_once_with()
        app.card_build_batch_panel.assert_called_once_with()

    def test_duplicate_selected_copies_nested_values(self):
        app = make_app()
        original = {"template": "Default", "output_name": "show_card", "profile": "Broadcast PNG", "values": {"title": "Hello"}}
        app.card_batch_items = [original]
        app.card_batch_selected_index = 0
        make_controller(app).duplicate_selected()
        self.assertEqual(app.card_batch_items[1]["output_name"], "show_card_copy")
        self.assertIsNot(app.card_batch_items[1]["values"], original["values"])
        self.assertEqual(app.card_batch_selected_index, 1)

    def test_remove_without_selection_preserves_items(self):
        app = make_app()
        app.card_batch_items = [{"output_name": "one"}]
        with patch("vadafok_studio.card_creator.batch_controller.messagebox.showinfo") as info:
            make_controller(app).remove_selected()
        self.assertEqual(app.card_batch_items, [{"output_name": "one"}])
        info.assert_called_once()
        app.card_build_batch_panel.assert_not_called()

    def test_clear_requires_confirmation(self):
        app = make_app()
        app.card_batch_items = [{"output_name": "one"}]
        with patch("vadafok_studio.card_creator.batch_controller.messagebox.askyesno", return_value=True):
            make_controller(app).clear()
        self.assertEqual(app.card_batch_items, [])
        self.assertIsNone(app.card_batch_selected_index)
        app.card_build_batch_panel.assert_called_once_with()

    def test_current_item_name_uses_default_for_blank_value(self):
        app = make_app()
        app.card_output_name = Variable("  ")
        self.assertEqual(
            make_controller(app).current_item_name(),
            "default_card",
        )

    def test_select_restores_item_into_existing_form_variables(self):
        app = make_app()
        app.card_batch_items = [{
            "template": "Default",
            "output_name": "selected_card",
            "profile": "Web PNG",
            "values": {"title": "Selected title"},
        }]

        make_controller(app).select(0)

        self.assertEqual(app.card_batch_selected_index, 0)
        self.assertEqual(app.card_output_name.get(), "selected_card")
        self.assertEqual(app.card_export_profile.get(), "Web PNG")
        self.assertEqual(
            app.card_creator_values["Default"]["title"].get(),
            "Selected title",
        )
        app.card_build_form.assert_called_once_with()
        app.card_save_values.assert_called_once_with()
        app.card_update_preview.assert_called_once_with()
        app.card_build_batch_panel.assert_called_once_with()

    def test_select_ignores_out_of_range_index(self):
        app = make_app()

        make_controller(app).select(4)

        self.assertIsNone(app.card_batch_selected_index)
        app.card_build_form.assert_not_called()

    def test_select_updates_only_row_highlight_when_view_supports_it(self):
        app = make_app()
        app.card_update_batch_selection = Mock()
        app.card_batch_items = [{
            "template": "Default",
            "output_name": "selected",
            "profile": "Broadcast PNG",
            "values": {"title": "Selected"},
        }]

        make_controller(app).select(0)

        app.card_update_batch_selection.assert_called_once_with()
        app.card_build_batch_panel.assert_not_called()

    def test_save_project_passes_current_items_to_engine(self):
        app = make_app()
        app.card_batch_items = [{"output_name": "one"}]
        engine = Mock()
        engine.batch_projects_dir.return_value = Path("batch_projects")
        engine.save_batch_project_file.return_value = "saved.vbatch"

        with patch(
            "vadafok_studio.card_creator.batch_controller.filedialog.asksaveasfilename",
            return_value="saved.vbatch",
        ), patch("vadafok_studio.card_creator.batch_controller.messagebox.showinfo"):
            make_controller(app, engine).save_project()

        engine.save_batch_project_file.assert_called_once_with(
            "saved.vbatch", app.card_batch_items
        )

    def test_load_project_replaces_items_and_selects_first(self):
        app = make_app()
        loaded = [{
            "template": "Default",
            "output_name": "loaded",
            "profile": "Broadcast PNG",
            "values": {"title": "Loaded title"},
        }]
        engine = Mock()
        engine.batch_projects_dir.return_value = Path("batch_projects")
        engine.load_batch_project_file.return_value = loaded

        with patch(
            "vadafok_studio.card_creator.batch_controller.filedialog.askopenfilename",
            return_value="saved.vbatch",
        ), patch("vadafok_studio.card_creator.batch_controller.messagebox.showinfo"):
            make_controller(app, engine).load_project()

        self.assertEqual(app.card_batch_items, loaded)
        self.assertEqual(app.card_batch_selected_index, 0)
        self.assertEqual(app.card_output_name.get(), "loaded")
        self.assertEqual(
            app.card_creator_values["Default"]["title"].get(), "Loaded title"
        )

    def test_cancelled_project_dialogs_do_not_change_items(self):
        app = make_app()
        app.card_batch_items = [{"output_name": "existing"}]
        engine = Mock()
        engine.batch_projects_dir.return_value = Path("batch_projects")

        with patch(
            "vadafok_studio.card_creator.batch_controller.filedialog.askopenfilename",
            return_value="",
        ):
            make_controller(app, engine).load_project()

        self.assertEqual(app.card_batch_items, [{"output_name": "existing"}])
        engine.load_batch_project_file.assert_not_called()

    def test_import_file_adds_only_rows_with_matching_values(self):
        app = make_app()
        app.card_template = Mock(return_value={"fields": [{"name": "title"}]})
        engine = Mock()
        engine.read_table.return_value = [{"title": "Imported"}]
        engine.analyze_columns.return_value = (["title"], [])
        engine.unique_output_name.side_effect = real_batch_engine.unique_output_name
        engine.rows_to_batch_items.return_value = [
            {"output_name": "matched", "values": {"title": "Imported"}},
            {"output_name": "unmatched", "values": {}},
        ]

        with patch(
            "vadafok_studio.card_creator.batch_controller.filedialog.askopenfilename",
            return_value="cards.csv",
        ), patch("vadafok_studio.card_creator.batch_controller.messagebox.showinfo"):
            make_controller(app, engine).import_file()

        engine.read_table.assert_called_once_with(Path("cards.csv"))
        self.assertEqual(
            app.card_batch_items,
            [{"output_name": "matched", "values": {"title": "Imported"}}],
        )
        self.assertEqual(app.card_batch_selected_index, 0)
        app.card_build_batch_panel.assert_called_once_with()

    def test_import_file_warns_when_no_columns_match(self):
        app = make_app()
        app.card_template = Mock(return_value={"fields": [{"name": "title"}]})
        engine = Mock()
        engine.read_table.return_value = [{"other": "value"}]
        engine.analyze_columns.return_value = ([], ["other"])
        engine.unique_output_name.side_effect = real_batch_engine.unique_output_name
        engine.rows_to_batch_items.return_value = [
            {"output_name": "unmatched", "values": {}}
        ]

        with patch(
            "vadafok_studio.card_creator.batch_controller.filedialog.askopenfilename",
            return_value="cards.csv",
        ), patch(
            "vadafok_studio.card_creator.batch_controller.messagebox.showwarning"
        ) as warning:
            make_controller(app, engine).import_file()

        self.assertEqual(app.card_batch_items, [])
        warning.assert_called_once()
        app.card_build_batch_panel.assert_not_called()

    def test_render_skips_unknown_templates_and_restores_ui_state(self):
        app = make_app()
        app.card_output_name.set("before")
        app.card_creator_values["Default"]["title"].set("Before title")
        app.card_values_plain.return_value = {"title": "Before title"}
        app.card_batch_items = [
            {
                "template": "Missing",
                "output_name": "skip",
                "profile": "Broadcast PNG",
                "values": {"title": "Skip"},
            },
            {
                "template": "Default",
                "output_name": "rendered",
                "profile": "Web PNG",
                "values": {"title": "Rendered title"},
            },
        ]

        with patch("vadafok_studio.card_creator.batch_controller.messagebox.showwarning"):
            make_controller(app).render()

        app.card_render_to_file.assert_called_once_with(
            final=True, output_dir=Path("exports")
        )
        self.assertEqual(app.card_selected_template.get(), "Default")
        self.assertEqual(app.card_output_name.get(), "before")
        self.assertEqual(app.card_export_profile.get(), "Broadcast PNG")
        self.assertEqual(
            app.card_creator_values["Default"]["title"].get(), "Before title"
        )
        app.card_save_values.assert_called_once_with()
        app.card_update_preview.assert_called_once_with()
        app.card_build_batch_panel.assert_called_once_with()

    def test_render_empty_batch_does_not_ask_for_output_directory(self):
        app = make_app()

        with patch("vadafok_studio.card_creator.batch_controller.messagebox.showinfo"):
            make_controller(app).render()

        app.card_choose_batch_output_directory.assert_not_called()
        app.card_render_to_file.assert_not_called()

    def test_render_cancelled_output_directory_preserves_ui(self):
        app = make_app()
        app.card_batch_items = [{"template": "Default"}]
        app.card_choose_batch_output_directory.return_value = None

        make_controller(app).render()

        app.card_render_to_file.assert_not_called()
        app.card_build_form.assert_not_called()

    def test_render_continues_after_item_error_and_protects_duplicate_names(self):
        app = make_app()
        app.card_batch_items = [
            {"template": "Default", "output_name": "show", "values": {}},
            {"template": "Default", "output_name": "show", "values": {}},
        ]
        rendered_names = []

        def render_item(**_kwargs):
            rendered_names.append(app.card_output_name.get())
            if len(rendered_names) == 1:
                raise RuntimeError("first failed")
            return Path("exports/show_2.png")

        app.card_render_to_file.side_effect = render_item
        with patch(
            "vadafok_studio.card_creator.batch_controller.messagebox.showwarning"
        ) as warning:
            make_controller(app).render()

        self.assertEqual(rendered_names, ["show", "show_2"])
        self.assertEqual(app.card_render_to_file.call_count, 2)
        warning.assert_called_once()
