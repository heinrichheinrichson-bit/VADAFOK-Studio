"""Single source of truth for VADAFOK Studio version information."""

from __future__ import annotations

PRODUCT_NAME = "VADAFOK Studio"
VERSION = "2.23.3"

APP_TITLE = f"{PRODUCT_NAME} {VERSION}"
SIDEBAR_VERSION = f"Studio {VERSION}"
APP_USER_MODEL_ID = f"VADAFOK.Studio.{VERSION}"


def version_info() -> dict[str, str]:
    """Return all central runtime version values."""
    return {
        "product_name": PRODUCT_NAME,
        "version": VERSION,
        "app_title": APP_TITLE,
        "sidebar_version": SIDEBAR_VERSION,
        "app_user_model_id": APP_USER_MODEL_ID,
    }


__all__ = [
    "PRODUCT_NAME",
    "VERSION",
    "APP_TITLE",
    "SIDEBAR_VERSION",
    "APP_USER_MODEL_ID",
    "version_info",
]
