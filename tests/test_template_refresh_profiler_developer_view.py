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


class TemplateRefreshProfilerDeveloperViewTests(unittest.TestCase):
    def test_developer_view_is_empty_and_disabled_by_default(self):
        manager = TemplateRefreshManager(_FakeApp())

        self.assertEqual(
            manager.refresh_developer_view(),
            {
                "enabled": False,
                "total_count": 0,
                "total_seconds": 0,
                "average_seconds": 0.0,
                "maximum_seconds": 0.0,
                "metrics": {},
            },
        )

    def test_developer_view_summarizes_all_gateway_calls(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)

        manager.canvas()
        manager.overlay(refresh_layers=False)
        manager.layers(full=False)

        view = manager.refresh_developer_view()
        self.assertTrue(view["enabled"])
        self.assertEqual(view["total_count"], 3)
        self.assertEqual(
            set(view["metrics"]),
            {"canvas", "layers_selection", "overlay"},
        )
        self.assertGreaterEqual(view["total_seconds"], 0.0)
        self.assertGreaterEqual(view["average_seconds"], 0.0)
        self.assertGreaterEqual(view["maximum_seconds"], 0.0)

    def test_developer_text_has_stable_status_and_metric_names(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()

        text = manager.refresh_developer_text()

        self.assertIn("RefreshProfiler: AKTIV", text)
        self.assertIn("Gesamt: 1 Refreshes", text)
        self.assertIn("canvas: 1", text)
        self.assertIn("Durchschnitt:", text)
        self.assertIn("Maximum:", text)

    def test_reset_updates_developer_view_without_disabling(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()
        manager.reset_profile()

        view = manager.refresh_developer_view()
        self.assertTrue(view["enabled"])
        self.assertEqual(view["total_count"], 0)
        self.assertEqual(view["metrics"], {})

    def test_disabling_keeps_existing_measurements_readable(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()
        manager.set_profiling(False)

        view = manager.refresh_developer_view()
        self.assertFalse(view["enabled"])
        self.assertEqual(view["total_count"], 1)

    def test_developer_snapshot_is_detached(self):
        profiler = TemplateRefreshProfiler(enabled=True)
        profiler.run("canvas", lambda: None)

        first = profiler.developer_snapshot()
        first["metrics"]["canvas"]["count"] = 999

        second = profiler.developer_snapshot()
        self.assertEqual(second["metrics"]["canvas"]["count"], 1)


if __name__ == "__main__":
    unittest.main()
