from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vadafok_studio.core.sync_profiler import SyncProfiler


class SyncProfilerTests(unittest.TestCase):
    def test_disabled_profiler_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sync.log"
            profiler = SyncProfiler(enabled=False, log_path=path)
            self.assertIsNone(profiler.mark("ignored"))
            self.assertFalse(profiler.save())
            self.assertFalse(path.exists())

    def test_enabled_profiler_writes_named_marks_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sync.log"
            profiler = SyncProfiler(enabled=True, session_name="Test SHOW", log_path=path)
            profiler.mark("Event")
            profiler.mark("OBS request")
            self.assertTrue(profiler.save())
            self.assertFalse(profiler.save())
            content = path.read_text(encoding="utf-8")
            self.assertIn("Test SHOW", content)
            self.assertIn("Event", content)
            self.assertIn("OBS request", content)

    def test_clear_starts_a_new_collecting_session(self) -> None:
        profiler = SyncProfiler(enabled=True)
        profiler.mark("old")
        profiler.clear()
        profiler.mark("new")
        names = [name for _, name in profiler.marks]
        self.assertEqual(names, ["new"])


if __name__ == "__main__":
    unittest.main()
