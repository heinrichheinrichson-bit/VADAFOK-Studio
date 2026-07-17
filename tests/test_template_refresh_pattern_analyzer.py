from __future__ import annotations

import unittest

from vadafok_studio.template_editor.refresh_manager import TemplateRefreshManager
from vadafok_studio.template_editor.refresh_profiler import TemplateRefreshProfiler


class _FakeApp:
    def __init__(self):
        self.calls: list[tuple] = []
        self.template_layers_body = object()
        self.template_props_body = object()

    def template_draw_canvas(self, **kwargs):
        self.calls.append(("canvas", kwargs))

    def template_update_fields_overlay(self, **kwargs):
        self.calls.append(("overlay", kwargs))

    def template_build_layers_panel(self):
        self.calls.append(("layers_full",))

    def template_refresh_layers_selection(self):
        self.calls.append(("layers_selection",))

    def template_load_selected_properties(self):
        self.calls.append(("load_properties",))

    def template_build_properties_panel(self):
        self.calls.append(("build_properties",))


class TemplateRefreshPatternAnalyzerTests(unittest.TestCase):
    def test_pattern_analysis_is_empty_when_profiling_is_disabled(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.selection()

        analysis = manager.refresh_pattern_analysis()

        self.assertFalse(analysis["enabled"])
        self.assertEqual(analysis["total_transitions"], 0)
        self.assertEqual(analysis["unique_transitions"], 0)
        self.assertEqual(analysis["transitions"], [])

    def test_selection_transitions_are_detected(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)

        manager.selection()

        analysis = manager.refresh_pattern_analysis()

        self.assertEqual(analysis["total_chains"], 1)
        self.assertEqual(analysis["total_transitions"], 3)
        self.assertEqual(analysis["unique_transitions"], 3)
        signatures = {
            transition["signature"]
            for transition in analysis["transitions"]
        }
        self.assertEqual(
            signatures,
            {
                "selection>properties",
                "selection>overlay",
                "selection>layers_selection",
            },
        )

    def test_repeated_transitions_are_aggregated(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)

        manager.selection()
        manager.selection()

        analysis = manager.refresh_pattern_analysis()
        by_signature = {
            transition["signature"]: transition
            for transition in analysis["transitions"]
        }

        self.assertEqual(by_signature["selection>properties"]["count"], 2)
        self.assertEqual(by_signature["selection>overlay"]["count"], 2)
        self.assertEqual(
            by_signature["selection>layers_selection"]["count"],
            2,
        )
        self.assertAlmostEqual(
            by_signature["selection>properties"]["target_share"],
            1 / 3,
        )

    def test_root_level_independent_calls_do_not_create_transitions(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)

        manager.canvas()
        manager.overlay()

        analysis = manager.refresh_pattern_analysis()

        self.assertEqual(analysis["total_chains"], 2)
        self.assertEqual(analysis["total_transitions"], 0)

    def test_nested_parent_child_relationships_are_used(self):
        profiler = TemplateRefreshProfiler(enabled=True)

        def nested():
            profiler.run("child", lambda: None)

        profiler.run("root", nested)

        analysis = profiler.pattern_analysis_snapshot()

        self.assertEqual(
            analysis["transitions"],
            [
                {
                    "source": "root",
                    "target": "child",
                    "signature": "root>child",
                    "count": 1,
                    "source_total": 1,
                    "target_share": 1.0,
                }
            ],
        )
        self.assertEqual(analysis["incoming_counts"], {"child": 1})

    def test_sources_are_ranked_by_outgoing_frequency(self):
        profiler = TemplateRefreshProfiler(enabled=True)

        profiler.run("root_a", lambda: profiler.run("child", lambda: None))
        profiler.run("root_a", lambda: profiler.run("child", lambda: None))
        profiler.run("root_b", lambda: profiler.run("child", lambda: None))

        analysis = profiler.pattern_analysis_snapshot()

        self.assertEqual(
            [source["name"] for source in analysis["sources"]],
            ["root_a", "root_b"],
        )
        self.assertEqual(analysis["sources"][0]["outgoing_count"], 2)

    def test_pattern_snapshot_is_detached(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.selection()

        first = manager.refresh_pattern_analysis()
        first["transitions"][0]["count"] = 999
        first["sources"][0]["transitions"][0]["target"] = "changed"

        second = manager.refresh_pattern_analysis()
        self.assertNotEqual(second["transitions"][0]["count"], 999)
        self.assertNotEqual(
            second["sources"][0]["transitions"][0]["target"],
            "changed",
        )

    def test_reset_analysis_clears_patterns_but_preserves_metrics(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.selection()

        manager.reset_analysis()

        self.assertEqual(
            manager.refresh_pattern_analysis()["transitions"],
            [],
        )
        self.assertEqual(
            manager.refresh_profile()["metrics"]["selection"]["count"],
            1,
        )

    def test_pattern_text_contains_transition_report(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.selection()

        text = manager.refresh_pattern_text()

        self.assertIn("=== Refresh Pattern Analysis ===", text)
        self.assertIn("Übergänge gesamt: 3", text)
        self.assertIn("selection -> properties", text)
        self.assertIn("selection -> overlay", text)
        self.assertIn("selection -> layers_selection", text)


if __name__ == "__main__":
    unittest.main()
