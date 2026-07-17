from __future__ import annotations

import unittest
from unittest.mock import patch

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


class TemplateRefreshHotspotAnalyzerTests(unittest.TestCase):
    def test_hotspot_analysis_is_empty_when_profiling_is_disabled(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.canvas()

        analysis = manager.refresh_hotspot_analysis()

        self.assertFalse(analysis["enabled"])
        self.assertEqual(analysis["total_count"], 0)
        self.assertEqual(analysis["total_seconds"], 0)
        self.assertEqual(analysis["gateway_count"], 0)
        self.assertEqual(analysis["gateways"], [])

    def test_hotspot_analysis_aggregates_all_gateway_metrics(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)

        manager.canvas()
        manager.canvas()
        manager.overlay()

        analysis = manager.refresh_hotspot_analysis()

        self.assertEqual(analysis["total_count"], 3)
        self.assertEqual(analysis["gateway_count"], 2)
        self.assertEqual(
            {gateway["name"] for gateway in analysis["gateways"]},
            {"canvas", "overlay"},
        )
        by_name = {
            gateway["name"]: gateway for gateway in analysis["gateways"]
        }
        self.assertEqual(by_name["canvas"]["count"], 2)
        self.assertEqual(by_name["overlay"]["count"], 1)
        self.assertAlmostEqual(
            sum(gateway["count_share"] for gateway in analysis["gateways"]),
            1.0,
        )
        self.assertAlmostEqual(
            sum(gateway["time_share"] for gateway in analysis["gateways"]),
            1.0,
        )

    def test_rankings_use_stable_documented_order(self):
        profiler = TemplateRefreshProfiler(enabled=True)
        timings = iter(
            [
                0.0, 0.004,  # slow: 4 ms
                1.0, 1.001,  # fast: 1 ms
                2.0, 2.001,  # fast: 1 ms
            ]
        )
        with patch(
            "vadafok_studio.template_editor.refresh_profiler.perf_counter",
            side_effect=lambda: next(timings),
        ):
            profiler.run("slow", lambda: None)
            profiler.run("fast", lambda: None)
            profiler.run("fast", lambda: None)

        analysis = profiler.hotspot_analysis_snapshot()

        self.assertEqual(
            [item["name"] for item in analysis["rankings"]["by_total_time"]],
            ["slow", "fast"],
        )
        self.assertEqual(
            [item["name"] for item in analysis["rankings"]["by_count"]],
            ["fast", "slow"],
        )
        self.assertEqual(
            [item["name"] for item in analysis["rankings"]["by_average_time"]],
            ["slow", "fast"],
        )
        self.assertEqual(
            [item["name"] for item in analysis["rankings"]["by_maximum_time"]],
            ["slow", "fast"],
        )

    def test_nested_selection_metrics_are_reported_without_behavior_change(self):
        app = _FakeApp()
        manager = TemplateRefreshManager(app)
        manager.set_profiling(True)

        manager.selection()

        analysis = manager.refresh_hotspot_analysis()
        self.assertEqual(analysis["total_count"], 4)
        self.assertEqual(
            {gateway["name"] for gateway in analysis["gateways"]},
            {"selection", "properties", "overlay", "layers_selection"},
        )
        self.assertEqual(
            app.calls,
            [
                ("load_properties",),
                ("build_properties",),
                (
                    "overlay",
                    {
                        "bg_info": None,
                        "refresh_layers": False,
                        "refresh_status": True,
                    },
                ),
                ("layers_selection",),
            ],
        )

    def test_hotspot_snapshot_is_detached(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()

        first = manager.refresh_hotspot_analysis()
        first["gateways"][0]["count"] = 999
        first["rankings"]["by_count"][0]["name"] = "changed"

        second = manager.refresh_hotspot_analysis()
        self.assertEqual(second["gateways"][0]["count"], 1)
        self.assertEqual(
            second["rankings"]["by_count"][0]["name"],
            "canvas",
        )

    def test_disabling_keeps_existing_hotspot_metrics_readable(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()
        manager.set_profiling(False)

        analysis = manager.refresh_hotspot_analysis()

        self.assertFalse(analysis["enabled"])
        self.assertEqual(analysis["total_count"], 1)

    def test_reset_profile_clears_hotspot_metrics_without_disabling(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()

        manager.reset_profile()

        analysis = manager.refresh_hotspot_analysis()
        self.assertTrue(analysis["enabled"])
        self.assertEqual(analysis["gateways"], [])

    def test_hotspot_text_contains_rankings_and_summary(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()
        manager.overlay()

        text = manager.refresh_hotspot_text()

        self.assertIn("=== Refresh Hotspot Analysis ===", text)
        self.assertIn("Ranking nach Gesamtzeit:", text)
        self.assertIn("canvas", text)
        self.assertIn("overlay", text)
        self.assertIn("Häufigster Gateway:", text)
        self.assertIn("Höchster Durchschnitt:", text)
        self.assertIn("Höchster Einzelwert:", text)


if __name__ == "__main__":
    unittest.main()
