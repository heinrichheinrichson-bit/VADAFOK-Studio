from __future__ import annotations

import unittest

from vadafok_studio.version import (
    APP_TITLE,
    APP_USER_MODEL_ID,
    PRODUCT_NAME,
    SIDEBAR_VERSION,
    VERSION,
    version_info,
)


class VersionTests(unittest.TestCase):
    def test_current_version(self) -> None:
        self.assertEqual(VERSION, "2.22.4")

    def test_derived_version_values(self) -> None:
        self.assertEqual(PRODUCT_NAME, "VADAFOK Studio")
        self.assertEqual(APP_TITLE, f"{PRODUCT_NAME} {VERSION}")
        self.assertEqual(SIDEBAR_VERSION, f"Studio {VERSION}")
        self.assertEqual(APP_USER_MODEL_ID, f"VADAFOK.Studio.{VERSION}")

    def test_version_info_matches_constants(self) -> None:
        self.assertEqual(
            version_info(),
            {
                "product_name": PRODUCT_NAME,
                "version": VERSION,
                "app_title": APP_TITLE,
                "sidebar_version": SIDEBAR_VERSION,
                "app_user_model_id": APP_USER_MODEL_ID,
            },
        )


if __name__ == "__main__":
    unittest.main()
