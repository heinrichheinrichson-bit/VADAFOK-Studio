from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import tkinter
import unittest

from vadafok_studio import logging_setup


class LoggingSetupTests(unittest.TestCase):
    def test_log_directory_and_file_exist(self) -> None:
        self.assertTrue(logging_setup.LOG_DIR.is_dir())
        self.assertTrue(logging_setup.LOG_FILE.is_file())

    def test_rotating_file_handler_is_configured(self) -> None:
        handlers = [
            handler
            for handler in logging_setup.LOGGER.handlers
            if isinstance(handler, RotatingFileHandler)
        ]
        self.assertEqual(len(handlers), 1)
        self.assertEqual(handlers[0].maxBytes, 2 * 1024 * 1024)
        self.assertEqual(handlers[0].backupCount, 3)

    def test_child_logger_uses_central_namespace(self) -> None:
        child = logging_setup.get_logger("tests")
        self.assertEqual(child.name, "vadafok_studio.tests")

    def test_global_exception_hooks_are_installed(self) -> None:
        self.assertIs(logging_setup.sys.excepthook, logging_setup._sys_exception_hook)
        self.assertTrue(
            getattr(
                tkinter.Tk.report_callback_exception,
                "_vadafok_logging_installed",
                False,
            )
        )

    def test_test_message_can_be_written(self) -> None:
        logging_setup.LOGGER.info("Basic test suite logging check")
        for handler in logging_setup.LOGGER.handlers:
            handler.flush()
        content = logging_setup.LOG_FILE.read_text(encoding="utf-8")
        self.assertIn("Basic test suite logging check", content)


if __name__ == "__main__":
    unittest.main()
