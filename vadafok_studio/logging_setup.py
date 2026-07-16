"""Central logging setup for VADAFOK Studio."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
import os
import platform
import sys
import threading
from pathlib import Path
from types import TracebackType
from typing import Any

from .version import APP_TITLE, VERSION

LOGGER_NAME = "vadafok_studio"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "vadafok_studio.log"

_MAX_LOG_BYTES = 2 * 1024 * 1024
_BACKUP_COUNT = 3
_CONFIGURED = False
_ORIGINAL_SYS_EXCEPTHOOK = sys.excepthook
_ORIGINAL_THREADING_EXCEPTHOOK = getattr(threading, "excepthook", None)


def _formatter() -> logging.Formatter:
    return logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def setup_logging() -> logging.Logger:
    """Configure and return the shared application logger."""
    global _CONFIGURED

    logger = logging.getLogger(LOGGER_NAME)
    if _CONFIGURED:
        return logger

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=_MAX_LOG_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_formatter())
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(_formatter())
    logger.addHandler(console_handler)

    _CONFIGURED = True
    return logger


LOGGER = setup_logging()


def log_application_start() -> None:
    """Write one compact startup block."""
    LOGGER.info("=" * 72)
    LOGGER.info("Application start: %s", APP_TITLE)
    LOGGER.info("Version: %s", VERSION)
    LOGGER.info("Python: %s", sys.version.replace("\n", " "))
    LOGGER.info("Platform: %s", platform.platform())
    LOGGER.info("Executable: %s", sys.executable)
    LOGGER.info("Working directory: %s", Path.cwd())
    LOGGER.info("Process ID: %s", os.getpid())
    LOGGER.info("Log file: %s", LOG_FILE)


def _sys_exception_hook(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    if issubclass(exc_type, KeyboardInterrupt):
        _ORIGINAL_SYS_EXCEPTHOOK(exc_type, exc_value, exc_traceback)
        return

    LOGGER.critical(
        "Unhandled exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )


def _thread_exception_hook(args: Any) -> None:
    LOGGER.critical(
        "Unhandled thread exception in %s",
        getattr(args.thread, "name", "unknown thread"),
        exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
    )


def _install_tk_callback_hook() -> None:
    """Log uncaught Tk callback exceptions globally without changing UI flows."""
    try:
        import tkinter

        if getattr(
            tkinter.Misc.report_callback_exception,
            "_vadafok_logging_installed",
            False,
        ):
            return

        original = tkinter.Misc.report_callback_exception

        def report_callback_exception(
            self: Any,
            exc_type: type[BaseException],
            exc_value: BaseException,
            exc_traceback: TracebackType | None,
        ) -> None:
            LOGGER.error(
                "Unhandled Tk callback exception",
                exc_info=(exc_type, exc_value, exc_traceback),
            )
            try:
                original(self, exc_type, exc_value, exc_traceback)
            except Exception:
                LOGGER.exception("Original Tk exception handler failed")

        report_callback_exception._vadafok_logging_installed = True
        tkinter.Misc.report_callback_exception = report_callback_exception
    except Exception:
        LOGGER.exception("Tk callback logging hook could not be installed")


def install_global_exception_hooks() -> None:
    """Install handlers for uncaught main-thread, worker-thread and Tk errors."""
    sys.excepthook = _sys_exception_hook

    if _ORIGINAL_THREADING_EXCEPTHOOK is not None:
        threading.excepthook = _thread_exception_hook

    _install_tk_callback_hook()


def get_logger(component: str | None = None) -> logging.Logger:
    """Return the shared logger or a named child logger."""
    if not component:
        return LOGGER
    return LOGGER.getChild(component)


log_application_start()
install_global_exception_hooks()


__all__ = [
    "LOGGER",
    "LOG_DIR",
    "LOG_FILE",
    "get_logger",
    "install_global_exception_hooks",
    "log_application_start",
    "setup_logging",
]
