from __future__ import annotations

import py_compile
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ProjectFoundationTests(unittest.TestCase):
    def test_app_uses_central_version_values(self) -> None:
        app_text = (
            PROJECT_ROOT / "vadafok_studio" / "app.py"
        ).read_text(encoding="utf-8")

        self.assertIn("APP_TITLE", app_text)
        self.assertIn("APP_USER_MODEL_ID", app_text)
        self.assertIn("SIDEBAR_VERSION", app_text)
        self.assertNotIn("2.16.5.1", app_text)

    def test_app_uses_central_logger(self) -> None:
        app_text = (
            PROJECT_ROOT / "vadafok_studio" / "app.py"
        ).read_text(encoding="utf-8")

        self.assertIn("from .logging_setup import LOGGER", app_text)
        self.assertIn('LOGGER.info("app.py loaded successfully")', app_text)

    def test_gitignore_has_required_runtime_entries(self) -> None:
        gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
        lines = {
            line.strip()
            for line in gitignore.splitlines()
            if line.strip() and not line.strip().startswith("#")
        }

        for required in (".idea/", "__pycache__/", "*.pyc", "logs/", "*.bak"):
            self.assertIn(required, lines)

        self.assertNotIn(r"\n", gitignore)

    def test_core_python_files_compile(self) -> None:
        files = [
            PROJECT_ROOT / "vadafok_studio" / "version.py",
            PROJECT_ROOT / "vadafok_studio" / "logging_setup.py",
            PROJECT_ROOT / "vadafok_studio" / "app.py",
        ]
        for path in files:
            py_compile.compile(str(path), doraise=True)


if __name__ == "__main__":
    unittest.main()
